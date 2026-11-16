from conftest import create_product


def test_add_and_delete_manual_attribute(client):
    product_id = create_product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/attributes",
        json={"label": "出行天数", "value": "5 天 4 晚", "status": "confirmed"},
    )
    assert response.status_code == 201, response.text
    attribute = response.json()
    assert attribute["origin"] == "manual"
    assert attribute["source_id"] is None

    listing = client.get(f"/api/v1/products/{product_id}").json()
    assert any(item["id"] == attribute["id"] for item in listing["attributes"])

    deleted = client.delete(f"/api/v1/attributes/{attribute['id']}")
    assert deleted.status_code == 204
    after = client.get(f"/api/v1/products/{product_id}").json()
    assert all(item["id"] != attribute["id"] for item in after["attributes"])


def test_delete_missing_attribute_returns_404(client):
    response = client.delete("/api/v1/attributes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
