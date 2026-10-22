# Phạm vi kiểm chứng bản tái cấu trúc

Historical SQL-era checkpoint; superseded by [MongoDB-only acceptance](../migration/MONGODB_ONLY_ACCEPTANCE.md). SQL commands below are retired and are not current run instructions.

Các kết quả dưới đây thuộc mã mới; lịch sử V4 trong HANDOFF không phải kết quả
kiểm thử của bản tái cấu trúc. Xem receipt máy đọc trong thư mục này để biết lượt
chạy cuối cùng. Không có kết luận nghiệm thu đầy đủ toàn bộ yêu cầu sản phẩm.

## Đã thực thi tại Windows

- pytest backend: contracts, engine unit, property-based capacity, independent
  brute-force T2 check, geometry/routing, deterministic workflow, API/database,
  process worker, replay, timeout, hủy T4 thật, chống sửa snapshot và migration.
- Performance smoke T1 với 2, 10, 20 kệ; thời gian ghi ở JUnit properties. Không
  phải benchmark khả năng mở rộng hay chứng nhận latency cho dữ liệu lớn.
- TypeScript strict production build, ESLint, Vitest cho editor math.
- Playwright workflow thật với backend/database/worker: tạo/sửa/tải lại, chạy,
  xem nghiệm/planogram/mô phỏng, replay, so sánh và tải report; kiểm tra lỗi 422,
  dự án rỗng/mới nhập một phần và trạng thái worker offline.
- Viewport 1440×1000 và 390×844; kiểm tra overflow, menu mobile, keyboard focus,
  reduced motion; screenshot tại `ui/`.
- Axe WCAG A/AA trên Dashboard và Floorplan Editor; không coi đó là audit đầy đủ
  mọi route hoặc mọi yêu cầu tiếp cận của canvas. Canvas có bảng tọa độ thay thế.

## Lỗi phát hiện và đã sửa trong lượt triển khai

1. TypeScript 7 không tương thích peer range của typescript-eslint: chọn TS 6.0.3,
   pin dependency thực tế và lưu npm lock; không dùng force/legacy-peer-deps.
2. Vitest ban đầu thu nhầm Playwright spec: tách include/exclude trong config.
3. Ca trạng thái trống dùng exact text không tính đơn vị con: sửa selector theo
   nhãn completion hiển thị; không đổi dữ liệu ứng dụng để chiều test.
4. Windows sharing violation khi thay progress.json: retry PermissionError có
   giới hạn, giữ atomic publish; ca replay sau sửa đã được chạy lại.
5. T1 kiểm tra lại các cặp kệ cũ mỗi ứng viên: cache footprint và kiểm tra ứng
   viên mới; chạy lại performance 20 kệ và kiểm chứng hình học độc lập.
6. Axe phát hiện tương phản thấp ở chữ phụ: chỉnh màu và chạy lại audit.

## Chưa kiểm chứng hoặc chưa có

PostgreSQL và Docker runtime tại máy này: chưa chạy vì không có executable/service.
CI PostgreSQL + browser được cấu hình nhưng chưa push/run trên GitHub. Có thể chạy
`scripts/verify_postgres.py` với database thử nghiệm khi môi trường sẵn sàng.
Chưa có nghiệm thu môi trường sạch toàn bộ Compose; chưa có soak test, resilience
campaign, large-scale MILP/route benchmarks, nhiều worker đồng thời hoặc cross-OS
bitwise replay. Không có bằng chứng thực địa hoặc hiệu chuẩn hành vi khách.

Cảnh báo thư viện Starlette: `httpx` TestClient deprecated, không ảnh hưởng các
assertion đã chạy. Chưa đổi sang httpx2 trong bản foundation. Pytest record_property
với xunit2 được xử lý bằng cấu hình JUnit legacy để giữ dữ liệu performance.

## Kết quả cuối ngày 21/10/2026

- Backend: **42 passed**, 1 Starlette deprecation warning, 8,15 giây.
- Vitest: **4 passed**.
- Playwright: **5 passed**, 18,2 giây; gồm audit Axe trên hai màn hình.
- Ruff, mypy (45 source files), ESLint, TypeScript/Vite build, pip check và Alembic check: **PASS**.
- Snapshot recovery smoke: **283 tệp** khôi phục và kiểm tra hash; 1.403 tệp gốc bảo toàn kiểm tra SHA-256; 57.457 mục cây đã chuyển kiểm tra kích thước/đích symlink, không có mismatch.
- Receipt máy đọc: `verification-summary.json`, `preservation.json`, JUnit, Playwright JSON và UI evidence.
