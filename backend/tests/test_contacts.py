import sqlite3
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_empty_list(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/contacts").json() == {"items": [], "total": 0}
    assert client.get("/docs").status_code == 200


def test_create_detail_and_replace_methods(client, contact):
    response = client.post("/api/contacts", json=contact)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "测试联系人甲"
    assert len(created["methods"]) == 3
    assert created["methods"][0]["value"] == "0013800000000"
    path = f"/api/contacts/{created['id']}"
    assert client.get(path).json() == created
    contact["methods"] = [{"type": "social", "value": "  demo_social  "}]
    contact["isFavorite"] = True
    edited = client.put(path, json=contact).json()
    assert edited["isFavorite"] is True
    assert edited["methods"] == [{"type": "social", "label": "", "value": "demo_social"}]
    assert client.get(path).json() == edited
    contact["methods"] = []
    assert client.put(path, json=contact).json()["methods"] == []


def test_favorite_is_idempotent_and_survives_restart(client, contact, database_path):
    created = client.post("/api/contacts", json=contact).json()
    path = f"/api/contacts/{created['id']}/favorite"
    for _ in range(2):
        response = client.patch(path, json={"isFavorite": True})
        assert response.status_code == 200 and response.json()["isFavorite"] is True
    with TestClient(create_app(database_path)) as restarted:
        saved = restarted.get("/api/contacts", params={"favorite": True}).json()
        assert saved["total"] == 1
        assert saved["items"][0]["methods"] == created["methods"]
    assert client.patch(path, json={"isFavorite": False}).json()["isFavorite"] is False
    assert client.get("/api/contacts?favorite=true").json()["total"] == 0
    assert client.get("/api/contacts?favorite=false").json()["total"] == 1


def test_search_name_methods_combined_and_literal_sql(client):
    for name, value, favorite in [("测试甲", "ÄBC@Example.com", True), ("测试乙", "100%_demo", False)]:
        assert client.post("/api/contacts", json={"name": name, "isFavorite": favorite,
                           "methods": [{"type": "email", "value": value}]}).status_code == 201
    for query in ("测试甲", "äbc", "EXAMPLE"):
        result = client.get("/api/contacts", params={"q": query, "favorite": True}).json()
        assert result["total"] == 1 and result["items"][0]["name"] == "测试甲"
    assert client.get("/api/contacts", params={"q": "%_"}).json()["total"] == 1
    assert client.get("/api/contacts", params={"q": "' OR 1=1 --"}).json()["total"] == 0
    assert [c["id"] for c in client.get("/api/contacts").json()["items"]] == [1, 2]


def test_delete_cascades_and_missing_ids(client, contact, database_path):
    contact_id = client.post("/api/contacts", json=contact).json()["id"]
    response = client.delete(f"/api/contacts/{contact_id}")
    assert response.status_code == 204 and response.content == b""
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT count(*) FROM contact_methods").fetchone()[0] == 0
    for method, body in [("get", None), ("put", contact), ("delete", None),
                         ("patch", {"isFavorite": True})]:
        path = f"/api/contacts/{contact_id}" + ("/favorite" if method == "patch" else "")
        response = client.request(method, path, **({"json": body} if body else {}))
        assert response.status_code == 404 and response.json()["detail"] == "联系人不存在"


@pytest.mark.parametrize("change", [
    {"name": "  "}, {"name": "字" * 101}, {"isFavorite": "false"}, {"isFavorite": 1},
    {"methods": [{"type": "fax", "value": "123"}]},
    {"methods": [{"type": "phone", "value": " "}]},
    {"methods": [{"type": "phone", "value": 123}]},
    {"methods": [{"type": "phone", "value": "1", "label": None}]},
    {"methods": [{"type": "phone", "value": "1"}] * 101}, {"extra": "unexpected"},
])
def test_invalid_create_and_edit_leave_original_intact(client, contact, change):
    original = client.post("/api/contacts", json=contact).json()
    invalid = deepcopy(contact)
    invalid.update(change)
    assert client.post("/api/contacts", json=invalid).status_code == 422
    assert client.put(f"/api/contacts/{original['id']}", json=invalid).status_code == 422
    assert client.get(f"/api/contacts/{original['id']}").json() == original
    assert client.get("/api/contacts").json()["total"] == 1


def test_database_failure_rolls_back_replace(client, contact, database_path):
    original = client.post("/api/contacts", json=contact).json()
    with sqlite3.connect(database_path) as connection:
        connection.execute("""CREATE TRIGGER reject_method BEFORE INSERT ON contact_methods
            WHEN NEW.value = 'reject' BEGIN SELECT RAISE(ABORT, 'test failure'); END""")
    contact["name"] = "不会保存"
    contact["methods"] = [{"type": "phone", "value": "reject"}]
    with pytest.raises(sqlite3.IntegrityError):
        client.put(f"/api/contacts/{original['id']}", json=contact)
    assert client.get(f"/api/contacts/{original['id']}").json() == original


def test_cors_only_allows_configured_origins(monkeypatch, database_path):
    monkeypatch.setenv("CORS_ORIGINS", "http://127.0.0.1:5173")
    with TestClient(create_app(database_path)) as client:
        allowed = client.options("/api/contacts", headers={"Origin": "http://127.0.0.1:5173",
                                "Access-Control-Request-Method": "PATCH"})
        assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
        blocked = client.options("/api/contacts", headers={"Origin": "https://other.example",
                                "Access-Control-Request-Method": "PATCH"})
        assert "access-control-allow-origin" not in blocked.headers
