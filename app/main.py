from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.db import get_conn

app = FastAPI()

TENANT_ID = 1  # temporary: day 9 takes this from the logged-in user


class ItemIn(BaseModel):
    name: str = Field(min_length=1)
    stock: int = Field(ge=0)


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    stock: Optional[int] = Field(default=None, ge=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", status_code=201)
def create_item(item: ItemIn):
    with get_conn() as conn:
        row = conn.execute(
            "INSERT INTO items (tenant_id, name, stock) VALUES (%s, %s, %s) "
            "RETURNING id, name, stock",
            (TENANT_ID, item.name, item.stock),
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
