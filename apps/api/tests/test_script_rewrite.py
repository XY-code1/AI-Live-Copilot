import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app

GENERATION = {
    "sections": [
        {"kind": "opening", "title": "开场", "content": "大家好，今天带来川西五日游。"},
        {"kind": "risk", "title": "风险提示", "content": "购物安排尚未确认。"},
    ]
}


class FakeProvider:
    async def complete(self, messages, *, response_format=None):
        return json.dumps({"content": "改写后的开场：大家好，川西五日游来啦！"})


class FakeGenerationProvider:
    async def complete(self, messages, *, response_format=None):
        return json.dumps(GENERATION)


def _client(monkeypatch) -> TestClient:
    monkeypatch.setattr("app.services.script_rewrite.get_provider", lambda: FakeProvider())
    monkeypatch.setattr(
        "app.services.script_generation.get_provider",
        lambda: FakeGenerationProvider(),
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


def test_rewrite_section(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "川西五日游"}).json()
    script = client.post(f"/api/v1/products/{product['id']}/scripts/generate", json={}).json()
    section = script["sections"][0]

    response = client.post(
        f"/api/v1/scripts/{script['id']}/sections/{section['id']}/rewrite",
        json={"instruction": "更活泼一点"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["content"] == "改写后的开场：大家好，川西五日游来啦！"


def test_rewrite_missing_section_returns_404(monkeypatch):
    client = _client(monkeypatch)
    product = client.post("/api/v1/products", json={"name": "川西五日游"}).json()
    script = client.post(f"/api/v1/products/{product['id']}/scripts/generate", json={}).json()
    response = client.post(
        f"/api/v1/scripts/{script['id']}/sections/00000000-0000-0000-0000-000000000000/rewrite",
        json={},
    )
    assert response.status_code == 404
