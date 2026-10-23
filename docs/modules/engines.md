> Current 2026-10-22 additions: seven-section schema 1.1 and explicit migration; exits/zones/connectivity; category soft affinity; SKU facing bounds and shelf compatibility; piecewise arrivals, finite picker pools and nearest/return/exact small-tour routing; persistent content-keyed stage cache and standalone stage execution. See [external historical archive](../architecture/HISTORICAL_ARCHIVE.md) and [reproduction guide](../research/HOW_TO_RUN_EXPERIMENTS.md). Earlier baseline descriptions below are retained for context.

# T1–T4: trách nhiệm, hợp đồng và mức thực hiện

Các API dưới đây nhận dataclass từ `smart_retail.domain.models`; không cần HTTP
hoặc database để chạy độc lập. Mỗi engine có fixture nhỏ trong `backend/tests/unit`.

| Tầng | Python API | Đầu vào → đầu ra | Trạng thái và giới hạn |
|---|---|---|---|
| T1 | `engines.t1_layout.engine.solve` | Floorplan, shelves, mode → LayoutSolution | Fixed validation hoặc constructive grid baseline; không chứng minh vị trí tối ưu |
| T2 | `engines.t2_allocation.engine.solve` | Floorplan, placed shelves, categories → assignment/objective/status | HiGHS MILP hoặc greedy; capacity, fixed_shelf, near/separate; MILP có independent constraint replay |
| T3 | `engines.t3_slotting.engine.solve` | shelves, products, assignment, algorithm/deadline → Planogram | First-fit hoặc HiGHS finite strip MILP; physical replay độc lập |
| T4 | `engines.t4_simulation.engine.solve` | Dataset, placed shelves, assignment, optional Planogram → SimulationResult | Grid routing đúng mặt SKU, entrance connectors, route points/pick quantities; SimPy shelf queue |

## T1 — Geometry & Layout

Kiểm tra polygon bằng Shapely. Kệ phải nằm trong biên, cách biên/vật cản/cửa/kệ
khác ít nhất `min_aisle_m`. Đây là mô hình bảo thủ: cũng yêu cầu lối đi quanh mép
kệ. Kệ locked giữ nguyên, các kệ khác được xét theo diện tích giảm dần, tọa độ lưới
và góc 0/90. Hết ứng viên là `SEARCH_EXHAUSTED`, không phải bằng chứng infeasible.
`violations()` có thể gọi độc lập để kiểm chứng nghiệm. Chưa có tối ưu đa mục tiêu
hình học, lối đi trung tâm có loại riêng, cửa nhiều loại hay kiểm chứng egress.

## T2 — Category Allocation

Mỗi ngành hàng chọn đúng một kệ; nhiều ngành hàng có thể dùng chung kệ trong giới
hạn tổng chiều rộng các tầng × số mặt. `near` và `separate` là ràng buộc cứng giữa
tâm kệ, với ngưỡng của ngành hàng khai báo. `fixed_shelf_id` là ràng buộc phân bổ.

Objective hiện tại: tổng khoảng cách Euclid từ cửa đến tâm kệ, chia đường chéo
mặt bằng, với trọng số demand × priority chia tổng demand × priority. Giá trị
không có đơn vị. `distance_weight` là hệ số dương chung nên không thay thứ tự
nghiệm; chưa kết hợp objective khác (`capacity_weight` phải bằng 0). Đây không
phải tổng chi phí vận hành T1–T4 và không phải khoảng cách tuyến đi thực T4.

MILP hỗ trợ tối đa 20.000 biến nhị phân và 200.000 cặp cấm. `OPTIMAL` chỉ khi
solver xác nhận; `FEASIBLE_TIME_LIMIT` khi có incumbent hợp lệ; `INFEASIBLE` chỉ
khi solver chứng minh. Greedy thất bại trả `SEARCH_EXHAUSTED`. Chưa có affinity
mềm, chia một ngành hàng trên nhiều kệ hoặc Pareto optimizer.

