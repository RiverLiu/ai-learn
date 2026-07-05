import pytest
from fastapi.testclient import TestClient

from main import app, get_item_db


def override_get_item_db():
    """覆盖数据库依赖，使用测试数据。"""
    return {"bar": {"name": "Bar", "price": 100.0}}


@pytest.fixture
def client():
    app.dependency_overrides[get_item_db] = override_get_item_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
