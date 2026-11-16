import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

VALID = {
    "sections": [
        {"kind": "opening", "title": "开场", "content": "大家好。"},
        {"kind": "risk", "title": "风险提示", "content": "下单前请咨询。"},
    ]
}


class FakeProvider:
    def __init__(self, payload):
        self.payload = payload

    async def complete(self, messages, *, response_format=None):
        return json.dumps(self.payload)


def _client(monkeypatch, payload=None) -> TestClient:
    monkeypatch.setattr(
        "app.services.script_generation.get_provider",
        lambda: FakeProvider(payload or VALID),
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


def _product(client: TestClient) -> str:
    return client.post("/api/v1/products", json={"name": "川西五日游"}).json()["id"]


def test_delete_removes_whole_series(monkeypatch):
    client = _client(monkeypatch)
    product_id = _product(client)
    script = client.post(
        f"/api/v1/products/{product_id}/scripts/generate", json={}
    ).json()
    client.post(
        f"/api/v1/scripts/{script['id']}/versions",
        json={"sections": [{"kind": "opening", "title": "开场", "content": "改版"}]},
    )
    assert len(client.get(f"/api/v1/scripts/{script['id']}/versions").json()) == 2

    assert client.delete(f"/api/v1/scripts/{script['id']}").status_code == 204
    assert client.get("/api/v1/scripts").json() == []


def test_generate_without_sections_fails(monkeypatch):
    client = _client(monkeypatch, {"sections": []})
    product_id = _product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/scripts/generate", json={}
    )
    assert response.status_code == 502


def test_generate_without_risk_section_fails(monkeypatch):
    client = _client(
        monkeypatch, {"sections": [{"kind": "opening", "title": "开场", "content": "嗨"}]}
    )
    product_id = _product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/scripts/generate", json={}
    )
    assert response.status_code == 502


def test_comparison_must_belong_to_product(monkeypatch):
    client = _client(monkeypatch)
    product_id = _product(client)
    other = _product(client)
    competitor = client.post(
        "/api/v1/competitors", json={"name": "经典版"}
    ).json()
    comparison = client.post(
        "/api/v1/comparisons",
        json={"product_id": other, "competitor_id": competitor["id"]},
    ).json()
    response = client.post(
        f"/api/v1/products/{product_id}/scripts/generate",
        json={"comparison_id": comparison["id"]},
    )
    assert response.status_code == 400


def test_long_directive_rejected(monkeypatch):
    client = _client(monkeypatch)
    product_id = _product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/scripts/generate",
        json={"scenario": "场" * 121},
    )
    assert response.status_code == 422


def test_save_version_keeps_ai_origin_for_unchanged_sections(monkeypatch):
    client = _client(monkeypatch)
    product_id = _product(client)
    script = client.post(
        f"/api/v1/products/{product_id}/scripts/generate", json={}
    ).json()
    saved = client.post(
        f"/api/v1/scripts/{script['id']}/versions",
        json={
            "sections": [
                {
                    "kind": "opening",
                    "title": "开场",
                    "content": script["sections"][0]["content"],
                },
                {
                    "kind": "risk",
                    "title": "风险提示",
                    "content": "改过的风险提示",
                },
            ]
        },
    ).json()
    origins = {section["kind"]: section["origin"] for section in saved["sections"]}
    assert origins["opening"] == "ai"
    assert origins["risk"] == "manual"