## T3 — Product Slotting & Planogram

`algorithm="milp"` chọn mô hình option hữu hạn: một khối/SKU, facings cố định,
orientation hợp lệ, số hàng/lớp có thể giảm để giữ tải chung của tầng. Maximize tổng
demand × capacity. OPTIMAL/INFEASIBLE chỉ áp dụng mô hình strip này; quá 20.000
option trả PROBLEM_LIMIT. `algorithm="first_fit"` giữ baseline. Cả hai chạy replay
độc lập dimensions/load/capacity/overlap. T4 nhận planogram để ánh xạ đúng mặt lấy
hàng. Chi tiết tại [công thức nghiên cứu](../research/MATHEMATICAL_FORMULATION.md).

Từng SKU được đặt trọn các facing trên một tầng/mặt kệ. Thuật toán thử các hướng
cho phép, tính số hàng sâu/lớp theo kích thước hữu dụng và khoảng hở, cộng tải trọng
hai mặt của cùng tầng. Kết quả có tọa độ x, rộng, orientation, facings, layers,
depth_units, capacity_units và load_kg. Mọi SKU phải được xếp; nếu không thì
`SLOTTING_FAILED` và không chạy T4. Đây là thất bại first-fit, chưa chứng minh
bài toán vật lý vô nghiệm. Chưa tách một SKU qua nhiều tầng hoặc tối ưu doanh thu.

## T4 — Customer & Picker Operations

Các ô đi được nằm trong polygon và tránh kệ/vật cản; cạnh lưới được kiểm tra
LineString để không cắt vật cản. Mỗi kệ cần mặt phục vụ nối tới cửa. Routing dùng
shortest path trên lưới 4 hướng, ghé kệ gần nhất tiếp theo rồi quay về cửa.
Tối đa 40.000 ô. Khoảng cách/collision chính xác chỉ ở độ phân giải lưới đã chọn.

Khách đến theo Poisson đến horizon_s, giỏ hàng từ mẫu hoặc nhu cầu SKU; seed
xác định. Đơn đến theo timestamp tương đối so với đơn đầu tiên; dwell nhân quantity.
Các hành trình đã nhận được xử lý hết, nên simulation_end_s có thể vượt horizon_s.
Mọi đơn có picker đồng thời; chưa có giới hạn đội ngũ picker, batching hoặc ca làm.

Congestion hiện chỉ là hàng đợi một server tại mỗi kệ, không phải xung đột người
đi bộ trong hành lang. Điểm phục vụ theo mặt kệ của SKU trong planogram; chưa xét
độ cao hoặc vị trí x riêng trên mặt kệ. KPI gồm completed journeys, khoảng cách
và chờ trung bình, đơn trễ. Route có points_m và quantities để replay độc lập;
quãng đường tính cả hai đoạn nối cửa với lưới.
Chưa mô phỏng depletion tồn kho, bổ sung hàng, khách bỏ giỏ hoặc hành vi hiệu chuẩn.

## Workflow và test

`application.workflow.execute(sections)` điều phối T1→T4 theo một ngân sách wall
time. Worker chạy trong process con, kiểm tra hủy và timeout từ process cha. Một
candidate thất bại được giữ trong kết quả nếu có candidate khác hoàn thành. Với
1 candidate, thất bại kết thúc run. Có tối đa 8 candidate dùng chung wall budget,
score chuẩn hóa route/wait/stock và cache nội bộ theo hash phụ thuộc. Chưa có
generic partial rerun, cache bền vững hoặc router tái chạy từng tầng.

```powershell
.venv\Scripts\python.exe -m pytest backend/tests/unit/test_engines.py -q
.venv\Scripts\python.exe -m pytest backend/tests/regression/test_workflow.py -q
.venv\Scripts\python.exe -m pytest backend/tests/performance/test_baseline.py -q
```
