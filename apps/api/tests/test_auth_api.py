from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


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


def test_register_login_me(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "password")
    client = _client()

    registered = client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123", "name": "甲"},
    )
    assert registered.status_code == 201, registered.text
    token = registered.json()["token"]
    assert registered.json()["user"]["email"] == "a@example.com"

    logged_in = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert logged_in.status_code == 200
    assert logged_in.json()["token"]

    me = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "a@example.com"


def test_duplicate_email_rejected(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "password")
    client = _client()
    payload = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_wrong_password_rejected(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "password")
    client = _client()
    client.post(
        "/api/v1/auth/register", json={"email": "b@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "b@example.com", "password": "wrong-pass"}
    )
    assert response.status_code == 401


def test_me_requires_token(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "password")
    client = _client()
    assert client.get("/api/v1/auth/me").status_code == 401
