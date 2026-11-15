import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def database_path(tmp_path):
    return tmp_path / "contacts.sqlite3"


@pytest.fixture
def client(database_path):
    with TestClient(create_app(database_path)) as client:
        yield client


@pytest.fixture
def contact():
    return {"name": "  测试联系人甲  ", "isFavorite": False, "methods": [
        {"type": "phone", "label": "手机", "value": "0013800000000"},
        {"type": "phone", "label": "工作", "value": "+44 (0)20 1234 ext.9"},
        {"type": "email", "label": "学校", "value": "demo@example.com"}]}
