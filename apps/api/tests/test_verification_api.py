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
        {"kind": "risk", "title": "风险提示", "content": "下单前请咨询客服。"},
    ]
}

AI_ISSUE = {
    "issues": [
        {
            "section_index": 0,
            "type": "exaggeration",
            "severity": "high",
            "message": "开场使用了夸大表述",
            "quote": "大家好",
            "suggestion": "改为客观描述",
        }
    ],
    "summary": "发现 1 处夸大表述。",
}

AI_CLEAN = {"issues": [], "summary": "未发现问题。"}


class FakeProvider:
    def __init__(self, payload):
        self.payload = payload

    async def complete(self, messages, *, response_format=None):
        return json.dumps(self.payload)


def _client(monkeypatch, verification_payload, generation_payload=None) -> TestClient:
    monkeypatch.setattr(
        "app.services.script_generation.get_provider",
        lambda: FakeProvider(generation_payload or GENERATED),
    )
    monkeypatch.setattr(
        "app.services.verification.get_provider",
        lambda: FakeProvider(verification_payload),
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


def _script(client: TestClient) -> str:
    product = client.post("/api/v1/products", json={"name": "川西五日游"}).json()
    script = client.post(
        f"/api/v1/products/{product['id']}/scripts/generate", json={}
    ).json()
    return script["id"]


def test_rule_detects_absolute_wording(monkeypatch):
    client = _client(monkeypatch, AI_CLEAN)
    script_id = _script(client)
    saved = client.post(
        f"/api/v1/scripts/{script_id}/versions",
        json={
            "sections": [
                {"kind": "opening", "title": "开场", "content": "全网最低价的川西五日游！"},
                {"kind": "risk", "title": "风险提示", "content": "下单前请咨询。"},
            ]
        },
    ).json()
    script_id = saved["id"]

    response = client.post(f"/api/v1/scripts/{script_id}/verify")
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "issue"
    rule_issue = next(item for item in body["issues"] if item["origin"] == "rule")
    assert rule_issue["type"] == "absolute_wording"
    assert rule_issue["severity"] == "high"
    assert "全网最低" in rule_issue["quote"]


def test_ai_issue_sets_status(monkeypatch):
    client = _client(monkeypatch, AI_ISSUE)
    script_id = _script(client)
    body = client.post(f"/api/v1/scripts/{script_id}/verify").json()
    assert body["status"] == "issue"
    assert body["issues"][0]["origin"] == "ai"
    assert body["issues"][0]["type"] == "exaggeration"


def test_clean_script_passes(monkeypatch):
    client = _client(monkeypatch, AI_CLEAN)
    script_id = _script(client)
    body = client.post(f"/api/v1/scripts/{script_id}/verify").json()
    assert body["status"] == "pass"
    assert body["issues"] == []


def test_list_verifications(monkeypatch):
    client = _client(monkeypatch, AI_CLEAN)
    script_id = _script(client)
    client.post(f"/api/v1/scripts/{script_id}/verify")
    client.post(f"/api/v1/scripts/{script_id}/verify")
    listing = client.get(f"/api/v1/scripts/{script_id}/verifications")
    assert listing.status_code == 200
    assert len(listing.json()) == 2


def test_ai_failure_marks_unverified(monkeypatch):
    class FailingProvider:
        async def complete(self, messages, *, response_format=None):
            raise RuntimeError("timeout")

    client = _client(monkeypatch, FailingProvider())
    script_id = _script(client)
    body = client.post(f"/api/v1/scripts/{script_id}/verify").json()
    assert body["status"] == "unverified"
    assert "未完成" in body["summary"]


def test_status_persisted_as_pass_value(monkeypatch):
    client = _client(monkeypatch, AI_CLEAN)
    script_id = _script(client)
    body = client.post(f"/api/v1/scripts/{script_id}/verify").json()
    assert body["status"] == "pass"
    # API and script status agree and use the public value, not the member name.
    script = client.get(f"/api/v1/scripts/{script_id}").json()
    assert script["verification_status"] == "pass"


def test_rule_hit_overrides_clean_ai_summary(monkeypatch):
    client = _client(monkeypatch, AI_CLEAN)
    script_id = _script(client)
    saved = client.post(
        f"/api/v1/scripts/{script_id}/versions",
        json={
            "sections": [
                {"kind": "opening", "title": "开场", "content": "全网最低价！"},
                {"kind": "risk", "title": "风险提示", "content": "下单前请咨询。"},
            ]
        },
    ).json()
    body = client.post(f"/api/v1/scripts/{saved['id']}/verify").json()
    assert body["status"] == "issue"
    assert "规则命中" in body["summary"]


def test_issue_without_matching_quote_has_no_section(monkeypatch):
    payload = {
        "issues": [
            {
                "section_index": 0,
                "type": "exaggeration",
                "severity": "medium",
                "message": "与段落无关的引文",
                "quote": "根本不在这段里",
            }
        ],
        "summary": "测试。",
    }
    client = _client(monkeypatch, payload)
    script_id = _script(client)
    body = client.post(f"/api/v1/scripts/{script_id}/verify").json()
    assert body["issues"][0]["section_id"] is None
