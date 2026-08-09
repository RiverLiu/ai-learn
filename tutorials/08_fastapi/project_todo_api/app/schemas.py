from pydantic import BaseModel, ConfigDict


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str | None = None
    disabled: bool


class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    completed: bool
    owner_id: int
