# Vai trò: Xuất kết quả lần chạy sang báo cáo JSON và planogram CSV từ dữ liệu đã có.
import csv
import io
import json


# Hàm report_json: xử lý bước report json trong phạm vi module hiện tại.
def report_json(run: dict) -> str:
    return json.dumps(
        {"schema": "smart-retail-report/1", "run": run},
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )


# Hàm planogram_csv: xử lý bước planogram csv trong phạm vi module hiện tại.
def planogram_csv(run: dict) -> str:
    rows = (run.get("result") or {}).get("stages", {}).get("T3", {}).get("placements", [])
    stream = io.StringIO(newline="")
    fields = [
        "sku",
        "shelf_id",
        "level_id",
        "face",
        "x_m",
        "width_m",
        "orientation",
        "facings",
        "layers",
        "depth_units",
        "capacity_units",
        "load_kg",
    ]
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()
