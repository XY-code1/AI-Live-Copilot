import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.sufficiency import assess


def test_assess_rules():
    assert assess("").sufficiency == "insufficient"
    assert assess("x" * 500).sufficiency == "sufficient"
    assert assess("请登录后查看商品价格").sufficiency == "restricted"
    assert assess("太短", is_url=True).sufficiency == "insufficient"


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


def test_html_snapshot_upload():
    client = _client()
    product_id = _product(client)
    html = "<html><body>" + ("川西五日游行程很丰富，费用包含门票住宿。" * 10) + "</body></html>"
    response = client.post(
        f"/api/v1/products/{product_id}/sources",
        files={"file": ("page.html", html.encode("utf-8"), "text/html")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["type"] == "url"
    assert body["parser"] == "snapshot"
    assert body["sufficiency"] == "sufficient"


def test_short_pdf_marked_insufficient():
    client = _client()
    product_id = _product(client)
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "short")
    payload = document.tobytes()
    document.close()
    response = client.post(
        f"/api/v1/products/{product_id}/sources",
        files={"file": ("s.pdf", payload, "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["sufficiency"] == "insufficient"


def test_restricted_url_marked(monkeypatch):
    client = _client()
    product_id = _product(client)
    monkeypatch.setattr(
        "app.api.sources.fetch_url_page",
        lambda url: ("登录", "请登录后查看商品", url, [], "<html></html>"),
    )
    response = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/login"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["sufficiency"] == "restricted"
