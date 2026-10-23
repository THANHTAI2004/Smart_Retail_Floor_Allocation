# ADR 0001 — Modular monolith và công việc theo process

Trạng thái hiện hành ngày 23/10/2026: React/TypeScript/Vite/Konva;
FastAPI/Pydantic; MongoDB với PyMongo đồng bộ. Application điều phối engines;
domain và engines không phụ thuộc HTTP hoặc persistence.

Hàng đợi dùng MongoDB atomic claim, lease và fencing. Worker tạo process con
để kiểm soát thời gian, bộ nhớ và hủy công việc. Mỗi run sở hữu input snapshot,
runtime identity và checksum. Không chạy số học dài trong HTTP request.

T2/T3 dùng HiGHS qua SciPy; T1 dùng Shapely; T4 dùng NetworkX/SimPy.
Phân biệt nghiệm khả thi, nghiệm tối ưu trong mô hình, search thất bại và vô
nghiệm đã chứng minh. Hàm mục tiêu liên tầng do application quyết định.
