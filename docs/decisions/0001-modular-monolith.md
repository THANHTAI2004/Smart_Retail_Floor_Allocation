# ADR 0001 — Một ứng dụng ở root, modular monolith và job theo process

Trạng thái: được triển khai ngày 21/10/2026 theo yêu cầu người dùng.

Quyết định dùng React/TypeScript/Vite/Konva; FastAPI/Pydantic; SQLAlchemy/Alembic;
PostgreSQL cho Compose/CI, SQLite file cho môi trường Windows chưa có PostgreSQL.
Hai database dùng chung migration và repository; chưa coi kiểm thử SQLite là bằng
chứng thực thi PostgreSQL.

T2 chọn `scipy.optimize.milp` với HiGHS đi kèm SciPy. Chưa thêm Pyomo vì baseline
chưa cần lớp mô hình thứ hai. Chưa thêm pymoo vì chưa thực hiện Pareto search.
T1 dùng Shapely; T4 dùng NetworkX/SimPy. Mỗi giải pháp này có dependency thực tế.

Queue dùng database và tiến trình con thay vì thêm Redis/Celery ở giai đoạn đầu.
Điều này cho phép hủy thật, hard timeout và tách số học khỏi request thread.
Trạng thái run và snapshot sống qua việc khởi động lại API. Các job đã claim khi
supervisor chết được đánh dấu hết lease sau 360 giây; không tự thực thi lại vì
không được suy đoán một job đang tính đã chết.

Engine trả trạng thái riêng: nghiệm MILP tối ưu, incumbent khi hết thời gian,
heuristic khả thi, search chưa tìm được và infeasible đã chứng minh. Objective T2
không được mô tả là tổng tối ưu T1–T4. Khi thêm objective, phải có đơn vị, normalization,
trọng số và fixture kiểm chứng độc lập trước khi chấp nhận cấu hình mới.
