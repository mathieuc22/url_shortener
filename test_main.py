import pytest
from fastapi.testclient import TestClient
from src.main import api_app
from src.api.models import UrlEntry
from src.api.internal.data import read_data, write_data
from datetime import datetime

client = TestClient(api_app)


def test_create_url_with_param():
    url_entry = UrlEntry(
        id="testid", url="https://test.com", created_at=datetime.utcnow()
    )
    write_data([url_entry])
    response = client.post("/urls", params={"url": "https://example.com"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://example.com"


def test_create_url_with_json():
    url_entry = UrlEntry(
        id="testid", url="https://test.com", created_at=datetime.utcnow()
    )
    write_data([url_entry])
    response = client.post("/urls", json={"url": "https://example.com"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://example.com"


def test_list_urls():
    response = client.get("/urls")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_url():
    url_entry = UrlEntry(
        id="testid", url="https://example.com", created_at=datetime.utcnow()
    )
    write_data([url_entry])

    response = client.get(f"/urls/{url_entry.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == url_entry.id
    assert data["url"] == url_entry.url


def test_get_url_not_found():
    response = client.get("/urls/nonexistentid")
    assert response.status_code == 404


def test_redirect_url():
    url_entry = UrlEntry(
        id="testid", url="https://example.com", created_at=datetime.utcnow()
    )
    write_data([url_entry])

    response = client.get(f"/{url_entry.id}", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == url_entry.url

    # Test for non-existent ID
    response2 = client.get("/nonexistent_id")
    assert response2.status_code == 404
