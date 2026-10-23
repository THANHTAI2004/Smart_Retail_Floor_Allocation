> Current 2026-10-22 additions: seven-section schema 1.1 and explicit migration; exits/zones/connectivity; category soft affinity; SKU facing bounds and shelf compatibility; piecewise arrivals, finite picker pools and nearest/return/exact small-tour routing; persistent content-keyed stage cache and standalone stage execution. See [external historical archive](../architecture/HISTORICAL_ARCHIVE.md) and [reproduction guide](../research/HOW_TO_RUN_EXPERIMENTS.md). Earlier baseline descriptions below are retained for context.

# Bảy nhóm dữ liệu đầu vào

Schema máy đọc: `datasets/schemas/*.schema.json`; API `GET /api/schemas`.
Fixture hợp lệ đầy đủ: `datasets/samples/small_store.json`. Fixture lỗi theo từng
nhóm: `datasets/samples/invalid_inputs.json`. Các trường lạ bị từ chối; NaN/Infinity
không hợp lệ. Thông báo lỗi HTTP 422 có đường dẫn trường và nội dung cụ thể.

| Nhóm | Nội dung và đơn vị | Kiểm tra chính |
|---|---|---|
| floorplan | Polygon boundary, entrance, polygon obstacles; m, m²; grid_m | Polygon đơn, diện tích dương ≤10.000 m², cửa và vật cản trong biên |
| shelves | items, kích thước m, levels hữu dụng, max_load_kg, faces 1/2, rotation 0/90 | Mã duy nhất; kích thước/tải dương; tầng nằm trong kích thước kệ; tổng chiều cao tầng không vượt kệ |
| categories | demand, priority, required_width_m, fixed_shelf_id, near/separate/distance_m | Tham chiếu đúng; near và separate không mâu thuẫn; yêu cầu chiều rộng dương |
| products | SKU/category, chiều rộng/sâu/cao m, kg, demand, facings, orientations, stack_layers, clearance_m | SKU duy nhất; category tồn tại; hướng 0/90; facing/layers nguyên dương |
| demand | arrivals_per_hour, horizon_s, customers, SKU baskets, behavior | Số lượng không âm, tốc độ dương, giỏ hàng chỉ có SKU tồn tại |
| orders | orders: ID/timestamp có múi giờ/kind/due_s; order_lines: order_id/SKU/quantity | FK và khóa ghép; không có đơn rỗng; quantity nguyên dương |
| optimization | seed, time_limit_s, max_iterations, algorithm, distance_weight, slotting_algorithm, candidate_count, travel/wait/stock_weight | T2 milp/greedy, T3 first_fit/milp; 1–8 candidate; budget (0,300]s dùng chung; trọng số không âm, ít nhất một trọng số liên tầng dương |

Fixed layout bắt buộc mọi kệ có x/y. Optimizable không yêu cầu x/y; kệ locked cần
có vị trí. x/y là góc trên trái của footprint trong hệ tọa độ y hướng xuống; cho
phép tọa độ âm nếu polygon tương ứng. Vị trí chưa cung cấp không được diễn giải
thành nghiệm (0,0).

Lưu từng nhóm không bắt buộc nhập lại các nhóm khác. Chỉnh/xóa mã đang được dữ
liệu khác tham chiếu bị từ chối; cần chỉnh dữ liệu phụ thuộc trước. Kiểm tra đầy
đủ trước enqueue còn yêu cầu tối thiểu một kệ, một ngành hàng và một sản phẩm.
Validation dữ liệu không đồng nghĩa đã có nghiệm: T1 kiểm tra hình học/clearance,
T2/T3/T4 tiếp tục kiểm tra ràng buộc chuyên biệt lúc chạy.

T3: mỗi facing dùng `product_width + clearance_m`; số hàng sâu và số lớp là phần
nguyên của kích thước hữu dụng chia kích thước sản phẩm cộng clearance. Tải trọng
tính theo toàn bộ sức chứa của placement, cộng chung hai mặt trên cùng tầng.
Chưa có bổ sung tồn kho hoặc depletion trong T4; sức chứa là giới hạn vật lý.

First-fit lấy số hàng/lớp tối đa cho orientation đang xét. MILP liệt kê mọi số
hàng/lớp hợp lệ, chọn đúng một khối cho mỗi SKU, tối đa hóa tổng demand × capacity
dưới ràng buộc chiều rộng từng tầng/mặt và tải chung mọi mặt cùng tầng. Quá 20.000
option trả PROBLEM_LIMIT. OPTIMAL/INFEASIBLE chỉ áp dụng mô hình strip với facings
cố định, không phải tối ưu planogram vật lý tổng quát. Xem công thức tại
[hồ sơ nghiên cứu](../research/MATHEMATICAL_FORMULATION.md).

Mô hình hành vi duy nhất hiện tại là `synthetic_basket`; không nhận đầu vào rồi
âm thầm coi là hành trình thực. Ảnh nền editor chỉ là tham chiếu trong phiên,
chỉ hiển thị sau khi nhập chiều rộng thực đã đo; chưa lưu ảnh vào database.

## Chưa có trong hợp đồng hiện tại

CAD/DXF import, nhiều cửa/tường/cột có loại riêng, vùng chức năng có metadata,
các điều kiện nhiệt độ/trưng bày đặc biệt, ma trận affinity mềm, lịch nhu cầu theo
giờ, mô hình thực nghiệm hiệu chuẩn, solver khác, Pareto objectives và memory quota.
Chưa dùng trường tự do để giả vờ hỗ trợ chúng. Các trường này cần hợp đồng và
engine tương ứng ở những bước tiếp theo.
