"""Fail an order after stock was taken and check that the stock comes back."""
from fastapi.testclient import TestClient

import app.main as main
from app.db import get_conn

client = TestClient(main.app, raise_server_exceptions=False)


def snapshot(item_id):
    with get_conn() as conn:
        stock = conn.execute(
            "SELECT stock FROM items WHERE id = %s", (item_id,)
        ).fetchone()["stock"]
        orders = conn.execute("SELECT count(*) AS n FROM orders").fetchone()["n"]
    return stock, orders


def check(strategy):
    item_id = client.post("/items", json={"name": "rollback-test", "stock": 5}).json()["id"]
    before = snapshot(item_id)

    def take_stock_then_fail(conn, order):
        strategy(conn, order)
        raise RuntimeError("deliberate failure after taking stock")

    main.take_stock = take_stock_then_fail
    status = client.post("/orders", json={"item_id": item_id, "quantity": 2}).status_code
    after = snapshot(item_id)

    main.take_stock = strategy
    ok_status = client.post("/orders", json={"item_id": item_id, "quantity": 2}).status_code
    final_stock, _ = snapshot(item_id)

    print(f"{strategy.__name__}:")
    print(f"  failing order -> {status}, (stock, orders) before {before}, after {after}")
    print(f"  normal order  -> {ok_status}, stock {final_stock}")
    assert status == 500
    assert after == before, "stock or orders changed despite the failure"
    assert ok_status == 201 and final_stock == 3


original = main.take_stock
try:
    for strategy in (main.take_stock_atomic, main.take_stock_for_update):
        check(strategy)
finally:
    main.take_stock = original
print("OK: a failed order leaves stock and orders unchanged")
