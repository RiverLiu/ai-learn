from fastapi import APIRouter, HTTPException, status

from app.crud import create_user, get_user_by_username
from app.database import SessionDep
from app.dependencies import CurrentUser
from app.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, session: SessionDep):
    """用户注册。"""
    if get_user_by_username(session, user_create.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    return create_user(session, user_create)


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: CurrentUser):
    """获取当前登录用户信息。"""
    return current_user
