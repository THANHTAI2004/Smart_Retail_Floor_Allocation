# Nhóm mã nguồn tương ứng từng khối trong sơ đồ nghiên cứu

Đối chiếu trực tiếp mã nguồn và cấu hình tại `D:\Smart_Retail_Floor_Allocation`, ngày **15/11/2026**.

Tài liệu này tách **nhóm tham chiếu mã nguồn** theo chín ô của ảnh bạn gửi. Các file giữ nguyên vị trí; một file dùng chung có thể xuất hiện trong nhiều nhóm. Không liệt kê mã unit test/E2E, thư viện cài đặt, cache hoặc artifact lịch sử.

## Bản đồ nhanh

| Khối trong ảnh | Nhóm mã chính | Điểm vào quan trọng |
|---|---|---|
| 1. Bộ dữ liệu tổng hợp — bốn họ mặt bằng | `backend/src/smart_retail/application/experiments/generators.py` | [generate](backend/src/smart_retail/application/experiments/generators.py#L30) |
| 2. T1 — Bố trí kệ | `backend/src/smart_retail/engines/t1_layout/engine.py` | [solve](backend/src/smart_retail/engines/t1_layout/engine.py#L18) |
| 3. T2 — Phân bổ ngành hàng bằng MILP | `backend/src/smart_retail/engines/t2_allocation/engine.py` | [solve](backend/src/smart_retail/engines/t2_allocation/engine.py#L17) |
| 4. T3 — Xếp vị trí SKU | `backend/src/smart_retail/engines/t3_slotting/engine.py` | [solve](backend/src/smart_retail/engines/t3_slotting/engine.py#L21) |
| 5. T4 — Mô phỏng SimPy | `backend/src/smart_retail/engines/t4_simulation/engine.py` | [solve](backend/src/smart_retail/engines/t4_simulation/engine.py#L38) |
| 6. Hàm mục tiêu J trên các kịch bản huấn luyện | `backend/src/smart_retail/application/feedback/evaluator.py` | [score](backend/src/smart_retail/application/feedback/evaluator.py#L29) |
| 7. Mô hình thay thế S(p) — Quãng đường × độ nóng | `backend/src/smart_retail/application/feedback/surrogate.py` | [heat](backend/src/smart_retail/application/feedback/surrogate.py#L17) |
| 8. Tìm kiếm phản hồi có mô hình thay thế | `backend/src/smart_retail/application/feedback/coordinator.py` | [optimize](backend/src/smart_retail/application/feedback/coordinator.py#L102) |
| 9. Phương án tốt nhất — Replay độc lập và tập giữ lại theo thời gian | `backend/src/smart_retail/application/experiments/splits.py` | [split_orders](backend/src/smart_retail/application/experiments/splits.py#L50) |

## Luồng liên kết giữa các nhóm

```text
Dữ liệu tổng hợp + chia đơn theo thời gian trước tìm kiếm
    ├── Phần huấn luyện → T1 → T2 → T3 → T4 → replay → J
    │                                      └→ diagnostics/heat
    │                                           ↓
    │    sinh ứng viên ← phản hồi ← xếp hạng S(p)
    │          └→ chạy lại các tầng phụ thuộc → replay/J → cập nhật local/best
    └── Phần giữ lại cuối kỳ → cố định best → mô phỏng/replay → kết quả ngoài mẫu
```

Sơ đồ luồng này làm rõ hai ranh giới trong ảnh: tập đơn giữ lại được tách trước vòng tối ưu, và thông tin độ nóng lấy từ dữ liệu hành trình mô phỏng.

## 1. Bộ dữ liệu tổng hợp — bốn họ mặt bằng

**Khối trong ảnh:** Ô dữ liệu ở trên cùng.

**Đầu vào:** DatasetSpec, seed sinh dữ liệu, scale, layout_family và các tham số sản phẩm/đơn hàng.

**Đầu ra:** Bộ đầu vào gồm floorplan, shelves, categories, products, demand, orders, optimization; manifest mô tả nguồn gốc và checksum.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   └── experiments/
            │       └── generators.py  # Sinh dữ liệu và áp dụng override treatment.
            ├── contracts/
            │   ├── experiments.py  # DatasetSpec/CampaignSpec và giao thức chia tập của thiết kế.
            │   └── inputs.py  # Xác thực bảy nhóm đầu vào và chuyển sang domain.
            └── domain/
                ├── categories/
                │   └── models.py  # Ngành hàng, nhu cầu, quan hệ và điều kiện phân bổ.
                ├── demand/
                │   └── models.py  # Tải, hành vi và kết quả mô phỏng.
                ├── floorplan/
                │   └── models.py  # Mô hình mặt bằng, vùng chức năng và nghiệm bố trí.
                ├── orders/
                │   └── models.py  # Đơn hàng và dòng SKU/quantity.
                ├── products/
                │   └── models.py  # SKU, kích thước và kết quả planogram.
                ├── shelves/
                │   └── models.py  # Kích thước, tầng kệ, số mặt và vị trí.
                └── workspace.py  # Gom đầu vào domain thành RetailDataset.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/application/experiments/generators.py` | [generate](backend/src/smart_retail/application/experiments/generators.py#L30), [merge](backend/src/smart_retail/application/experiments/generators.py#L226) |
| `backend/src/smart_retail/contracts/experiments.py` | [DatasetSpec](backend/src/smart_retail/contracts/experiments.py#L12), [EvaluationSpec](backend/src/smart_retail/contracts/experiments.py#L53), [CampaignSpec](backend/src/smart_retail/contracts/experiments.py#L119) |
| `backend/src/smart_retail/contracts/inputs.py` | [to_domain](backend/src/smart_retail/contracts/inputs.py#L379), [validate_references](backend/src/smart_retail/contracts/inputs.py#L351) |
| `backend/src/smart_retail/domain/workspace.py` | [RetailDataset](backend/src/smart_retail/domain/workspace.py#L15) |
| `backend/src/smart_retail/domain/floorplan/models.py` | [Floorplan](backend/src/smart_retail/domain/floorplan/models.py#L19), [LayoutSolution](backend/src/smart_retail/domain/floorplan/models.py#L32) |
| `backend/src/smart_retail/domain/shelves/models.py` | [Shelf](backend/src/smart_retail/domain/shelves/models.py#L18), [ShelfLevel](backend/src/smart_retail/domain/shelves/models.py#L9) |
| `backend/src/smart_retail/domain/categories/models.py` | [Category](backend/src/smart_retail/domain/categories/models.py#L9) |
| `backend/src/smart_retail/domain/products/models.py` | [Product](backend/src/smart_retail/domain/products/models.py#L9), [Planogram](backend/src/smart_retail/domain/products/models.py#L28) |
| `backend/src/smart_retail/domain/orders/models.py` | [Order](backend/src/smart_retail/domain/orders/models.py#L9), [OrderLine](backend/src/smart_retail/domain/orders/models.py#L17) |
| `backend/src/smart_retail/domain/demand/models.py` | [DemandProfile](backend/src/smart_retail/domain/demand/models.py#L23), [SimulationResult](backend/src/smart_retail/domain/demand/models.py#L35) |

### Cách hiểu đúng so với ảnh

- Bốn giá trị layout_family đang được hợp đồng chấp nhận là grid, corner_entrance, wide và columns. Generator mặc định dùng grid nếu không truyền họ mặt bằng.
- Nguồn là dữ liệu SYNTHETIC có seed; không trình bày chúng như dữ liệu quan sát từ cửa hàng thật.
- Cấu hình khai báo dữ liệu dùng cho Paper V5 nằm trong experiments/configs/paper-v5-unlimited-parallel-20261110; phần cấu hình cụ thể được chỉ ra ở cuối tài liệu.

## 2. T1 — Bố trí kệ

**Khối trong ảnh:** Ô T1 bố trí kệ.

**Đầu vào:** Mặt bằng, vật cản, kệ, chế độ bố trí và/hoặc poses do tìm kiếm cung cấp.

**Đầu ra:** Danh sách kệ có tọa độ x/y, góc quay và trạng thái đáp ứng ràng buộc hình học.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   ├── decisions.py  # Phát lại poses cụ thể do joint search đề xuất.
            │   └── stage_workflow.py  # Điều phối T1 và cache theo đầu vào tầng.
            └── engines/
                ├── t1_layout/
                │   ├── engine.py  # Điểm vào giải T1 và xử lý chế độ bố trí.
                │   ├── geometry.py  # Footprint, ngoài biên, chồng lấn và khoảng trống.
                │   └── search.py  # Cải thiện bố trí bằng tìm kiếm lân cận có giới hạn.
                └── navigation.py  # Kiểm tra topology và đồ thị đi được dùng chung.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/engines/t1_layout/engine.py` | [solve](backend/src/smart_retail/engines/t1_layout/engine.py#L18) |
| `backend/src/smart_retail/engines/t1_layout/geometry.py` | [footprint](backend/src/smart_retail/engines/t1_layout/geometry.py#L10), [violations](backend/src/smart_retail/engines/t1_layout/geometry.py#L20) |
| `backend/src/smart_retail/engines/t1_layout/search.py` | [objective](backend/src/smart_retail/engines/t1_layout/search.py#L16), [improve](backend/src/smart_retail/engines/t1_layout/search.py#L24) |
| `backend/src/smart_retail/engines/navigation.py` | [navigation](backend/src/smart_retail/engines/navigation.py#L17), [validate_topology](backend/src/smart_retail/engines/navigation.py#L116) |
| `backend/src/smart_retail/application/decisions.py` | [decided_layout](backend/src/smart_retail/application/decisions.py#L14) |
| `backend/src/smart_retail/application/stage_workflow.py` | [_candidate](backend/src/smart_retail/application/stage_workflow.py#L40) |

### Cách hiểu đúng so với ảnh

- Trong bộ V5, layout_mode=fixed mô tả bố trí đầu vào. Vòng joint vẫn có thể truyền poses mới cho kệ không locked; không diễn giải fixed thành cấm mọi thay đổi vị trí.
- Ràng buộc hình học và topology được kiểm tra trước khi phương án được dùng tiếp. Engine T1 không tự chọn toàn bộ workflow T1–T4.

## 3. T2 — Phân bổ ngành hàng bằng MILP

**Khối trong ảnh:** Ô T2 phân bổ ngành hàng (MILP).

**Đầu vào:** Bố trí kệ hợp lệ, ngành hàng, nhu cầu, chiều rộng cần dùng, kệ cố định và quan hệ gần/tách/affinity.

**Đầu ra:** Assignment ánh xạ ngành hàng sang kệ, mục tiêu T2 và trạng thái solver.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   ├── decisions.py  # Áp dụng assignment được chọn hoặc đề xuất sửa.
            │   └── stage_workflow.py  # Truyền kết quả T1 sang T2 và quản lý phụ thuộc cache.
            └── engines/
                └── t2_allocation/
                    ├── engine.py  # Mô hình MILP HiGHS và nhánh greedy được hỗ trợ.
                    └── validation.py  # Phát lại assignment và tính lại mục tiêu độc lập với ma trận MILP.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/engines/t2_allocation/engine.py` | [solve](backend/src/smart_retail/engines/t2_allocation/engine.py#L17) |
| `backend/src/smart_retail/engines/t2_allocation/validation.py` | [replay](backend/src/smart_retail/engines/t2_allocation/validation.py#L11) |
| `backend/src/smart_retail/application/decisions.py` | [decided_assignment](backend/src/smart_retail/application/decisions.py#L28) |
| `backend/src/smart_retail/application/stage_workflow.py` | [_candidate](backend/src/smart_retail/application/stage_workflow.py#L40) |

### Cách hiểu đúng so với ảnh

- Nhãn MILP trong ảnh tương ứng nhánh algorithm=milp. Mã vẫn hỗ trợ greedy cho các cấu hình khác.
- OPTIMAL của T2 chỉ là kết luận trong mô hình phân bổ với bố trí hiện có, không phải tối ưu toàn bộ hệ thống.
- Sức chứa tổng chiều rộng của T2 còn phải đi qua kiểm tra vật lý từng SKU ở T3.

## 4. T3 — Xếp vị trí SKU

**Khối trong ảnh:** Ô T3 xếp vị trí SKU (MILP + sửa chữa).

**Đầu vào:** Assignment T2, kích thước SKU, hướng đặt, facings, tầng kệ, số mặt và giới hạn tải.

**Đầu ra:** Placements chứa shelf_id, level_id, face, x_m, facings, capacity_units và load_kg.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   └── decisions.py  # Phát lại planogram cụ thể được truyền từ vòng joint.
            └── engines/
                └── t3_slotting/
                    ├── engine.py  # Chọn nhánh MILP hoặc first-fit và xử lý first-fit bị mắc kẹt.
                    ├── mip.py  # Mô hình đóng gói hữu hạn để tối ưu xếp SKU.
                    ├── repair.py  # Sắp lại một kệ trong ngân sách giới hạn khi first-fit thất bại.
                    └── validation.py  # Kiểm tra độc lập hình học placement, sức chứa và tải trọng.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/engines/t3_slotting/engine.py` | [solve](backend/src/smart_retail/engines/t3_slotting/engine.py#L21) |
| `backend/src/smart_retail/engines/t3_slotting/mip.py` | [solve](backend/src/smart_retail/engines/t3_slotting/mip.py#L22) |
| `backend/src/smart_retail/engines/t3_slotting/repair.py` | [repack](backend/src/smart_retail/engines/t3_slotting/repair.py#L19) |
| `backend/src/smart_retail/engines/t3_slotting/validation.py` | [violations](backend/src/smart_retail/engines/t3_slotting/validation.py#L11) |
| `backend/src/smart_retail/application/decisions.py` | [decided_planogram](backend/src/smart_retail/application/decisions.py#L50) |

### Cách hiểu đúng so với ảnh

- Cần đọc nhãn “MILP + sửa chữa” trong ảnh có điều kiện: khi algorithm=milp, engine gọi mip.solve; repack nằm trong nhánh first_fit khi phương pháp này không đặt được SKU. Không có cơ sở để nói mọi lần giải MILP đều gọi repair.
- Tải trọng các mặt trên cùng tầng kệ là tải dùng chung. First-fit/repack không tìm thấy nghiệm chưa đủ chứng minh mọi cách xếp đều vô nghiệm.

## 5. T4 — Mô phỏng SimPy

**Khối trong ảnh:** Ô T4 mô phỏng SimPy.

**Đầu vào:** Quyết định T1–T3, đơn hàng, hành vi, picker, chính sách định tuyến và seed kịch bản.

**Đầu ra:** Metrics và hành trình: mean_distance_m, mean_wait_s, late_orders, completed, routes, journeys và các số liệu sử dụng tài nguyên.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   ├── feedback/
            │   │   └── evaluator.py  # Đánh giá cùng quyết định qua tập seed kịch bản.
            │   └── decisions.py  # Phát lại lựa chọn mô phỏng/định tuyến của quyết định.
            └── engines/
                ├── t4_simulation/
                │   ├── engine.py  # Mô phỏng hành trình và tranh chấp phục vụ kệ/picker bằng SimPy.
                │   └── routing.py  # Chọn thứ tự ghé các điểm lấy hàng.
                └── navigation.py  # Đường đi hợp lệ và khoảng cách trên đồ thị.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/engines/t4_simulation/engine.py` | [solve](backend/src/smart_retail/engines/t4_simulation/engine.py#L38), [navigation](backend/src/smart_retail/engines/t4_simulation/engine.py#L28) |
| `backend/src/smart_retail/engines/t4_simulation/routing.py` | [order](backend/src/smart_retail/engines/t4_simulation/routing.py#L10) |
| `backend/src/smart_retail/engines/navigation.py` | [navigation](backend/src/smart_retail/engines/navigation.py#L17) |
| `backend/src/smart_retail/application/decisions.py` | [decided_simulation](backend/src/smart_retail/application/decisions.py#L65) |
| `backend/src/smart_retail/application/feedback/evaluator.py` | [evaluate](backend/src/smart_retail/application/feedback/evaluator.py#L47) |

### Cách hiểu đúng so với ảnh

- SimPy mô hình hóa hàng chờ phục vụ với giả định được khai báo; không suy ra đây là mô phỏng chuyển động đám đông đầy đủ.
- Cùng tập scenario_seeds được dùng khi so sánh ứng viên trong vòng tìm kiếm. Đường đi được tính trên topology hợp lệ, không chỉ nối khoảng cách thẳng xuyên vật cản.

## 6. Hàm mục tiêu J trên các kịch bản huấn luyện

**Khối trong ảnh:** Ô hàm mục tiêu J: quãng đường, chờ, thiếu hụt, trễ.

**Đầu vào:** Metrics T4, capacity từ T3, nhu cầu SKU, Objective.weights/scales và tập seed kịch bản.

**Đầu ra:** Điểm J của quyết định, vector thành phần chuẩn hóa và biểu diễn phân số dùng khi so sánh.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   ├── feedback/
            │   │   └── evaluator.py  # Tính mục tiêu bốn thành phần và trung bình trên các kịch bản.
            │   └── evaluation.py  # Mục tiêu pipeline tổng hợp và dùng lại định nghĩa khi chấm tập giữ lại.
            └── contracts/
                └── feedback.py  # Khai báo weights, scales, scenario_seeds và điều khiển joint.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/application/feedback/evaluator.py` | [score](backend/src/smart_retail/application/feedback/evaluator.py#L29), [evaluate](backend/src/smart_retail/application/feedback/evaluator.py#L47), [exact_score](backend/src/smart_retail/application/feedback/evaluator.py#L104) |
| `backend/src/smart_retail/contracts/feedback.py` | [Objective](backend/src/smart_retail/contracts/feedback.py#L9), [JointConfig](backend/src/smart_retail/contracts/feedback.py#L22) |
| `backend/src/smart_retail/application/evaluation.py` | [integrated_score](backend/src/smart_retail/application/evaluation.py#L46), [evaluate_held_out](backend/src/smart_retail/application/evaluation.py#L78) |

### Cách hiểu đúng so với ảnh

- Với joint trong sơ đồ, score dùng bốn thành phần: quãng đường trung bình, thời gian chờ trung bình, tỷ lệ thiếu capacity so với nhu cầu và tỷ lệ đơn trễ. Trọng số/scales lấy từ cấu hình; không mặc định tất cả thành phần đều có trọng số dương.
- Thiếu hụt ở đây được tính từ capacity trưng bày và demand, không phải bằng chứng hệ thống đã mô phỏng đầy đủ quá trình trừ tồn kho theo thời gian.
- integrated_score của luồng tổng hợp thông thường có định nghĩa riêng; khi mô tả feedback joint cần chỉ đúng evaluator.score, tránh đánh đồng hai hàm.

Với một quyết định `p` và tập kịch bản `K`, mã joint tính:

$$J(p)=\frac{1}{|K|}\sum_{k\in K}\frac{\sum_{i=1}^{4}w_i\,m_{k,i}(p)/s_i}{\sum_{i=1}^{4}w_i}.$$

`m` lần lượt là quãng đường, chờ, thiếu capacity và tỷ lệ đơn trễ; `w` và `s` là weights/scales cấu hình. Quyết định tốt hơn có J nhỏ hơn.

## 7. Mô hình thay thế S(p) — Quãng đường × độ nóng

**Khối trong ảnh:** Ô mô hình thay thế S(p) và mũi tên độ nóng.

**Đầu vào:** Poses ứng viên, dữ liệu ngành/SKU, kệ cố định và số lượng SKU được lấy từ mô phỏng trạng thái local.

**Đầu ra:** Surrogate score và thứ tự ứng viên; bố trí sai topology bị loại.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   └── feedback/
            │       ├── diagnostics.py  # Rút sku_pick_counts và chẩn đoán từ journeys/routes của các kịch bản.
            │       └── surrogate.py  # Tính heat, đường đi tới kệ, điểm S và thứ tự xếp hạng.
            └── engines/
                └── navigation.py  # Đồ thị đi được và điểm phục vụ trên các mặt kệ.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/application/feedback/surrogate.py` | [heat](backend/src/smart_retail/application/feedback/surrogate.py#L17), [distances](backend/src/smart_retail/application/feedback/surrogate.py#L28), [value](backend/src/smart_retail/application/feedback/surrogate.py#L57), [rank](backend/src/smart_retail/application/feedback/surrogate.py#L78) |
| `backend/src/smart_retail/application/feedback/diagnostics.py` | [analyze](backend/src/smart_retail/application/feedback/diagnostics.py#L10) |
| `backend/src/smart_retail/engines/navigation.py` | [navigation](backend/src/smart_retail/engines/navigation.py#L17) |

### Cách hiểu đúng so với ảnh

- Với walk_heat, độ nóng mỗi ngành khởi đầu là 1 rồi cộng quantity của SKU thuộc ngành được lấy trong mô phỏng. Khi tắt weighting thì heat đều bằng 1.
- distances dùng Dijkstra từ cửa tới điểm phục vụ gần nhất trên các mặt kệ. Ngành fixed_shelf_id giữ kệ chỉ định; phần còn lại ghép heat cao với khoảng cách nhỏ theo quy tắc surrogate.
- S(p) là tín hiệu sàng lọc/xếp hạng. Việc chấp nhận phương án vẫn dựa vào đánh giá T1–T4, replay và J, không dựa riêng vào S.
- Mũi tên “độ nóng” trong ảnh thực tế là thông tin chẩn đoán từ hành trình T4. Một số J đơn lẻ không đủ để suy ra sku_pick_counts.

Biểu diễn ý tưởng surrogate trong ảnh:

$$S(p)=\sum_c h_c\,d_{a(c)}(p).$$

`h_c` là độ nóng ngành, `d_j` là quãng đường tới điểm phục vụ gần nhất của kệ, `a(c)` tuân theo quy tắc ghép surrogate trong `value`. Khi ngành nhiều hơn kệ, danh sách kệ được lặp theo implementation; S không thay thế bài toán sức chứa/khả thi T2–T3.

## 8. Tìm kiếm phản hồi có mô hình thay thế

**Khối trong ảnh:** Ô dưới bên trái: lấy mẫu, xếp hạng, mô phỏng và hạ dần.

**Đầu vào:** Phương án khởi tạo, feedback mô phỏng, cấu hình lân cận, seed tìm kiếm, budget và tolerance.

**Đầu ra:** Nghiệm best đã đánh giá, trace, đường hội tụ, số evaluations và trạng thái kết thúc.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            └── application/
                ├── feedback/
                │   ├── bootstrap.py  # Sửa khả thi có giới hạn khi phương án tuần tự chưa khởi tạo được.
                │   ├── coordinator.py  # Sở hữu vòng tìm kiếm, warm start, đánh giá, chấp nhận, kick và giữ best.
                │   ├── evaluator.py  # Mô phỏng, replay và chấm điểm ứng viên.
                │   ├── neighborhood.py  # Sinh sửa T1/T2/T3 và policy T4 khi layer tương ứng được bật.
                │   ├── restarts.py  # Dòng seed tìm kiếm và random walk/điểm khởi động lại.
                │   ├── state.py  # Snapshot niêm phong và sao chép dữ liệu trạng thái.
                │   └── surrogate.py  # Xếp hạng các bố trí trước khi mô phỏng đầy đủ.
                ├── stage_workflow.py  # Chạy lại các tầng phụ thuộc và cache theo đúng đầu vào.
                └── workflow.py  # Chọn dispatch joint ở tầng application.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/application/feedback/coordinator.py` | [optimize](backend/src/smart_retail/application/feedback/coordinator.py#L102), [warm_start](backend/src/smart_retail/application/feedback/coordinator.py#L360), [assess](backend/src/smart_retail/application/feedback/coordinator.py#L157) |
| `backend/src/smart_retail/application/feedback/neighborhood.py` | [t1_pool](backend/src/smart_retail/application/feedback/neighborhood.py#L158), [actions](backend/src/smart_retail/application/feedback/neighborhood.py#L206) |
| `backend/src/smart_retail/application/feedback/bootstrap.py` | [initialize](backend/src/smart_retail/application/feedback/bootstrap.py#L13) |
| `backend/src/smart_retail/application/feedback/restarts.py` | [search_seed](backend/src/smart_retail/application/feedback/restarts.py#L19), [restart](backend/src/smart_retail/application/feedback/restarts.py#L34) |
| `backend/src/smart_retail/application/feedback/state.py` | [FeedbackSnapshot](backend/src/smart_retail/application/feedback/state.py#L11) |
| `backend/src/smart_retail/application/feedback/surrogate.py` | [rank](backend/src/smart_retail/application/feedback/surrogate.py#L78) |
| `backend/src/smart_retail/application/feedback/evaluator.py` | [evaluate](backend/src/smart_retail/application/feedback/evaluator.py#L47), [exact_score](backend/src/smart_retail/application/feedback/evaluator.py#L104) |
| `backend/src/smart_retail/application/stage_workflow.py` | [_candidate](backend/src/smart_retail/application/stage_workflow.py#L40) |
| `backend/src/smart_retail/application/workflow.py` | [execute](backend/src/smart_retail/application/workflow.py#L16) |

### Cách hiểu đúng so với ảnh

- Điều kiện nhận một bước hạ dần trong nhánh feedback là exact_score(candidate) < exact_score(next_state) - tolerance. Tolerance lấy từ cấu hình.
- Các bước kick/restart có thể chuyển local sang điểm kém hơn để thoát hội tụ; best được giữ riêng. Vì vậy không viết rằng mọi trạng thái của toàn bộ thuật toán đều giảm nghiêm ngặt.
- Warm start là phần triển khai không được vẽ riêng trong ảnh: lấy pool random walks, xếp hạng nếu có surrogate, đánh giá số ứng viên được cấu hình rồi chọn điểm bắt đầu.
- Đây là mô tả cho phương pháp feedback có surrogate, không phải toàn bộ baseline. sequential, random_search, annealing và genetic có quy tắc riêng.
- Không có bảo đảm tối ưu toàn cục chỉ vì tìm kiếm dừng hoặc không tìm được cải thiện trong lân cận đã xét.

## 9. Phương án tốt nhất — Replay độc lập và tập giữ lại theo thời gian

**Khối trong ảnh:** Ô dưới bên phải: best → phát lại độc lập → đánh giá 80/20.

**Đầu vào:** Đơn đã sắp theo thời gian, cấu hình test_size=0.2 và các quyết định best cố định.

**Đầu ra:** Kết quả đánh giá ngoài mẫu, validation, objective, metrics, generalization_gap và trạng thái hoàn tất/giới hạn ngân sách.

### Cây file liên quan

```text
└── backend/
    └── src/
        └── smart_retail/
            ├── application/
            │   ├── experiments/
            │   │   ├── splits.py  # Chia order ID theo thời gian và áp dụng train/held-out cho job.
            │   │   └── validation.py  # Replay độc lập hình học, assignment, planogram và hành trình.
            │   ├── feedback/
            │   │   └── evaluator.py  # Đánh giá quyết định cố định trên các seed đã khai báo.
            │   └── evaluation.py  # Ước lượng demand từ tập được phép, tách đánh giá khỏi tối ưu và chấm best trên tập giữ lại.
            └── engines/
                ├── t1_layout/
                │   └── geometry.py  # Ràng buộc hình học của nghiệm best.
                ├── t2_allocation/
                │   └── validation.py  # Replay ràng buộc và mục tiêu T2.
                └── t3_slotting/
                    └── validation.py  # Replay ràng buộc vật lý T3.
```

### Hàm/lớp cần đọc

| File | Hàm/lớp và vị trí |
|---|---|
| `backend/src/smart_retail/application/experiments/splits.py` | [split_orders](backend/src/smart_retail/application/experiments/splits.py#L50), [apply_split](backend/src/smart_retail/application/experiments/splits.py#L108) |
| `backend/src/smart_retail/application/evaluation.py` | [estimate_demand](backend/src/smart_retail/application/evaluation.py#L28), [with_held_out](backend/src/smart_retail/application/evaluation.py#L169), [evaluate_held_out](backend/src/smart_retail/application/evaluation.py#L78) |
| `backend/src/smart_retail/application/experiments/validation.py` | [verify](backend/src/smart_retail/application/experiments/validation.py#L18) |
| `backend/src/smart_retail/engines/t1_layout/geometry.py` | [violations](backend/src/smart_retail/engines/t1_layout/geometry.py#L20) |
| `backend/src/smart_retail/engines/t2_allocation/validation.py` | [replay](backend/src/smart_retail/engines/t2_allocation/validation.py#L11) |
| `backend/src/smart_retail/engines/t3_slotting/validation.py` | [violations](backend/src/smart_retail/engines/t3_slotting/validation.py#L11) |
| `backend/src/smart_retail/application/feedback/evaluator.py` | [evaluate](backend/src/smart_retail/application/feedback/evaluator.py#L47) |

### Cách hiểu đúng so với ảnh

- Việc chia 80/20 phải thực hiện trước tìm kiếm. Code sắp đơn theo placed_at và id, lấy ceil(N × 0.2) đơn cuối để đánh giá; tỷ lệ thực tế có làm tròn khi N không chia hết.
- with_held_out bỏ evaluation khỏi đầu vào tìm kiếm và dành phần ngân sách đánh giá theo budget_fraction; bộ cấu hình V5 hiện kiểm tra dùng 0.25 cho tỷ lệ ngân sách này, khác với tỷ lệ số đơn 0.2.
- Khi chấm tập giữ lại, giữ cố định bố trí, assignment, planogram và chính sách định tuyến đã chọn. Không tối ưu lại theo 20% đơn giữ lại.
- Replay độc lập còn được gọi ngay trong evaluator trước khi chấm ứng viên, không chỉ một lần ở cuối như hình giản lược.
- Tập đơn cuối theo thời gian khác với tùy chọn holdout_seeds. Các tệp trong nhóm này là mã đánh giá nghiệm của ứng dụng, không phải file unit test hay Playwright.

## 10. Các file nối toàn bộ sơ đồ thành lượt thực nghiệm

Đây là phần hạ tầng thực thi phía sau hình: chốt snapshot, nhận diện nguồn, queue/worker, records và báo cáo.

```text
├── backend/
│   └── src/
│       └── smart_retail/
│           ├── application/
│           │   └── experiments/
│           │       ├── analysis.py  # Thống kê và so sánh ghép cặp trong phạm vi dữ liệu.
│           │       ├── campaign.py  # Lập job, chốt input/split/identity và chạy qua queue.
│           │       ├── cli.py  # Entrypoint chạy, xác minh, phân tích và phát lại campaign.
│           │       ├── reports.py  # Bảng và biểu đồ từ record đã lưu.
│           │       └── storage.py  # Bằng chứng bất biến, checkpoint và checksum.
│           ├── infrastructure/
│           │   └── provenance.py  # Nhận diện byte nguồn, solver và dependency.
│           └── workers/
│               └── runner.py  # Worker claim job, giám sát tiến trình con và lưu receipt.
└── scripts/
    ├── build_paper_v5_configs.py  # Sinh thiết kế W1/W2 và cấu hình từng phần campaign.
    └── run_paper_v5_parallel.py  # Điều phối ba slot campaign độc lập và kiểm tra kết quả/identity.
```

| File | Điểm vào |
|---|---|
| `backend/src/smart_retail/application/experiments/campaign.py` | [initialize](backend/src/smart_retail/application/experiments/campaign.py#L56), [job_sections](backend/src/smart_retail/application/experiments/campaign.py#L34), [run](backend/src/smart_retail/application/experiments/campaign.py#L129) |
| `backend/src/smart_retail/application/experiments/cli.py` | [main](backend/src/smart_retail/application/experiments/cli.py#L75) |
| `backend/src/smart_retail/application/experiments/storage.py` | [write](backend/src/smart_retail/application/experiments/storage.py#L27), [verify_integrity](backend/src/smart_retail/application/experiments/storage.py#L64) |
| `backend/src/smart_retail/workers/runner.py` | [work_once](backend/src/smart_retail/workers/runner.py#L135) |
| `backend/src/smart_retail/infrastructure/provenance.py` | [runtime_identity](backend/src/smart_retail/infrastructure/provenance.py#L12) |
| `backend/src/smart_retail/application/experiments/reports.py` | [report](backend/src/smart_retail/application/experiments/reports.py#L94) |
| `backend/src/smart_retail/application/experiments/analysis.py` | [analyze](backend/src/smart_retail/application/experiments/analysis.py#L296) |
| `scripts/build_paper_v5_configs.py` | [build](scripts/build_paper_v5_configs.py#L124), [main](scripts/build_paper_v5_configs.py#L164) |
| `scripts/run_paper_v5_parallel.py` | [main](scripts/run_paper_v5_parallel.py#L57), [inspect_records](scripts/run_paper_v5_parallel.py#L36) |

## 11. Cấu hình nào gắn với sơ đồ này?

Đã đọc chỉ mục và **68 file cấu hình** trong [experiments/configs/paper-v5-unlimited-parallel-20261110](experiments/configs/paper-v5-unlimited-parallel-20261110). Các cấu hình hiện tại khai báo đủ bốn họ mặt bằng, temporal_holdout với test_size=0.2 và budget_fraction=0.25. Đây là thông tin thiết kế, không phải khẳng định các lượt chạy hiện đã hoàn tất.

```text
experiments/configs/paper-v5-unlimited-parallel-20261110/
├── index.json                         # Danh mục campaign và khối W1/W2.
├── paper-v5-w1-*-part*.json           # Mẫu tên: so sánh chính theo scale/phần.
└── paper-v5-w2-ablation-part*.json    # Mẫu tên: ablation các thành phần V5.
```

Hai dòng có dấu `*` là **mẫu tên**, không phải tên file thực. Các file cụ thể và treatment được khai báo trong index và từng cấu hình. `feedback_v5` với joint.mode=feedback và surrogate=walk_heat là nhánh cần đọc để hiểu phương pháp có mô hình thay thế trong hình; các baseline khác không đi theo toàn bộ nhánh này.

## 12. Thứ tự đọc mã đề xuất

1. `generators.py` và các hợp đồng đầu vào: dữ liệu và giả định đến từ đâu.
2. `workflow.py`, `stage_workflow.py`, rồi engine T1–T4: một phương án được dựng và đánh giá ra sao.
3. `feedback/evaluator.py`, `diagnostics.py`, `surrogate.py`: J, độ nóng và S có quan hệ thế nào.
4. `neighborhood.py`, `restarts.py`, `coordinator.py`: sinh ứng viên, xếp hạng, chấp nhận và giữ best.
5. `splits.py`, `evaluation.py`, `experiments/validation.py`: tách dữ liệu, chấm ngoài mẫu và replay.
6. `campaign.py`, worker, storage và scripts Paper V5: chạy có thể truy xuất và lưu bằng chứng.

## 13. Phạm vi kiểm chứng của tài liệu

Các đường dẫn, tên hàm/lớp và vị trí dòng được kiểm tra từ file thực tế. Tỷ lệ chia tập và bốn họ mặt bằng được đối chiếu trên toàn bộ bộ cấu hình nêu trên. Đây là truy vết mã tĩnh; không chạy solver/campaign, không tạo hoặc sửa dữ liệu vận hành, không kết luận thêm về hiệu quả thuật toán.

Tham khảo đối chiếu chi tiết đã có: [WORKFLOW_REPORT_CODE_MAPPING.md](docs/research/WORKFLOW_REPORT_CODE_MAPPING.md). Vị trí dòng trong các liên kết có thể đổi nếu mã được chỉnh sau ngày lập tài liệu.
