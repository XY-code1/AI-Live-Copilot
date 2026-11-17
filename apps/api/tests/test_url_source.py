from conftest import create_product

HTML = """
<html><head><title>川西五日游 详情页</title></head>
<body><h1>川西五日游</h1><p>出行天数：5 天 4 晚</p><p>出行方式：小团</p></body></html>
"""


def test_create_url_source(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.sources.fetch_url_text",
        lambda url: ("川西五日游 详情页", "川西五日游\n出行天数：5 天 4 晚\n出行方式：小团"),
    )
    product_id = create_product(client)

    response = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/product/chuanxi"},
    )
    assert response.status_code == 201, response.text
    source = response.json()
    assert source["type"] == "url"
    assert source["name"] == "川西五日游 详情页"
    assert source["reference"] == "https://example.com/product/chuanxi"

    text_response = client.get(f"/api/v1/sources/{source['id']}")
    assert "出行天数：5 天 4 晚" in text_response.json()["text"]


def test_url_source_fetch_failure_returns_400(client, monkeypatch):
    def failing_fetch(url):
        raise ValueError("boom")

    monkeypatch.setattr("app.api.sources.fetch_url_text", failing_fetch)
    product_id = create_product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/bad"},
    )
    assert response.status_code == 400
