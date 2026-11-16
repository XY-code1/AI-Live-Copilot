import json

import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

EXTRACTED = {
    "attributes": [
        {"label": "出行天数", "value": "5 天 4 晚", "status": "confirmed"},
        {"label": "购物安排", "value": "待确认", "status": "unconfirmed"},
    ]
}


class FakeProvider:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    async def complete(self, messages, *, response_format=None) -> str:
        assert response_format == {"type": "json_object"}
        return json.dumps(self.payload)


def _pdf_bytes(text: str = "Chuanxi 5-Day Tour\nDays: 5 Nights: 4") -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    payload = document.tobytes()
    document.close()
    return payload


def _client(monkeypatch, provider_payload: dict | None = None) -> TestClient:
    monkeypatch.setattr(
        "app.services.extraction.get_provider",
        lambda: FakeProvider(provider_payload or EXTRACTED),
    )
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


def _create_product_with_pdf(client: TestClient) -> str:
    product = client.post(
        "/api/v1/products", json={"name": "川西五日游", "category": "旅游线路"}
    ).json()
    uploaded = client.post(
        f"/api/v1/products/{product['id']}/sources",
        files={"file": ("行程单.pdf", _pdf_bytes(), "application/pdf")},
    )
    assert uploaded.status_code == 201
    return product["id"]


def test_extract_creates_ai_attributes(monkeypatch):
    client = _client(monkeypatch)
    product_id = _create_product_with_pdf(client)

    response = client.post(f"/api/v1/products/{product_id}/extract")
    assert response.status_code == 200, response.text
    attributes = response.json()["attributes"]
    assert len(attributes) == 2
    days = next(item for item in attributes if item["label"] == "出行天数")
    assert days["status"] == "confirmed"
    assert days["origin"] == "ai"
    assert days["source_id"] is not None


def test_extract_replaces_previous_ai_attributes(monkeypatch):
    client = _client(monkeypatch)
    product_id = _create_product_with_pdf(client)
    first = client.post(f"/api/v1/products/{product_id}/extract").json()
    assert {item["label"] for item in first["attributes"]} == {"出行天数", "购物安排"}

    replacement = {"attributes": [{"label": "住宿标准", "value": "四钻", "status": "confirmed"}]}
    monkeypatch.setattr(
        "app.services.extraction.get_provider",
        lambda: FakeProvider(replacement),
    )
    second = client.post(f"/api/v1/products/{product_id}/extract").json()
    assert {item["label"] for item in second["attributes"]} == {"住宿标准"}


def test_extract_without_text_returns_400(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "空商品"}).json()
    response = client.post(f"/api/v1/products/{product['id']}/extract")
    assert response.status_code == 400
