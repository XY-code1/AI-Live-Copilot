import hashlib

import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app


def _pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Chuanxi 5-Day Tour, fee included")
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
    return client.post(
        "/api/v1/products", json={"name": "川西五日游"}
    ).json()["id"]


def test_pdf_upload_records_run():
    client = _client()
    product_id = _product(client)
    payload = _pdf_bytes()
    response = client.post(
        f"/api/v1/products/{product_id}/sources",
        files={"file": ("行程单.pdf", payload, "application/pdf")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["content_hash"] == hashlib.sha256(payload).hexdigest()
    assert body["parser"].startswith("pymupdf")

    runs = client.get(f"/api/v1/products/{product_id}/ingestion-runs")
    assert runs.status_code == 200
    assert len(runs.json()) == 1
    run = runs.json()[0]
    assert run["status"] == "done"
    assert run["type"] == "pdf"
    assert run["snapshot_path"]
    assert run["content_hash"] == body["content_hash"]


def test_failed_upload_records_failed_run():
    client = _client()
    product_id = _product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/sources",
        files={"file": ("bad.pdf", b"not a pdf", "application/pdf")},
    )
    assert response.status_code == 400
    runs = client.get(f"/api/v1/products/{product_id}/ingestion-runs").json()
    assert runs[0]["status"] == "failed"
    assert runs[0]["error"]


def test_url_source_records_evidence(monkeypatch):
    client = _client()
    product_id = _product(client)

    def fake_page(url):
        return ("标题", "正文", "https://example.com/final", ["https://example.com/a"], "<html>hi</html>")

    monkeypatch.setattr("app.api.sources.fetch_url_page", fake_page)
    response = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/a"},
    )
    assert response.status_code == 201, response.text
    run = client.get(f"/api/v1/products/{product_id}/ingestion-runs").json()[0]
    assert run["status"] == "done"
    assert run["final_url"] == "https://example.com/final"
    assert run["redirect_chain"] == ["https://example.com/a"]
    assert run["snapshot_path"]
