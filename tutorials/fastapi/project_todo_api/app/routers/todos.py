from fastapi import APIRouter, HTTPException, status

from app.crud import (
    create_todo,
    delete_todo,
    get_todo,
    get_todos,
    update_todo,
)
from app.database import SessionDep
from app.dependencies import CurrentUser
from app.schemas import TodoCreate, TodoResponse, TodoUpdate

router = APIRouter()


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create(user_todo: TodoCreate, current_user: CurrentUser, session: SessionDep):
    """创建待办事项。"""
    return create_todo(session, user_todo, current_user.id)


@router.get("/", response_model=list[TodoResponse])
def read_list(
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """查询当前用户的待办事项列表。"""
    return get_todos(session, owner_id=current_user.id, skip=skip, limit=limit)


@router.get("/{todo_id}", response_model=TodoResponse)
def read_one(todo_id: int, current_user: CurrentUser, session: SessionDep):
    """查询单个待办事项。"""
    db_todo = get_todo(session, todo_id=todo_id, owner_id=current_user.id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    return db_todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新待办事项。"""
    db_todo = get_todo(session, todo_id=todo_id, owner_id=current_user.id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    return update_todo(session, db_todo, todo_update)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(todo_id: int, current_user: CurrentUser, session: SessionDep):
    """删除待办事项。"""
    db_todo = get_todo(session, todo_id=todo_id, owner_id=current_user.id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    delete_todo(session, db_todo)
    return None
