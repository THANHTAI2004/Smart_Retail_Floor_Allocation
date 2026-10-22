# Trạng thái triển khai theo yêu cầu ngày 21/10/2026

Đây là bàn giao phần đã thực hiện, chưa phải nghiệm thu toàn bộ prompt. Danh sách
tệp chính xác ở `changed-files.json`; cây thực tế ở `actual-tree.txt`. Chạy ứng dụng
bằng `scripts/start.ps1`, kiểm thử theo README. Các receipt cuối ở docs/testing.

| Phase | Trạng thái thực tế | Tệp/nhóm thay đổi | Còn thiếu |
|---|---|---|---|
| 0 Bảo vệ dữ liệu | Đã kiểm kê, snapshot toàn bộ và đọc lại SHA-256 | Snapshot ngoài dự án, migration.md, HANDOFF | Chưa restore toàn bộ 7,7 GB vào cây thử để nghiệm thu recovery toàn bộ |
| 1 Cấu trúc | Đã chuyển lõi cũ ra ngoài, tạo root frontend/backend/config/scripts/CI | Cây smart-retail-layout di chuyển nguyên vẹn; root configs | Tài liệu gốc chưa phân loại tiếp; không tự xóa |
| 2 Backend foundation | Đã chạy API, SQLite bền vững, migration, validation, queue/worker, contracts | backend/, datasets/schemas, samples | PostgreSQL runtime chưa xác minh; chưa multi-store/auth |
| 3 Frontend foundation | Đã chạy giao diện, 15 route, form/JSON import, Konva editor, lưu/tải dữ liệu | frontend/, UI evidence | Form nâng cao cho cấu trúc lồng vẫn dùng JSON; ảnh nền chưa lưu bền vững |
| 4 T1 | Baseline khả thi đã có và kiểm thử độc lập | engines/t1_layout, unit/performance | Chưa tìm tối ưu hình học, không chứng minh infeasibility của search |
| 5 T2 | MILP/greedy baseline đã có, kiểm chứng với brute force fixture nhỏ | engines/t2_allocation, unit | Chưa multi-objective/soft-affinity, chia category nhiều kệ |
| 6 T3 | Physical first-fit đã có, property/fixture | engines/t3_slotting, viewer | Chưa optimizer planogram toàn cục hoặc mọi yêu cầu đặc biệt |
| 7 T4 | Routing + synthetic simulation đã có | engines/t4_simulation, analytics | Chưa crowd dynamics, calibration, staffing/batching |
| 8 Tích hợp | Workflow worker → lưu → replay → compare → JSON/CSV đã chạy E2E | application/workers/reporting/frontend results | Chưa partial rerun/invalidation tổng quát, PDF report |
| 9 Nghiệm thu | Đã có kiểm chứng baseline cục bộ và audit cấu trúc | tests, verification receipts | Chưa clean Compose/PostgreSQL, CI live, large benchmarks hoặc full product acceptance |

Các quyết định: một aggregate JSON theo input group kết hợp orders/order_lines có
FK; SQLAlchemy chung SQLite/PostgreSQL; HiGHS qua SciPy; SimPy/NetworkX baseline;
database queue + killable process; không thêm Redis/Pyomo/pymoo khi chưa có use case.

Đầu vào còn thiếu so với prompt được liệt kê công khai trong input-contracts.md.
Mô hình bảy nhóm hiện tại không được quảng bá là hỗ trợ mọi trường chuyên sâu.
Không có mock endpoint/solver placeholder; các nút đang hiển thị đều có hành động
hoặc trạng thái disabled có lý do. Module model như Store/DisplayArea có thiết kế
domain nhưng chưa có màn hình CRUD độc lập; không đánh dấu chức năng đó hoàn tất.

## Việc tiếp theo

1. Cung cấp môi trường PostgreSQL/Docker và chạy migration + workflow/replay/queue
   tests trên database đó, rồi khởi động Compose từ môi trường sạch.
2. Chốt hợp đồng mở rộng: nhiều cửa/tường/cột/vùng cấm có metadata, capacity/special
   conditions, correlation mềm, nhu cầu theo giờ và operational staffing.
3. Mở rộng editor có undo/redo, lưu ảnh hiệu chuẩn và form có cấu trúc cho levels,
   baskets/order lines; thêm E2E cho polygon drawing/drag/rotation bằng chuột.
4. Thay T1/T3 baseline khi có objective và fixture chấp nhận; mở T2 soft constraints,
   Pareto search và orchestration nhiều mục tiêu có normalization.
5. Nâng simulation theo dữ liệu thực, lưu partial artifacts theo tầng, rerun routing
   và chiến dịch benchmark/research có protocol.
