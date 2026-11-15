"""Real HTTP verification, including a process restart. Uses a temporary database."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

import httpx

BACKEND = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def start(database_path, port):
    env = dict(os.environ, ADDRESS_BOOK_DB=str(database_path))
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host",
                                "127.0.0.1", "--port", str(port)], cwd=BACKEND, env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("后端进程未成功启动")
        try:
            if httpx.get(f"http://127.0.0.1:{port}/api/health", timeout=1).status_code == 200:
                return process
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    stop(process)
    raise RuntimeError("等待服务启动超时")


def stop(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main():
    with tempfile.TemporaryDirectory(prefix="address-book-smoke-") as directory:
        database_path = Path(directory) / "contacts.sqlite3"
        port = free_port()
        process = start(database_path, port)
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=15) as client:
            try:
                payload = {"name": "HTTP测试", "methods": [
                    {"type": "phone", "value": "0013800000000"},
                    {"type": "phone", "value": "+44 20 0000 ext.9"},
                    {"type": "email", "value": "http@example.com"}]}
                response = client.post("/api/contacts", json=payload)
                assert response.status_code == 201, response.text
                contact_id = response.json()["id"]
                path = f"/api/contacts/{contact_id}"
                payload["name"] = "HTTP编辑测试"
                assert client.put(path, json=payload).json()["name"] == payload["name"]
                assert client.patch(path + "/favorite", json={"isFavorite": True}).json()["isFavorite"]
                assert client.get("/api/contacts?favorite=true&q=example.com").json()["total"] == 1
                exported = client.get("/api/contacts/export")
                assert exported.status_code == 200 and exported.content.startswith(b"PK")
                stop(process)
                process = start(database_path, port)
                saved = client.get(path).json()
                assert saved["isFavorite"] is True and len(saved["methods"]) == 3
                assert client.delete(path).status_code == 204
                assert client.get("/api/contacts").json()["total"] == 0
                imported = client.post("/api/contacts/import", files={
                    "file": ("round-trip.xlsx", exported.content)})
                assert imported.json() == {"imported": 1, "errors": []}, imported.text
                assert client.get("/api/contacts").json()["items"][0]["methods"][0]["value"] == "0013800000000"
                for sample in sorted((BACKEND.parent / "samples/invalid").glob("*.xlsx")):
                    response = client.post("/api/contacts/import", files={"file": (sample.name, sample.read_bytes())})
                    assert response.status_code == (400 if sample.name == "corrupt.xlsx" else 422), response.text
                assert client.get("/api/contacts").json()["total"] == 1
                print(json.dumps({"result": "passed", "checks": ["real HTTP CRUD", "favorite search",
                    "process restart persistence", "Excel round trip", "all six invalid samples rejected"]}))
            finally:
                stop(process)


if __name__ == "__main__":
    main()
