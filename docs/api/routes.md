# API cục bộ

Local API `http://127.0.0.1:8010`; OpenAPI `/docs` và `/openapi.json`.
Frontend dùng `/api` qua Vite proxy hoặc nginx trong Compose.

| Method | Route | Tác dụng |
|---|---|---|
| GET | /api/health | Database, worker heartbeat và runtime identity |
| GET | /api/schemas | JSON Schema của bảy input group |
| GET/POST | /api/projects | Danh sách hoặc tạo dự án |
| GET | /api/projects/{id} | Dữ liệu đã lưu, revision và trạng thái hoàn thành |
| PUT | /api/projects/{id}/inputs/{section}?expected_revision=N | Lưu một nhóm; 409 nếu revision cũ |
| POST | /api/projects/{id}/validate | Kiểm tra đủ nhóm và tham chiếu; chưa chạy solver |
| GET/POST | /api/projects/{id}/runs | Xem hoặc enqueue workflow T1–T4 |
| GET | /api/runs/{id} | Trạng thái, snapshot, kết quả, lỗi |
| POST | /api/runs/{id}/cancel | Hủy queued ngay; chạy thì yêu cầu supervisor kết thúc child |
| POST | /api/runs/{id}/replay | Tạo run mới từ snapshot gốc, từ chối nếu runtime/source đổi |
| GET | /api/runs/{id}/report?format=json/csv | JSON truy vết đầy đủ hoặc CSV planogram |

Lỗi: 404 không tồn tại; 409 ghi đè/replay/checksum không hợp lệ; 422 vi phạm
schema/tham chiếu. Run failed giữ `error.code` và `error.message`, không trả một
phương án giả thành công. Worker lưu `input.json`, `progress.json`, `result.json`
hoặc `error.json`, cùng `receipt.json` trong thư mục run riêng ở `var/artifacts`.

Các section hợp lệ: floorplan, shelves, categories, products, demand, orders,
optimization. Giới hạn và mô hình tính toán được nêu trong docs/data và docs/modules.
