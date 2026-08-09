from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


def get_item_db():
    """模拟数据库依赖。"""
    return {"foo": {"name": "Foo", "price": 50.0}}


def common_query_params(q: str | None = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
def read_items(params: dict = Depends(common_query_params)):
    return params


@app.get("/items/{item_id}")
def read_item(item_id: str, db: dict = Depends(get_item_db)):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]


@app.post("/items/", status_code=201)
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
