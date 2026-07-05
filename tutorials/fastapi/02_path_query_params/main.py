from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(title="项目 ID", ge=1)],
    q: Annotated[str | None, Query(max_length=50)] = None,
):
    """
    路径参数 + 查询参数示例。

    - `item_id`：路径参数，必须为正整数
    - `q`：查询参数，可选，最长 50 个字符
    """
    result = {"item_id": item_id}
    if q:
        result["q"] = q
    return result


@app.get("/users/{user_id}/items/{item_id}")
def read_user_item(
    user_id: int,
    item_id: int,
    detail: Annotated[bool, Query()] = False,
):
    """多个路径参数 + 布尔查询参数。"""
    item = {"user_id": user_id, "item_id": item_id}
    if detail:
        item["detail"] = "显示详情"
    return item


@app.get("/items/")
def list_items(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10,
):
    """分页查询参数示例。"""
    fake_items = [
        {"item_id": i, "name": f"Item {i}"}
        for i in range(skip, skip + limit)
    ]
    return {"skip": skip, "limit": limit, "items": fake_items}
