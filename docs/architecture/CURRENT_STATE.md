# Trạng thái hệ thống ngày 23/10/2026

Ứng dụng nằm trực tiếp trong `frontend/` và `backend/`. React/TypeScript gọi
FastAPI; application services điều phối domain và engines; infrastructure triển
khai MongoDB/PyMongo đồng bộ. Công việc số học chạy bằng process con do worker
giám sát. MongoDB lưu project aggregate, hàng đợi, kết quả và heartbeat; GridFS
lưu payload vượt ngưỡng BSON. Không có service database thay thế trong Compose.

T1 có grid/local search và kiểm tra hình học/topology. T2 có greedy/MILP và
replay độc lập. T3 có first-fit/MILP strip-packing và kiểm tra vật lý. T4 dùng
đồ thị di chuyển, routing và SimPy với hàng đợi tại kệ. Application hỗ trợ
sequential, multistart, feedback, exact và hybrid; chứng minh chỉ có hiệu lực
trong miền hữu hạn, trên các seed và mục tiêu đã khai báo.

Kết quả audit ngày 22/10/2026: 178 pytest ở mỗi đường dẫn dài/ngắn, 4 Vitest,
10 Playwright trong phạm vi tổng hợp xác định. Đây là kết quả lịch sử, không
phải kiểm thử lại cho các thay đổi tài liệu và công cụ ngày 23/10/2026.
Xem [audit](../system-audit/FINAL_SYSTEM_AUDIT.md) và
[README](../../README.md) để biết giới hạn và quy trình kiểm chứng hiện hành.

Tài liệu lịch sử không còn dùng để hướng dẫn vận hành được giữ nguyên ngoài
dự án theo [hồ sơ lưu trữ](HISTORICAL_ARCHIVE.md).
