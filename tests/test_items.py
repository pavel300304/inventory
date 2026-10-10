from fastapi.testclient import TestClient
import psycopg
from app.main import app

client = TestClient(app)


def test_create_item_returns_201():
    response = client.post("/items", json={"name": "bolt", "stock": 5})
    assert response.status_code == 201
    assert response.json()["name"] == "bolt"


def test_negative_stock_is_rejected():
    response = client.post("/items", json={"name": "bolt", "stock": -1})
    assert response.status_code == 422


def test_list_is_empty_at_start():
    response = client.get("/items")
    assert response.json() == []


def test_create_item():
    response = client.post("/items", json={"name": "bolt", "stock": 5})
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_missing_item_returns_404():
    response = client.get("/items/999")
    assert response.status_code == 404


def test_empty_name_is_rejected():
    response = client.post("/items", json={"name": "", "stock": 1})
    assert response.status_code == 422


def test_get_returns_created_item():
    item_id = client.post(
        "/items", json={"name": "nut", "stock": 7}).json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"id": item_id, "name": "nut", "stock": 7}


def test_pagination_returns_requested_page():
    for i in range(5):
        client.post("/items", json={"name": f"item-{i}", "stock": 1})
    response = client.get("/items", params={"limit": 2, "offset": 2})
    assert [item["name"] for item in response.json()] == ["item-2", "item-3"]


def test_pagination_limit_is_capped():
    response = client.get("/items", params={"limit": 101})
    assert response.status_code == 422


def test_patch_changes_only_sent_field():
    item_id = client.post(
        "/items", json={"name": "bolt", "stock": 5}).json()["id"]
    response = client.patch(f"/items/{item_id}", json={"stock": 9})
    assert response.json() == {"id": item_id, "name": "bolt", "stock": 9}


def test_patch_missing_item_returns_404():
    response = client.patch("/items/999", json={"stock": 1})
    assert response.status_code == 404


def test_delete_item():
    item_id = client.post(
        "/items", json={"name": "bolt", "stock": 5}).json()["id"]
    assert client.delete(f"/items/{item_id}").status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_delete_missing_item_returns_404():
    assert client.delete("/items/999").status_code == 404


def test_delete_item_with_orders_returns_409():
    item_id = client.post(
        "/items", json={"name": "bolt", "stock": 5}).json()["id"]
    client.post("/orders", json={"item_id": item_id, "quantity": 1})
    assert client.delete(f"/items/{item_id}").status_code == 409
    assert client.get(f"/items/{item_id}").status_code == 200


def test_database_down_returns_503(monkeypatch):
    def broken_connection():
        raise psycopg.OperationalError("database is down")

    monkeypatch.setattr("app.main.get_conn", broken_connection)
    response = client.get("/items")
    assert response.status_code == 503
