from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()


class UserIn(BaseModel):
    """用户输入模型，包含密码。"""

    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    """用户输出模型，隐藏密码。"""

    username: str
    email: EmailStr
    full_name: str | None = None


class Item(BaseModel):
    """商品模型。"""

    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


db = {
    1: {"username": "alice", "email": "alice@example.com", "full_name": "Alice L."},
}


@app.post("/users/", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    """创建用户，返回时隐藏密码字段。"""
    return user


@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int):
    """根据 ID 查询用户，不存在则抛出 404。"""
    if user_id not in db:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db[user_id]


@app.post("/items/", response_model=Item, response_model_exclude_unset=True)
def create_item(item: Item):
    """只返回客户端实际设置过的字段。"""
    return item
