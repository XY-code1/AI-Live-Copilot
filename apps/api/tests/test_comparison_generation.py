import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

GENERATED = {
    "differences": [
        {
            "field": "价格",
            "ours": "¥3280",
            "theirs": "¥3580",
            "evidence_type": "source",
            "side": "ours",
            "note": "",
        }
    ],
    "missing_info": ["购物安排"],
}


class FakeProvider:
    def __init__(self, payload=None):
        self.payload = payload or GENERATED

    async def complete(self, messages, *, response_format=None):
        return json.dumps(self.payload)


def _client(monkeypatch, provider_payload=None) -> TestClient:
    monkeypatch.setattr(
        "app.services.comparison_generation.get_provider",
        lambda: FakeProvider(provider_payload),
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


def _setup(client: TestClient) -> str:
    product = client.post(
        "/api/v1/products", json={"name": "川西五日游", "category": "旅游线路"}
    ).json()
    client.post(
        f"/api/v1/products/{product['id']}/attributes",
        json={"label": "出行天数", "value": "5 天 4 晚", "status": "confirmed"},
    )
    competitor = client.post(
        "/api/v1/competitors",
        json={"name": "经典版", "brand": "某社", "material": "价格 ¥3580，5 天 4 晚"},
    ).json()
    comparison = client.post(
        "/api/v1/comparisons",
        json={"product_id": product["id"], "competitor_id": competitor["id"]},
    )
    assert comparison.status_code == 201
    return comparison.json()["id"]


def test_generate_writes_differences_and_missing_info(monkeypatch):
    client = _client(monkeypatch)
    comparison_id = _setup(client)

    response = client.post(f"/api/v1/comparisons/{comparison_id}/generate")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ready"
    assert body["missing_info"] == ["购物安排"]
    assert body["differences"][0]["field"] == "价格"
    assert body["differences"][0]["origin"] == "ai"


def test_generate_replaces_previous_ai_differences(monkeypatch):
    client = _client(monkeypatch)
    comparison_id = _setup(client)
    client.post(f"/api/v1/comparisons/{comparison_id}/generate")

    replacement = {
        "differences": [
            {
                "field": "出行方式",
                "ours": "小团",
                "theirs": "大团",
                "evidence_type": "source",
                "side": "ours",
            }
        ],
        "missing_info": [],
    }
    monkeypatch.setattr(
        "app.services.comparison_generation.get_provider",
        lambda: FakeProvider(replacement),
    )
    body = client.post(f"/api/v1/comparisons/{comparison_id}/generate").json()
    assert {item["field"] for item in body["differences"]} == {"出行方式"}


def test_generate_without_material_returns_400(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "空商品"}).json()
    competitor = client.post("/api/v1/competitors", json={"name": "空竞品"}).json()
    comparison = client.post(
        "/api/v1/comparisons",
        json={"product_id": product["id"], "competitor_id": competitor["id"]},
    ).json()
    response = client.post(f"/api/v1/comparisons/{comparison['id']}/generate")
    assert response.status_code == 400
