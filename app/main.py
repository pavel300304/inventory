from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()
items: dict[int, dict] = {}


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
    item_id = len(items) + 1
    items[item_id] = {"id": item_id, **item.model_dump()}
    return items[item_id]


@app.get("/items")
def list_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    all_items = list(items.values())
    return all_items[offset : offset + limit]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="item not found")
    return items[item_id]


@app.patch("/items/{item_id}")
def update_item(item_id: int, update: ItemUpdate):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="item not found")
    changes = update.model_dump(exclude_unset=True)
    items[item_id].update(changes)
    return items[item_id]