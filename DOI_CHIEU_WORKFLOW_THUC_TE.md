# Đối chiếu chính xác workflow với mã hiện tại — 15/11/2026

## Kết luận

Hình có các thành phần đúng, nhưng chưa mô tả chính xác quy trình thực thi của hệ thống. Nó gần nhánh feedback có surrogate, không phải workflow chung của mọi lần chạy. Nhận định trước đây “khớp với luồng chính” chưa đủ chặt chẽ.

## Bằng chứng quan trọng

| Điểm | Cách thực thi hiện tại | Nguồn |
|---|---|---|
| Chạy mẫu qua giao diện | small_store có joint=null, candidate_count=1, slotting_algorithm=first_fit; không tự bật surrogate/feedback. | datasets/samples/small_store.json; application/workflow.py |
| V5 được đề xuất | feedback_v5: feedback, walk_heat, first_improvement, adaptive layer allocation. | 68 cấu hình trong experiments/configs/paper-v5-unlimited-parallel-20261110 |
| Khởi tạo | Chấm phương án tuần tự; khi lỗi packing/infeasible có thể thử sửa assignment có giới hạn. | application/feedback/bootstrap.py::initialize |
| Warm start | Tối đa 128 lần sinh random walk; lọc trùng/lỗi, xếp hạng bằng S rồi đánh giá tối đa 10 hoặc 8 ứng viên, tùy B=40 hoặc B=30. | coordinator.py::warm_start; cấu hình feedback_v5 |
| Pool trong vòng lặp | Lấy mẫu tối đa 96 sửa T1 hợp lệ và thử 32 compound moves; đây là giới hạn lấy mẫu/lần thử, không bảo đảm có 128 ứng viên cuối cùng. | neighborhood.py::t1_pool |
| Phạm vi surrogate | Chỉ xếp hạng pool T1. Các sửa T2/T3 không được đưa chung vào một bảng xếp hạng S toàn cục. | neighborhood.py::t1_pool, actions |
| Thứ tự đánh giá | Các hàng đợi T1/T2/T3 được trộn theo trọng số thành công thích nghi, cắt max_actions=24. First improvement dừng lượt khi gặp cải thiện đủ tolerance. | neighborhood.py::interleave; coordinator.py::optimize |
| Tầng nào thực sự giải lại | Sửa T1 bỏ assignment/placements nên giải lại T2/T3. Sửa T2 truyền assignment để replay và giải lại T3. Sửa T3 truyền placements để replay. Không phải lượt nào cũng giải lại cả hai MILP. | neighborhood.py; stage_workflow.py::_candidate; decisions.py |
| T3 và repair | V5 khai báo slotting_algorithm=milp. Repack thuộc nhánh first_fit, không phải hậu xử lý bắt buộc sau MILP. Sửa khả thi ở bootstrap là cơ chế khác. | engines/t3_slotting/engine.py; application/feedback/bootstrap.py |
| Hạ dần | Bước descent nhận khi J mới < J hiện tại - tolerance. Có tối đa 10 kick, kick_edits=3; local có thể kém đi còn best được giữ riêng. | coordinator.py::optimize, kick; cấu hình V5 |
| Phạm vi sửa T3 | t3_scope=objective: tập trung đổi mặt, swap khác mặt và tăng facings khi thiếu capacity, thay vì mọi thay đổi xếp hàng đều được thử. | neighborhood.py::actions |
| Mũi tên độ nóng | Dữ liệu từ journeys/picks của T4 qua diagnostics; không suy ra từ một số J. | diagnostics.py::analyze; surrogate.py::heat |
| Dữ liệu ngoài mẫu | Chia đơn trước tối ưu theo thời gian; số đơn giữ lại là ceil(N*0.2). Cố định quyết định best và chấm phần giữ lại, dùng bộ scenario seed của best. | splits.py; evaluation.py::with_held_out, evaluate_held_out |
| Replay | Xác minh ngay khi đánh giá ứng viên, trước khi tính score, và khi chấm phần giữ lại; không chỉ ở cuối. | feedback/evaluator.py::evaluate; experiments/validation.py::verify |

Các đường dẫn rút gọn application/ và engines/ trong bảng nằm dưới backend/src/smart_retail/.

## Workflow sát với nhánh feedback_v5

```text
Sinh dữ liệu tổng hợp và chốt snapshot/identity
    ↓
Chia đơn theo thời gian: phần đầu huấn luyện, khoảng 20% cuối giữ riêng
    ↓
Ước lượng demand từ train; thực thi qua worker
    ↓
Phương án ban đầu T1 → T2 → T3 → T4 → replay → J
    └── Nếu cần: sửa khả thi khởi tạo có giới hạn
    ↓
Warm start: tối đa 128 random walks
    → xếp hạng S → đánh giá tối đa E=10 hoặc 8 → chọn điểm bắt đầu
    ↓
Mỗi vòng:
    T4 journeys/picks → diagnostics và heat
    ├── T1: lấy mẫu ≤96 sửa đơn + thử ≤32 compound moves
    │        → lọc hình học/trùng/topology → xếp hạng S
    ├── T2: sinh reassign/swap ngành hàng
    └── T3: sinh sửa liên quan mục tiêu
              ↓
    Trộn hàng đợi theo adaptive layer allocation, lấy tối đa 24 hành động
              ↓
    Đánh giá theo thứ tự, chỉ tính lại tầng phụ thuộc / replay quyết định có sẵn
              ↓
    T4 trên scenario seeds → replay → J
              ↓
    Nhận cải thiện đầu tiên vượt tolerance; cập nhật local và best
              ↓
    Hội tụ: kick nếu còn lượt; luôn giữ best riêng
              ↓
    Lặp đến khi hết budget/thời gian hoặc điều kiện dừng
    ↓
Cố định best → chấm đơn giữ lại bằng cùng định nghĩa J và seed của best
    ↓
Record, trạng thái, lỗi, checksum, bảng và báo cáo
```

## Những phần vẫn đúng trong hình

Bốn họ mặt bằng; vai trò T1–T4; SimPy; bốn thành phần của J; surrogate dựa vào khoảng cách và heat; vòng feedback; nguyên tắc giữ best và đánh giá ngoài mẫu đều có mã tương ứng. Khác biệt nằm ở cấu hình được chọn, phạm vi áp dụng surrogate, thứ tự điều phối và các nhánh giải lại/replay.

## Phạm vi kiểm tra

Đọc mã các nhánh thực thi và toàn bộ 68 cấu hình; xuất tổng hợp cấu hình feedback_v5 vào var/workflow-precise-verification.json. Đây là đối chiếu tĩnh của checkout hiện tại, không xác nhận historical run đã dùng đúng cùng byte nguồn, không chạy campaign hoặc suy luận thêm hiệu quả khoa học. Không thay đổi source, dữ liệu hoặc thuật toán.
