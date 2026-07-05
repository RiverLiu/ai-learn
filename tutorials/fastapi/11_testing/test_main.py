from fastapi.testclient import TestClient

from main import app


def test_read_items():
    with TestClient(app) as client:
        response = client.get("/items/?q=phone&skip=0&limit=5")
        assert response.status_code == 200
        assert response.json() == {
            "q": "phone",
            "skip": 0,
            "limit": 5,
        }


def test_read_item_found(client):
    response = client.get("/items/bar")
    assert response.status_code == 200
    assert response.json()["name"] == "Bar"


def test_read_item_not_found(client):
    response = client.get("/items/unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item():
    with TestClient(app) as client:
        response = client.post(
            "/items/",
            json={"name": "Phone", "price": 5999.0},
        )
        assert response.status_code == 201
        assert response.json() == {"name": "Phone", "price": 5999.0}


def test_create_item_invalid():
    with TestClient(app) as client:
        response = client.post("/items/", json={"name": "Phone", "price": "free"})
        assert response.status_code == 422
