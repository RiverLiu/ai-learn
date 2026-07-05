import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(name="client")
def client_fixture():
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as client:
        yield client
    SQLModel.metadata.drop_all(engine)


def register_user(client: TestClient, username: str = "alice"):
    return client.post(
        "/users/",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "secret",
            "full_name": "Alice",
        },
    )


def get_token(client: TestClient, username: str = "alice"):
    response = client.post(
        "/auth/token",
        data={"username": username, "password": "secret"},
    )
    return response.json()["access_token"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register(client):
    response = register_user(client)
    assert response.status_code == 201
    assert response.json()["username"] == "alice"


def test_register_duplicate(client):
    register_user(client)
    response = register_user(client)
    assert response.status_code == 400


def test_login(client):
    register_user(client)
    token = get_token(client)
    assert token


def test_create_todo(client):
    register_user(client)
    token = get_token(client)

    response = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "学习 FastAPI", "description": "完成教程"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "学习 FastAPI"
    assert data["completed"] is False


def test_read_todos(client):
    register_user(client)
    token = get_token(client)

    client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "任务 1"},
    )
    client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "任务 2"},
    )

    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_todo(client):
    register_user(client)
    token = get_token(client)

    created = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "任务"},
    ).json()

    response = client.put(
        f"/todos/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"completed": True},
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_todo(client):
    register_user(client)
    token = get_token(client)

    created = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "任务"},
    ).json()

    response = client.delete(
        f"/todos/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


def test_todo_isolation(client):
    """用户只能看到自己的待办事项。"""
    register_user(client, "alice")
    register_user(client, "bob")

    alice_token = get_token(client, "alice")
    bob_token = get_token(client, "bob")

    client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"title": "Alice 的任务"},
    )

    bob_response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert bob_response.status_code == 200
    assert len(bob_response.json()) == 0
