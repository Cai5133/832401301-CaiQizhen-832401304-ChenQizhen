import json
import sqlite3
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from openpyxl import Workbook, load_workbook

from app.services import excel


def workbook_bytes(rows=(), headers=excel.HEADERS, sheet_name="Contacts"):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    return output.getvalue()


def upload(client, content, filename="contacts.xlsx"):
    return client.post("/api/contacts/import", files={"file": (filename, content, excel.MIME_TYPE)})


def test_template_and_empty_export_are_valid_and_importable(client):
    for kind, expected_count in [("template", 1), ("export", 0)]:
        response = client.get(f"/api/contacts/{kind}")
        assert response.status_code == 200
        assert response.headers["content-type"] == excel.MIME_TYPE
        assert "attachment; filename=" in response.headers["content-disposition"]
        workbook = load_workbook(BytesIO(response.content))
        assert workbook.sheetnames == ["Contacts"]
        assert tuple(cell.value for cell in workbook.active[1]) == excel.HEADERS
        workbook.close()
        assert upload(client, response.content).json() == {"imported": expected_count, "errors": []}
        if kind == "template":
            client.delete("/api/contacts/1")


def test_round_trip_duplicates_unicode_values_and_leading_zero(client, contact):
    contact["name"] = "同名测试"
    contact["isFavorite"] = True
    contact["methods"] += [{"type": "email", "value": "two@example.com"},
                           {"type": "address", "value": "示例市, A座" * 50},
                           {"type": "social", "value": "=demo_social"}]
    first = client.post("/api/contacts", json=contact).json()
    second = client.post("/api/contacts", json=contact).json()
    exported = client.get("/api/contacts/export").content
    workbook = load_workbook(BytesIO(exported))
    assert workbook.active.max_row == 3
    assert json.loads(workbook.active["C2"].value)[0] == {"label": "手机", "value": "0013800000000"}
    workbook.close()
    client.delete(f"/api/contacts/{first['id']}")
    client.delete(f"/api/contacts/{second['id']}")
    assert upload(client, exported).json() == {"imported": 2, "errors": []}
    items = client.get("/api/contacts").json()["items"]
    for item in items:
        assert item["name"] == "同名测试" and item["isFavorite"] is True
        assert sorted((m["type"], m["label"], m["value"]) for m in item["methods"]) == sorted(
            (m["type"], m["label"], m["value"]) for m in first["methods"])
    assert upload(client, exported).json()["imported"] == 2
    assert client.get("/api/contacts").json()["total"] == 4


def test_formula_like_contact_names_are_exported_as_text(client):
    for name in ["=1+1", "+test", "-test", "@demo"]:
        assert client.post("/api/contacts", json={"name": name}).status_code == 201
    exported = client.get("/api/contacts/export").content
    workbook = load_workbook(BytesIO(exported), data_only=False)
    assert [workbook.active.cell(row, 1).data_type for row in range(2, 6)] == ["s"] * 4
    assert workbook.active["A2"].value == "=1+1"
    workbook.close()
    assert upload(client, exported).json()["imported"] == 4


def test_collects_row_errors_and_writes_nothing(client):
    content = workbook_bytes([
        ["有效测试", 1, '["00123"]', "[]", "[]", "[]"],
        ["  ", 2, "[123]", "bad JSON", "[]", "[]"],
        ["另一个错误", 0, '[""]', "[]", "[]", "[]"],
    ])
    response = upload(client, content)
    assert response.status_code == 422
    errors = response.json()["detail"]["errors"]
    assert {(e["row"], e["column"]) for e in errors} >= {(3, "姓名"), (3, "收藏"), (3, "电话"), (3, "邮箱"), (4, "电话")}
    assert client.get("/api/contacts").json()["total"] == 0


