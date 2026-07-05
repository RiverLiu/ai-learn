from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    """商品请求体模型。"""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=200)
    price: float = Field(gt=0)
    tax: float | None = None


class Address(BaseModel):
    """地址嵌套模型。"""

    city: str
    country: str


class User(BaseModel):
    """用户模型，包含嵌套地址。"""

    name: str
    age: int | None = Field(default=None, ge=0, le=150)
    address: Address | None = None


@app.post("/items/")
def create_item(item: Item):
    """使用 Pydantic 模型接收请求体。"""
    item_dict = item.model_dump()
    if item.tax:
        item_dict["price_with_tax"] = item.price + item.tax
    return item_dict


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, q: str | None = None):
    """同时接收路径参数、请求体和查询参数。"""
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result["q"] = q
    return result


@app.post("/users/")
def create_user(user: User):
    """嵌套模型请求体示例。"""
    return user
