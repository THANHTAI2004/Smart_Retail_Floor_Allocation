# Vai trò: Nhập và xuất CSV cho dữ liệu dạng bảng, giữ trường lồng nhau bằng ô JSON để có thể khôi phục đầy đủ.
"""Lossless CSV import/export for tabular sections, including nested JSON cells."""

import csv
import io
import json

from smart_retail.contracts.inputs import SECTIONS

TABLES = {"shelves": "items", "categories": "items", "products": "items", "orders": "order_lines"}


# Hàm export_csv: xuất csv theo quy tắc trong thân hàm.
def export_csv(section: str, payload: dict) -> str:
    if section not in TABLES:
        raise ValueError("This section is not a supported table")
    normalized = SECTIONS[section].model_validate(payload).model_dump(mode="json")
    table = TABLES[section]
    stream = io.StringIO(newline="")
    columns = sorted({key for row in normalized[table] for key in row})
    writer = csv.DictWriter(stream, ["_metadata", *columns])
    writer.writeheader()
    # Metadata preserves layout mode and parent orders, even for an empty table.
    writer.writerow(
        {
            "_metadata": json.dumps(
                {k: v for k, v in normalized.items() if k != table}, ensure_ascii=True
            )
        }
    )
    for row in normalized[table]:
        writer.writerow({k: json.dumps(v, ensure_ascii=True) for k, v in row.items()})
    return stream.getvalue()


# Hàm import_csv: nhập csv theo quy tắc trong thân hàm.
def import_csv(section: str, text: str) -> dict:
    if section not in TABLES or len(text.encode("utf-8")) > 10_000_000:
        raise ValueError("Unsupported table or file exceeds 10 MB")
    reader = csv.DictReader(io.StringIO(text))
    first = next(reader, None)
    if first is None or not first.get("_metadata"):
        raise ValueError("CSV must start with a metadata record from the table exporter")
    metadata = json.loads(first["_metadata"])
    if not isinstance(metadata, dict):
        raise ValueError("CSV metadata must be an object")
    rows = []
    for row in reader:
        if None in row or row.get("_metadata"):
            raise ValueError("Malformed CSV row")
        rows.append(
            {
                key: json.loads(value)
                for key, value in row.items()
                if key != "_metadata" and value != ""
            }
        )
    return (
        SECTIONS[section]
        .model_validate({**metadata, TABLES[section]: rows})
        .model_dump(mode="json")
    )
