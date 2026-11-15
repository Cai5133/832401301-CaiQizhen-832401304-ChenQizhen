"""Run from backend/: python scripts/generate_samples.py."""
from io import BytesIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from openpyxl import load_workbook
from app.services.excel import build_workbook, sample_contacts


def main():
    output = Path(__file__).resolve().parents[2] / "samples"
    invalid = output / "invalid"
    invalid.mkdir(parents=True, exist_ok=True)
    template = build_workbook(sample_contacts())
    (output / "template.xlsx").write_bytes(template)
    normal = sample_contacts() + [
        {"name": "同名示例", "isFavorite": False, "methods": [{"type": "phone", "value": "01000000000"}]},
        {"name": "同名示例", "isFavorite": True, "methods": [{"type": "email", "value": "sample@example.org"}]},
        {"name": "无方式示例", "isFavorite": False, "methods": []}]
    (output / "normal.xlsx").write_bytes(build_workbook(normal))
    changes = {"missing-header.xlsx": ("C1", "错误电话列"),
               "invalid-favorite.xlsx": ("B2", 2),
               "invalid-json.xlsx": ("C2", "[123]"),
               "empty-name.xlsx": ("A2", " "),
               "formula.xlsx": ("A2", "=1+1")}
    for filename, (cell, value) in changes.items():
        workbook = load_workbook(BytesIO(template))
        workbook.active[cell] = value
        workbook.save(invalid / filename)
        workbook.close()
    (invalid / "corrupt.xlsx").write_bytes(b"not an Excel workbook")
    print("Generated template, normal data and six invalid fixtures")


if __name__ == "__main__":
    main()
