from io import BytesIO

from app.services.url import _validate_public_url


def test_workspace_isolation(client):
    alice = {"x-dev-user": "alice"}
    bob = {"x-dev-user": "bob"}
    created = client.post(
        "/api/v1/products",
        headers=alice,
        json={"name": "Alice 商品", "category": "旅游线路"},
    )
    assert created.status_code == 201
    product_id = created.json()["id"]
    assert client.get(f"/api/v1/products/{product_id}", headers=bob).status_code == 404
    assert client.get("/api/v1/products", headers=bob).json() == []


def test_url_validator_blocks_private_addresses():
    for url in ("http://127.0.0.1", "http://localhost", "http://169.254.169.254"):
        try:
            _validate_public_url(url)
        except ValueError:
            continue
        raise AssertionError(f"private URL was accepted: {url}")


def test_image_upload_uses_ocr(client, monkeypatch):
    monkeypatch.setattr("app.api.sources.extract_image_text", lambda data: "识别后的旅游海报")
    product = client.post(
        "/api/v1/products", json={"name": "海报商品", "category": "旅游线路"}
    ).json()
    response = client.post(
        f"/api/v1/products/{product['id']}/sources",
        files={"file": ("poster.png", BytesIO(b"fake-image"), "image/png")},
    )
    assert response.status_code == 201, response.text
    assert response.json()["type"] == "image"


def test_rejects_unsupported_upload(client):
    product = client.post(
        "/api/v1/products", json={"name": "危险文件测试", "category": "旅游线路"}
    ).json()
    response = client.post(
        f"/api/v1/products/{product['id']}/sources",
        files={"file": ("payload.exe", BytesIO(b"MZ"), "application/octet-stream")},
    )
    assert response.status_code == 400

