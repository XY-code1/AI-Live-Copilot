import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_product(client: TestClient, name: str = "川西五日游") -> dict:
    response = client.post(
        "/api/v1/products",
        json={
            "name": name,
            "category": "旅游线路",
            "summary": "成都出发，小团出行。",
            "price": 3280,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_get_product(client: TestClient):
    created = _create_product(client)
    assert created["name"] == "川西五日游"
    assert created["status"] == "draft"
    assert created["price"] == 3280

    response = client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_list_and_search(client: TestClient):
    _create_product(client, name="川西五日游")
    _create_product(client, name="云南大理丽江 6 日游")

    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert len(response.json()) == 2

    filtered = client.get("/api/v1/products", params={"q": "川西"})
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["name"] == "川西五日游"


def test_update_product(client: TestClient):
    created = _create_product(client)
    response = client.patch(
        f"/api/v1/products/{created['id']}",
        json={"price": 2999, "status": "ready"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 2999
    assert body["status"] == "ready"


def test_delete_product(client: TestClient):
    created = _create_product(client)
    response = client.delete(f"/api/v1/products/{created['id']}")
    assert response.status_code == 204

    missing = client.get(f"/api/v1/products/{created['id']}")
    assert missing.status_code == 404


def test_get_missing_product_returns_404(client: TestClient):
    response = client.get("/api/v1/products/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
