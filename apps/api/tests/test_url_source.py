from conftest import create_product

HTML = """
<html><head><title>川西五日游 详情页</title></head>
<body><h1>川西五日游</h1><p>出行天数：5 天 4 晚</p><p>出行方式：小团</p></body></html>
"""


def test_create_url_source(client, monkeypatch):
    html = f"<html><body>{HTML}</body></html>"
    monkeypatch.setattr(
        "app.api.sources.fetch_url_page",
        lambda url: (
            "川西五日游 详情页",
            "川西五日游\n出行天数：5 天 4 晚\n出行方式：小团",
            url,
            [],
            html,
        ),
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

    monkeypatch.setattr("app.api.sources.fetch_url_page", failing_fetch)
    product_id = create_product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "https://example.com/bad"},
    )
    assert response.status_code == 400


def test_create_url_source_extracts_escaped_link_from_share_text(client, monkeypatch):
    captured = []
    monkeypatch.setattr(
        "app.api.sources.fetch_url_page",
        lambda url: (captured.append(url) or ("抖音商品", "三日游商品详情", url, [], "<html></html>")),
    )
    product_id = create_product(client)
    response = client.post(
        f"/api/v1/products/{product_id}/sources/url",
        json={"url": "四毕达8人小团，戳链接 https\\://v.douyin.com/-W6u4bJRQEM/ 4@9.com"},
    )
    assert response.status_code == 201, response.text
    assert captured == ["https://v.douyin.com/-W6u4bJRQEM/"]
    assert response.json()["reference"] == captured[0]
    source = client.get(f"/api/v1/sources/{response.json()['id']}").json()
    assert "四毕达8人小团" in source["text"]


def test_preview_share_text_infers_product_fields(client, monkeypatch):
    monkeypatch.setattr("app.api.sources.fetch_url_text", lambda url: ("商品详情", ""))
    response = client.post(
        "/api/v1/sources/url/preview",
        json={"url": "1- 【四毕达8人小团】达古冰川三日游，戳链接 https\\://v.douyin.com/demo/"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "【四毕达8人小团】达古冰川三日游"
    assert response.json()["category"] == "旅游线路"
    assert response.json()["url"] == "https://v.douyin.com/demo/"
