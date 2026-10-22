# Nghiệm thu MongoDB-only — 22/10/2026

**MONGODB_ONLY_VERIFIED.** Theo yêu cầu mới, đã gỡ SQLite/SQLAlchemy khỏi source,
dependency và database trong checkout. MongoDB là persistence duy nhất của ứng
dụng và experiment runner; backup/restore hiện tại cũng dùng BSON MongoDB.

## Phần đã gỡ

- Database ứng dụng SQLite và 32 `campaign.db` cũ; database thử nghiệm cũ.
- Alembic config/migrations, script xác minh PostgreSQL.
- Công cụ import SQLite và ba test chỉ dành cho quá trình chuyển đổi đã hoàn tất.
- SQLAlchemy, Alembic, psycopg, psycopg-binary và Mako khỏi `.venv` chính và môi
  trường thí nghiệm Python cũ. Không còn SQL driver trong dependency lock.
- Hướng dẫn rollback SQL trong checkout; thay bằng backup/restore MongoDB.
- Cache SQLite của mypy; cấu hình mypy dùng filesystem để không tạo lại file này.

Không sửa thư viện chuẩn của Python hoặc cài đặt hệ thống. Guard test xác nhận
source ứng dụng không import `sqlite3`/SQLAlchemy/Alembic/SQL drivers/Motor và
project venv không cài các package persistence đã loại bỏ.

## Bảo toàn dữ liệu trước khi xóa

Archive ngoài repository:
`C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-only-01`.

522 file database/source/cache được đọc lại đối chiếu SHA-256 trước khi gỡ;
64 file WAL/SHM phát sinh khi đọc dữ liệu cũ cũng được archive, xác minh rồi gỡ.
Bytecode SQL cũ được loại bỏ. Bản SQL phục hồi bên ngoài repository vẫn được
giữ nguyên, không có runtime nào trong ứng dụng sử dụng chúng.

34 database ứng dụng/campaign đã được giải mã thành 206 bảng document MongoDB
trong `smart_retail_history`. Mỗi bảng có số dòng, checksum, source identity và
readback kiểm tra. Payload lớn dùng GridFS; không lưu file SQLite làm backend.
Archive này tách khỏi queue đang hoạt động. JSON/artifact/manifest nghiên cứu
được giữ nguyên; fingerprint khoa học không bị sửa để thích nghi với database mới.

Receipt: [manifest gỡ SQL](mongodb-only-removal.json),
[khôi phục lịch sử MongoDB](mongodb-only-history-restore.json).

## Kiểm chứng mới

| Kiểm tra | Kết quả |
|---|---|
| Backend pytest | 165 PASS, không skip integration |
| Vitest | 4 PASS |
| Playwright với MongoDB thật | 9 PASS |
| Ruff, mypy, pip check, ESLint, build, npm audit, kiến trúc | PASS |
| Pilot T1–T4 trên source MongoDB-only | 19/19 thành công |
| Replay pilot mới | 19/19 khớp input SHA, result SHA và số liệu |
| Backup/restore BSON dữ liệu chính | PASS; 16 project, 8 run, mọi document bằng nhau |
| Backup/restore lịch sử | PASS; 34 database nguồn, 206 bảng, mọi document bằng nhau |
| Các kiểm soát backup | GridFS, số nguyên chính xác, indexes, archive hỏng, từ chối ghi đè target |
| Quét checkout sau gỡ | Không còn database SQLite/WAL/SHM |

Release: [verification.json](evidence/20261022-mongodb-only-release-01/verification.json).
Receipt backup chính: [mongodb-only-native-restore.json](mongodb-only-native-restore.json).
Pilot/replay: `experiments/results/20261022-mongodb-only-{pilot,replay}-01`;
đối chiếu: `experiments/reports/20261022-mongodb-only-comparison-01.json`.
Tổng kiểm chứng: [mongodb-only-closeout.json](mongodb-only-closeout.json).

Test migration SQL trước đây được loại bỏ cùng importer. Bộ test mới bổ sung
backup/restore MongoDB và guard chống đưa lại SQL; số test mới không được suy từ
receipt cũ. Một cảnh báo deprecation Starlette/httpx vẫn còn, các assertion PASS.

## Vận hành

API/worker/frontend đã khởi động lại trên source MongoDB-only:
http://127.0.0.1:5173/#research. Database chính: `smart_retail`.
Tất cả dữ liệu gốc đã chuyển vẫn có 16 project và 8 run.

Backup hiện tại yêu cầu dừng toàn bộ writer; chưa phải online point-in-time backup.
Xem [hướng dẫn BSON/GridFS](MONGODB_BACKUP_RESTORE.md). Docker/Compose, Atlas và
remote CI vẫn chưa được chạy kiểm chứng trên máy này. Các receipt SQLite trước
đây là bằng chứng lịch sử. Thay đổi gỡ SQL chưa được stage/commit/push.