@pytest.mark.parametrize("row", [
    ["=1+1", 0, "[]", "[]", "[]", "[]"],
    ["测试", True, "[]", "[]", "[]", "[]"],
    [123, 0, "[]", "[]", "[]", "[]"],
    ["测试", 0, "{ }", "[]", "[]", "[]"],
    ["测试", 0, '[null]', "[]", "[]", "[]"],
    ["测试", 0, '[{"value":"00123","label":12}]', "[]", "[]", "[]"],
    ["测试", 0, json.dumps([{"value": "00123", "label": "a" * 101}]), "[]", "[]", "[]"],
    ["测试", 0, '[{"label":"手机"}]', "[]", "[]", "[]"],
    ["测试", 0, '[{"value":"00123","extra":"ignored?"}]', "[]", "[]", "[]"],
    ["测试", 0, '"text"', "[]", "[]", "[]"],
    ["测试", 0, json.dumps(["a"] * 101), "[]", "[]", "[]"],
    ["测试", 0, "[]", "[]", "[]", "[]", "多余数据"],
])
def test_invalid_rows_rejected(client, row):
    assert upload(client, workbook_bytes([row])).status_code == 422
    assert client.get("/api/contacts").json()["total"] == 0


def test_skip_blank_rows_accept_empty_methods_and_text_favorite(client):
    content = workbook_bytes([[None] * 6, ["测试甲", " 1 ", None, None, None, None],
                              ["  "] * 6, ["测试乙", 0, "[]", "[]", "[]", "[]"]])
    assert upload(client, content).json() == {"imported": 2, "errors": []}
    items = client.get("/api/contacts").json()["items"]
    assert items[0]["isFavorite"] is True and items[1]["isFavorite"] is False
    assert items[0]["methods"] == items[1]["methods"] == []


@pytest.mark.parametrize("content,filename,status", [
    (b"not a workbook", "contacts.xlsx", 400),
    (b"", "contacts.xlsx", 400),
    (b"name,phone", "contacts.csv", 400),
    (b"x" * (excel.MAX_FILE_BYTES + 1), "contacts.xlsx", 413),
    (workbook_bytes(headers=("姓名", "电话")), "contacts.xlsx", 422),
    (workbook_bytes(sheet_name="Sheet1"), "contacts.xlsx", 422),
])
def test_bad_files(client, content, filename, status):
    response = upload(client, content, filename)
    assert response.status_code == status and "detail" in response.json()
    assert client.get("/api/contacts").json()["total"] == 0


def test_row_limit_and_empty_row_scan_limit(client):
    rows = [[f"测试{i}", 0, "[]", "[]", "[]", "[]"] for i in range(excel.MAX_ROWS + 1)]
    response = upload(client, workbook_bytes(rows))
    assert response.status_code == 422
    assert response.json()["detail"]["errors"][0]["row"] == 5002
    assert client.get("/api/contacts").json()["total"] == 0
    rows = [[None] * 6] * excel.MAX_SCANNED_ROWS + [["远处测试", 0]]
    assert upload(client, workbook_bytes(rows)).status_code == 422


def test_database_error_during_import_rolls_back_all_rows(client, database_path):
    with sqlite3.connect(database_path) as connection:
        connection.execute("""CREATE TRIGGER reject_contact BEFORE INSERT ON contacts
            WHEN NEW.name = '失败测试' BEGIN SELECT RAISE(ABORT, 'test failure'); END""")
    with pytest.raises(sqlite3.IntegrityError):
        upload(client, workbook_bytes([["正常测试", 0], ["失败测试", 0]]))
    assert client.get("/api/contacts").json()["total"] == 0


def test_zip_expansion_limit(client):
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("huge.xml", b"x" * (excel.MAX_EXPANDED_BYTES + 1))
    assert upload(client, output.getvalue()).status_code == 413


def test_export_rejects_cell_overflow_without_silent_truncation(client):
    response = client.post("/api/contacts", json={"name": "长内容测试", "methods": [
        {"type": "address", "value": "字" * 2000} for _ in range(20)]})
    assert response.status_code == 201
    response = client.get("/api/contacts/export")
    assert response.status_code == 422
    assert "无法保存" in response.json()["detail"]
