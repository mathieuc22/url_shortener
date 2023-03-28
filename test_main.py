import pytest
from fastapi.testclient import TestClient
from src.main import app, UrlEntry, read_data, write_data

client = TestClient(app)


def test_create_url():
    response = client.post("/urls", params={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://example.com"


def test_list_urls():
    response = client.get("/urls")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_url():
    url_entry = UrlEntry(id="testid", url="https://example.com")
    write_data([url_entry])

    response = client.get(f"/urls/{url_entry.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == url_entry.id
    assert data["url"] == url_entry.url


def test_get_url_not_found():
    response = client.get("/urls/nonexistentid")
    assert response.status_code == 404
