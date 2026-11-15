from fastapi.testclient import TestClient
from app.main import create_app


def test_production_serves_frontend_without_shadowing_api(database_path, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<h1>Production frontend</h1>")
    (dist / "assets").mkdir()
    (dist / "assets/app.js").write_text("console.log('loaded')")
    with TestClient(create_app(database_path, dist)) as client:
        assert "Production frontend" in client.get("/").text
        assert client.get("/assets/app.js").status_code == 200
        assert client.get("/api/health").json() == {"status": "ok"}
        assert client.post("/api/contacts", json={"name": "Production"}).status_code == 201
        assert client.get("/api/contacts").json()["total"] == 1
        assert client.get("/api/unknown").status_code == 404
        assert client.get("/backend/data/contacts.sqlite3").status_code == 404
        assert client.get("/assets/missing.js").status_code == 404


def test_api_only_app_runs_without_frontend_build(database_path, tmp_path):
    with TestClient(create_app(database_path, tmp_path / "missing")) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/").status_code == 404
