from fastapi import FastAPI

app = FastAPI(
    title="Hello FastAPI",
    description="第一个 FastAPI 应用",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """返回欢迎信息。"""
    return {"message": "Hello FastAPI"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    """根据 ID 返回一个项目。"""
    return {"item_id": item_id}

@app.post("/items/{item_id}")
def read_item(item_id: int):
    """根据 ID 返回一个项目。"""
    return {"item_id-post": item_id}
