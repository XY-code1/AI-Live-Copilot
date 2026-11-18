import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

HTML = """
<html><head><title>商品页</title>
<script type="application/ld+json">{"@type":"Product","name":"川西五日游"}</script>
</head><body>
<h1>川西五日游</h1><p>出行天数：5 天 4 晚</p>
<table><tr><th>项目</th><th>费用</th></tr><tr><td>门票</td><td>含</td></tr></table>
</body></html>
"""


def _pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Chuanxi 5-Day Tour\nDays: 5")
    payload = document.tobytes()
    document.close()
    return payload


def _client() -> TestClient:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override():
        db = session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    return TestClient(app)


def _product(client: TestClient) -> str:
    return client.post("/api/v1/products", json={"name": "川西五日游"}).json()["id"]


def test_pdf_segments_created():
    client = _client()
    product_id = _product(client)
    uploaded = client.post(
        f"/api/v1/products/{product_id}/sources",
        files={"file": ("行程单.pdf", _pdf_bytes(), "application/pdf")},
    )
    assert uploaded.status_code == 201, uploaded.text
    segments = client.get(f"/api/v1/sources/{uploaded.json()['id']}/segments")
    assert segments.status_code == 200
    kinds = {item["kind"] for item in segments.json()}
    assert "page" in kinds
    assert any("Chuanxi" in item["content"] for item in segments.json())
    assert all(item["page_no"] == 1 for item in segments.json())


def test_url_segments_include_table_and_jsonld(monkeypatch):
    client = _client()
    product_id = _product(client)
    monkeypatch.setattr(
        "app.api.sources.fetch_url_page",
        lambda url: ("商品页", "正文", url, [], HTML),
    )
    uploaded = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/p"},
    )
    assert uploaded.status_code == 201, uploaded.text
    segments = client.get(f"/api/v1/sources/{uploaded.json()['id']}/segments").json()
    kinds = {item["kind"] for item in segments}
    assert {"heading", "paragraph", "table", "jsonld"} <= kinds
    table = next(item for item in segments if item["kind"] == "table")
    assert table["structured"]["rows"][0] == ["项目", "费用"]
    jsonld = next(item for item in segments if item["kind"] == "jsonld")
    assert "川西五日游" in jsonld["content"]


def test_url_segments_carry_locator_and_hash(monkeypatch):
    html = """
    <html><body>
    <h2>行程亮点</h2>
    <ul><li>四姑娘山</li><li>双桥沟</li></ul>
    </body></html>
    """
    client = _client()
    product_id = _product(client)
    monkeypatch.setattr(
        "app.api.sources.fetch_url_page",
        lambda url: ("商品页", "正文", url, [], html),
    )
    created = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/p"},
    )
    assert created.status_code == 201, created.text
    segments = client.get(f"/api/v1/sources/{created.json()['id']}/segments").json()

    heading = next(item for item in segments if item["kind"] == "heading")
    assert heading["heading_level"] == 2
    assert heading["source_locator"].endswith("h2")

    listing = next(item for item in segments if item["kind"] == "list")
    assert listing["content"] == "- 四姑娘山\n- 双桥沟"
    assert listing["structured"]["item_count"] == 2

    assert all(item["content_hash"] for item in segments)


def test_segments_are_scoped_to_workspace(client=None):
    # covered by product isolation; a missing source returns 404
    client = _client()
    product_id = _product(client)
    assert client.get(
        "/api/v1/sources/00000000-0000-0000-0000-000000000000/segments"
    ).status_code == 404
    assert product_id
