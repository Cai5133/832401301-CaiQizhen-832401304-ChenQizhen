"""Excel: one contact per row, categorized arrays preserving method labels."""
import json
from io import BytesIO
from zipfile import ZipFile

from fastapi import HTTPException
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Font, PatternFill
from pydantic import ValidationError

from ..schemas import ContactInput
from .contacts import insert_contact, list_contacts

HEADERS = ("姓名", "收藏", "电话", "邮箱", "社交账号", "地址")
TYPES = ("phone", "email", "social", "address")
MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_EXPANDED_BYTES = 50 * 1024 * 1024
MAX_ROWS = 5000
MAX_SCANNED_ROWS = 10000


def sample_contacts():
    return [{"name": "测试联系人甲", "isFavorite": True, "methods": [
        {"type": "phone", "value": "0013800000000"},
        {"type": "phone", "value": "+44 20 0000 0000 ext.9"},
        {"type": "email", "value": "demo@example.com"},
        {"type": "email", "value": "demo2@example.com"},
        {"type": "social", "value": "demo_social"},
        {"type": "address", "value": "示例市示例路1号, A座"}]}]


def build_workbook(items):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contacts"
    sheet.append(HEADERS)
    for row_number, contact in enumerate(items, start=2):
        values = [contact["name"], int(contact["isFavorite"])]
        for method_type in TYPES:
            values.append(json.dumps([{"label": method.get("label", ""), "value": method["value"]}
                                      if method.get("label") else method["value"]
                                      for method in contact["methods"]
                                      if method["type"] == method_type], ensure_ascii=False))
        for column, value in enumerate(values, start=1):
            if isinstance(value, str) and (len(value) > 32767 or ILLEGAL_CHARACTERS_RE.search(value)):
                raise HTTPException(status_code=422, detail=f"第 {row_number} 行 {HEADERS[column - 1]} 无法保存为 Excel 文本")
            cell = sheet.cell(row_number, column, value)
            if isinstance(value, str):
                # Explicit string type prevents formula injection without altering the value.
                cell.data_type = "s"
                cell.number_format = "@"
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        sheet.row_dimensions[row_number].height = 60
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="254B65")
        cell.alignment = Alignment(vertical="center")
    sheet.row_dimensions[1].height = 26
    for column, width in zip("ABCDEF", (24, 10, 48, 48, 36, 60)):
        sheet.column_dimensions[column].width = width
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    return output.getvalue()


def export_workbook(database):
    return build_workbook(list_contacts(database)["items"])


def _error(row, column, reason):
    return {"row": row, "column": column, "reason": reason}


def _invalid(errors):
    raise HTTPException(status_code=422, detail={"message": "导入失败，未写入数据", "errors": errors})


def parse_workbook(content: bytes):
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="文件不能超过 5 MB")
    try:
        with ZipFile(BytesIO(content)) as archive:
            if len(archive.infolist()) > 1000 or sum(item.file_size for item in archive.infolist()) > MAX_EXPANDED_BYTES:
                raise HTTPException(status_code=413, detail="工作簿解压后过大")
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=False, keep_links=False)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail="文件不是可读取的 .xlsx 工作簿") from error
    try:
        if "Contacts" not in workbook.sheetnames:
            _invalid([_error(1, "工作表", "缺少 Contacts 工作表")])
        sheet = workbook["Contacts"]
        # Ignore forged worksheet dimensions and stream actual XML rows.
        sheet.reset_dimensions()
        rows = sheet.iter_rows()
        header = next(rows, ())
        if tuple(cell.value for cell in header) != HEADERS:
            _invalid([_error(1, "表头", "必须依次为：" + "、".join(HEADERS))])
        items, errors, count = [], [], 0
        for row_number, cells in enumerate(rows, start=2):
            if row_number > MAX_SCANNED_ROWS + 1:
                _invalid([_error(row_number, "行数", "扫描范围不能超过 10000 行，请移除多余空行")])
            values = [cell.value for cell in cells]
            if all(value is None or (isinstance(value, str) and not value.strip()) for value in values):
                continue
            count += 1
            if count > MAX_ROWS:
                _invalid([_error(row_number, "行数", "每次最多导入 5000 位联系人")])
            row_errors = []
            for index, cell in enumerate(cells):
                if cell.data_type in ("f", "e"):
                    column = HEADERS[index] if index < len(HEADERS) else "额外列"
                    row_errors.append(_error(row_number, column, "不接受公式或 Excel 错误值"))
            if any(value is not None for value in values[6:]):
                row_errors.append(_error(row_number, "额外列", "仅允许模板的六列数据"))
            values = (values + [None] * 6)[:6]
            name, favorite = values[:2]
            if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
                row_errors.append(_error(row_number, "姓名", "必须是 1 至 100 字的非空文本"))
            if isinstance(favorite, bool) or not (
                    (isinstance(favorite, (int, float)) and favorite in (0, 1)) or
                    (isinstance(favorite, str) and favorite.strip() in ("0", "1"))):
                row_errors.append(_error(row_number, "收藏", "只能填 1 或 0"))
            methods = []
            for index, method_type in enumerate(TYPES, start=2):
                value = values[index]
                if value is None or (isinstance(value, str) and not value.strip()):
                    continue
                try:
                    array = json.loads(value) if isinstance(value, str) else None
                    if not isinstance(array, list):
                        raise ValueError
                    parsed_methods = []
                    for item in array:
                        if isinstance(item, str):
                            label, method_value = "", item
                        elif isinstance(item, dict) and set(item) <= {"label", "value"}:
                            label, method_value = item.get("label", ""), item.get("value")
                        else:
                            raise ValueError
                        if (not isinstance(label, str) or len(label.strip()) > 100 or
                                not isinstance(method_value, str) or
                                not 1 <= len(method_value.strip()) <= 2000):
                            raise ValueError
                        parsed_methods.append({"type": method_type, "label": label, "value": method_value})
                    methods.extend(parsed_methods)
                except (ValueError, TypeError):
                    row_errors.append(_error(row_number, HEADERS[index], "需要 JSON 数组：非空文本或含 value、可选 label 的对象；value 为 1 至 2000 字，label 最多 100 字"))
            if len(methods) > 100:
                row_errors.append(_error(row_number, "联系方式", "每位联系人最多 100 项联系方式"))
            if row_errors:
                errors.extend(row_errors)
                continue
            try:
                items.append(ContactInput(name=name, isFavorite=str(favorite).strip() in ("1", "1.0"), methods=methods))
            except ValidationError:
                errors.append(_error(row_number, "联系人", "联系人字段不符合接口约定"))
        if errors:
            _invalid(errors)
        return items
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail="工作簿内容损坏，无法解析") from error
    finally:
        workbook.close()


def import_workbook(database, content):
    items = parse_workbook(content)
    with database.connect() as connection, connection:
        for contact in items:
            insert_contact(connection, contact)
    return {"imported": len(items), "errors": []}
