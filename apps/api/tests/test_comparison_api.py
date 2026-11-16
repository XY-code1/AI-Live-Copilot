from conftest import create_product


def _create_competitor(client, name="川西五日游 · 经典版") -> str:
    response = client.post(
        "/api/v1/competitors",
        json={"name": name, "brand": "某旅行社", "price": 3580},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_competitor_crud(client):
    competitor_id = _create_competitor(client)

    listing = client.get("/api/v1/competitors")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    updated = client.patch(f"/api/v1/competitors/{competitor_id}", json={"brand": "另一家"})
    assert updated.status_code == 200
    assert updated.json()["brand"] == "另一家"

    deleted = client.delete(f"/api/v1/competitors/{competitor_id}")
    assert deleted.status_code == 204
    assert client.get("/api/v1/competitors").json() == []


def test_comparison_with_differences(client):
    product_id = create_product(client)
    competitor_id = _create_competitor(client)

    comparison = client.post(
        "/api/v1/comparisons",
        json={"product_id": product_id, "competitor_id": competitor_id},
    )
    assert comparison.status_code == 201, comparison.text
    comparison_id = comparison.json()["id"]
    assert comparison.json()["status"] == "pending"

    difference = client.post(
        f"/api/v1/comparisons/{comparison_id}/differences",
        json={
            "field": "价格",
            "ours": "¥3280",
            "theirs": "¥3580",
            "evidence_type": "source",
            "side": "ours",
        },
    )
    assert difference.status_code == 201, difference.text
    body = difference.json()
    assert body["evidence_type"] == "source"
    assert body["side"] == "ours"

    listing = client.get(f"/api/v1/products/{product_id}/comparisons")
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert listing.json()[0]["differences"][0]["field"] == "价格"

    deleted = client.delete(f"/api/v1/comparisons/differences/{body['id']}")
    assert deleted.status_code == 204
    after = client.get(f"/api/v1/comparisons/{comparison_id}").json()
    assert after["differences"] == []


def test_delete_comparison_cascades(client):
    product_id = create_product(client)
    competitor_id = _create_competitor(client)
    comparison_id = client.post(
        "/api/v1/comparisons",
        json={"product_id": product_id, "competitor_id": competitor_id},
    ).json()["id"]

    assert client.delete(f"/api/v1/comparisons/{comparison_id}").status_code == 204
    assert client.get(f"/api/v1/comparisons/{comparison_id}").status_code == 404
