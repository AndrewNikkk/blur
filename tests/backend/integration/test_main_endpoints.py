import pytest


@pytest.mark.integration
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world"}


@pytest.mark.integration
def test_robots_txt_contains_disallow_and_sitemap(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "Disallow: /login" in body
    assert "Disallow: /profile" in body
    assert "Sitemap:" in body


@pytest.mark.integration
def test_sitemap_xml_returns_xml(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    body = response.text
    assert "<urlset" in body
    assert "<loc>" in body
