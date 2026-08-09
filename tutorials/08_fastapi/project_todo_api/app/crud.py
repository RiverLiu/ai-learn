from sqlmodel import Session, select

from app.auth import get_password_hash
from app.models import Todo, User
from app.schemas import TodoCreate, TodoUpdate, UserCreate


def create_user(session: Session, user_create: UserCreate) -> User:
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def create_todo(session: Session, todo_create: TodoCreate, owner_id: int) -> Todo:
    db_todo = Todo(
        title=todo_create.title,
        description=todo_create.description,
        owner_id=owner_id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


def get_todos(session: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[Todo]:
    statement = (
        select(Todo)
        .where(Todo.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_todo(session: Session, todo_id: int, owner_id: int) -> Todo | None:
    statement = (
        select(Todo)
        .where(Todo.id == todo_id, Todo.owner_id == owner_id)
    )
    return session.exec(statement).first()


def update_todo(session: Session, db_todo: Todo, todo_update: TodoUpdate) -> Todo:
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


def delete_todo(session: Session, db_todo: Todo) -> None:
    session.delete(db_todo)
    session.commit()
