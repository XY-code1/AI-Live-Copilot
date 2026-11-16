from uuid import uuid4

import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app


def _pdf_bytes(text: str = "Chuanxi 5-Day Tour\nDays: 5 Nights: 4") -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    payload = document.tobytes()
    document.close()
    return payload


def _client():
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
    client = TestClient(app)
    return client


def test_upload_pdf_extracts_text():
    client = _client()
    created = client.post(
        "/api/v1/products", json={"name": "川西五日游", "category": "旅游线路"}
    ).json()

    response = client.post(
        f"/api/v1/products/{created['id']}/sources",
        files={"file": ("行程单.pdf", _pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 201, response.text
    source = response.json()
    assert source["status"] == "ready"
    assert source["page_count"] == 1
    assert source["type"] == "pdf"

    text_response = client.get(f"/api/v1/sources/{source['id']}")
    assert text_response.status_code == 200
    assert "Chuanxi 5-Day Tour" in text_response.json()["text"]


def test_upload_to_missing_product_returns_404():
    client = _client()
    missing = uuid4()
    response = client.post(
        f"/api/v1/products/{missing}/sources",
        files={"file": ("行程单.pdf", _pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 404


def test_read_missing_source_returns_404():
    client = _client()
    response = client.get(f"/api/v1/sources/{uuid4()}")
    assert response.status_code == 404
