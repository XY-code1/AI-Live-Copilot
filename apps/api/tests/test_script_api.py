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
    "sections": [
        {"kind": "opening", "title": "开场", "content": "大家好，今天带来川西五日游。"},
        {"kind": "selling_points", "title": "核心卖点", "content": "小团 12 人以内，含门票住宿。"},
        {"kind": "risk", "title": "风险提示", "content": "购物安排尚未确认，下单前请咨询。"},
    ]
}


class FakeProvider:
    def __init__(self, payload=None):
        self.payload = payload or GENERATED

    async def complete(self, messages, *, response_format=None):
        return json.dumps(self.payload)


def _client(monkeypatch, payload=None) -> TestClient:
    monkeypatch.setattr(
        "app.services.script_generation.get_provider",
        lambda: FakeProvider(payload),
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


def test_generate_script(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "川西五日游"}).json()
    client.post(
        f"/api/v1/products/{product['id']}/attributes",
        json={"label": "出行天数", "value": "5 天 4 晚", "status": "confirmed"},
    )

    response = client.post(
        f"/api/v1/products/{product['id']}/scripts/generate",
        json={"scenario": "日常带货", "audience": "白领", "style": "亲切自然"},
    )
    assert response.status_code == 201, response.text
    script = response.json()
    assert script["version"] == 1
    assert [section["kind"] for section in script["sections"]] == [
        "opening",
        "selling_points",
        "risk",
    ]
    assert all(section["origin"] == "ai" for section in script["sections"])


def test_save_version_increments(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "川西五日游"}).json()
    script = client.post(f"/api/v1/products/{product['id']}/scripts/generate", json={}).json()

    new_version = client.post(
        f"/api/v1/scripts/{script['id']}/versions",
        json={
            "sections": [
                {"kind": "opening", "title": "开场", "content": "改过的开场"},
            ]
        },
    )
    assert new_version.status_code == 201, new_version.text
    assert new_version.json()["version"] == 2
    assert new_version.json()["sections"][0]["content"] == "改过的开场"

    versions = client.get(f"/api/v1/scripts/{script['id']}/versions")
    assert versions.status_code == 200
    assert len(versions.json()) == 2


def test_delete_script(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "川西五日游"}).json()
    script = client.post(f"/api/v1/products/{product['id']}/scripts/generate", json={}).json()
    assert client.delete(f"/api/v1/scripts/{script['id']}").status_code == 204
    assert client.get(f"/api/v1/scripts/{script['id']}").status_code == 404
