import os
from typing import Optional
import uuid
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.db import get_conn

app = FastAPI()

TENANT_ID = 1  # temporary: day 9 takes this from the logged-in user
USER_ID = 1  # temporary: day 9 takes this from the logged-in user


class ItemIn(BaseModel):
    name: str = Field(min_length=1)
    stock: int = Field(ge=0)


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    stock: Optional[int] = Field(default=None, ge=0)


class OrderIn(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", status_code=201)
def create_item(item: ItemIn):
    sku = "SKU-" + uuid.uuid4().hex[:8].upper()
    with get_conn() as conn:
        row = conn.execute(
            "INSERT INTO items (tenant_id, name, stock, sku) VALUES (%s, %s, %s, %s) "
            "RETURNING id, name, stock, sku",
            (TENANT_ID, item.name, item.stock, sku),
        ).fetchone()
    return row


@app.get("/items")
def list_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, stock FROM items WHERE tenant_id = %s "
            "ORDER BY id LIMIT %s OFFSET %s",
            (TENANT_ID, limit, offset),
        ).fetchall()
    return rows


@app.get("/items/{item_id}")
def get_item(item_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, stock FROM items WHERE id = %s AND tenant_id = %s",
            (item_id, TENANT_ID),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="item not found")
    return row


@app.patch("/items/{item_id}")
def update_item(item_id: int, update: ItemUpdate):
    with get_conn() as conn:
        row = conn.execute(
            "UPDATE items SET name = COALESCE(%s, name), stock = COALESCE(%s, stock) "
            "WHERE id = %s AND tenant_id = %s RETURNING id, name, stock",
            (update.name, update.stock, item_id, TENANT_ID),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="item not found")
    return row


def take_stock_atomic(conn, order: OrderIn):
    # check and decrement in one statement, so no other request can slip
    # in between the read and the write
    updated = conn.execute(
        "UPDATE items SET stock = stock - %s "
        "WHERE id = %s AND tenant_id = %s AND stock >= %s",
        (order.quantity, order.item_id, TENANT_ID, order.quantity),
    ).rowcount
    if updated == 0:
        exists = conn.execute(
            "SELECT 1 FROM items WHERE id = %s AND tenant_id = %s",
            (order.item_id, TENANT_ID),
        ).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="item not found")
        raise HTTPException(status_code=409, detail="not enough stock")


def take_stock_for_update(conn, order: OrderIn):
    # lock the row; concurrent requests wait here until this transaction ends,
    # then read the already-decremented stock
    item = conn.execute(
        "SELECT stock FROM items WHERE id = %s AND tenant_id = %s FOR UPDATE",
        (order.item_id, TENANT_ID),
    ).fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    if item["stock"] < order.quantity:
        raise HTTPException(status_code=409, detail="not enough stock")
    conn.execute(
        "UPDATE items SET stock = %s WHERE id = %s AND tenant_id = %s",
        (item["stock"] - order.quantity, order.item_id, TENANT_ID),
    )


# both are safe; atomic holds the row lock for less time (see NOTES.md)
take_stock = (
    take_stock_for_update
    if os.environ.get("ORDER_LOCKING") == "for_update"
    else take_stock_atomic
)


@app.post("/orders", status_code=201)
def create_order(order: OrderIn):
    # one transaction: if anything below fails, the stock change rolls back too
    with get_conn() as conn:
        take_stock(conn, order)
        row = conn.execute(
            "INSERT INTO orders (tenant_id, user_id) VALUES (%s, %s) "
            "RETURNING id",
            (TENANT_ID, USER_ID),
        ).fetchone()
        conn.execute(
            "INSERT INTO order_items (order_id, item_id, quantity) "
            "VALUES (%s, %s, %s)",
            (row["id"], order.item_id, order.quantity),
        )
    return {"id": row["id"], "item_id": order.item_id, "quantity": order.quantity}
