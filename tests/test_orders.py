from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.db import get_conn

client = TestClient(main.app)

STRATEGIES = [main.take_stock_atomic, main.take_stock_for_update]


@pytest.fixture(params=STRATEGIES, ids=lambda s: s.__name__)
def strategy(request, monkeypatch):
    monkeypatch.setattr(main, "take_stock", request.param)
    return request.param


def create_item(stock):
    return client.post("/items", json={"name": "bolt", "stock": stock}).json()["id"]


def stock_of(item_id):
    return client.get(f"/items/{item_id}").json()["stock"]


def order_count():
    with get_conn() as conn:
        return conn.execute("SELECT count(*) AS n FROM orders").fetchone()["n"]


def test_order_reduces_stock(strategy):
    item_id = create_item(5)
    response = client.post("/orders", json={"item_id": item_id, "quantity": 2})
    assert response.status_code == 201
    assert stock_of(item_id) == 3


def test_order_without_enough_stock_returns_409(strategy):
    item_id = create_item(1)
    response = client.post("/orders", json={"item_id": item_id, "quantity": 2})
    assert response.status_code == 409
    assert stock_of(item_id) == 1


def test_order_for_missing_item_returns_404(strategy):
    response = client.post("/orders", json={"item_id": 999, "quantity": 1})
    assert response.status_code == 404


def test_zero_quantity_is_rejected():
    item_id = create_item(5)
    response = client.post("/orders", json={"item_id": item_id, "quantity": 0})
    assert response.status_code == 422


def test_failed_order_leaves_stock_unchanged(strategy, monkeypatch):
    item_id = create_item(5)

    def take_stock_then_fail(conn, order):
        strategy(conn, order)
        raise RuntimeError("deliberate failure after taking stock")

    monkeypatch.setattr(main, "take_stock", take_stock_then_fail)
    failing_client = TestClient(main.app, raise_server_exceptions=False)
    response = failing_client.post("/orders", json={"item_id": item_id, "quantity": 2})

    assert response.status_code == 500
    assert stock_of(item_id) == 5
    assert order_count() == 0


def test_concurrent_orders_do_not_oversell(strategy):
    item_id = create_item(1)

    def place_order(_):
        return client.post("/orders", json={"item_id": item_id, "quantity": 1}).status_code

    with ThreadPoolExecutor(max_workers=20) as pool:
        statuses = sorted(pool.map(place_order, range(20)))

    assert statuses == [201] + [409] * 19
    assert stock_of(item_id) == 0
    assert order_count() == 1
