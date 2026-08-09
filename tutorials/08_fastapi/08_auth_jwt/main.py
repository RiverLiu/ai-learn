from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    User,
    authenticate_user,
    create_access_token,
    fake_users_db,
    get_current_active_user,
)

app = FastAPI()


@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """登录接口，返回 JWT Token。"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """获取当前登录用户信息。"""
    return current_user


@app.get("/users/me/items")
def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """获取当前用户的项目（受保护路由示例）。"""
    return [{"item_id": 1, "owner": current_user.username}]
