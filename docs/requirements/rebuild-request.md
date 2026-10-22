# PROMPT — TÁI XÂY DỰNG TOÀN BỘ SMART RETAIL FLOOR ALLOCATION TRONG THƯ MỤC GỐC

## 1. Vai trò và nhiệm vụ

Bạn là **Principal Software Architect, Senior Full-Stack Engineer, Optimization Engineer và QA Architect**.

Hãy truy cập trực tiếp vào dự án hiện tại:

`D:\Smart_Retail_Floor_Allocation`

Nhiệm vụ là **tái xây dựng toàn bộ cấu trúc và nền tảng phần mềm ngay trong thư mục này**, thay thế kiến trúc cũ bằng một kiến trúc mới hoàn chỉnh, rõ ràng, dễ phát triển, dễ kiểm thử, dễ mở rộng và phù hợp với nghiên cứu khoa học.

**Đây là yêu cầu triển khai thực tế, không phải yêu cầu chỉ viết tài liệu hoặc đề xuất kế hoạch.**

## 2. Yêu cầu bắt buộc về vị trí dự án

- Giữ nguyên thư mục gốc: `D:\Smart_Retail_Floor_Allocation`.
- Không tạo `Smart_Retail_Floor_Allocation_V2`.
- Không tạo một repository hoặc thư mục dự án mới nằm bên trong thư mục hiện tại.
- Không tiếp tục sử dụng `smart-retail-layout/` làm thư mục chứa mã nguồn chính.
- Toàn bộ `frontend`, `backend`, `tests`, `datasets`, `docs`, `configs`, `scripts` và các thành phần khác phải được tổ chức trực tiếp dưới thư mục gốc.
- Không duy trì song song hai hệ thống cũ và mới.
- Không bắt buộc tương thích với API, import, workflow hoặc cách tổ chức mã nguồn cũ.
- Được phép thay thế và viết lại các thành phần cũ khi cần thiết.

**Lưu ý về an toàn:** Trước khi thay thế hoặc xóa bất kỳ nội dung hiện có nào, phải kiểm kê trạng thái Git, các tệp chưa commit và dữ liệu nghiên cứu. Tạo bản sao lưu có thể khôi phục ở vị trí bên ngoài thư mục dự án, không ghi đè dữ liệu gốc và không xóa `.git`. Không tự ý reset, clean, commit hoặc push. Những tệp không thể xác định rõ là có thể loại bỏ phải được bảo toàn cho đến khi có xác nhận.

Sau khi có bản sao lưu an toàn, tiến hành thay thế kiến trúc cũ trong chính thư mục gốc; mục tiêu cuối cùng không còn thư mục legacy hoặc lớp tương thích thừa.

## 3. Mục tiêu hệ thống

Xây dựng nền tảng:

**Smart Retail Floor Allocation — Intelligent Retail Layout Optimization Platform**

Hệ thống có nhiệm vụ hỗ trợ thiết kế và tối ưu khu vực trưng bày trong cửa hàng bán lẻ, bao gồm:

1. Quản lý và thiết kế mặt bằng khu vực trưng bày.
2. Quản lý số lượng, vị trí và thông số vật lý của kệ.
3. Tối ưu phân bổ ngành hàng.
4. Tối ưu sắp xếp sản phẩm trên các tầng kệ.
5. Phân tích nhu cầu và hành vi khách hàng.
6. Phân tích đơn hàng và hoạt động lấy hàng.
7. Mô phỏng luồng di chuyển của khách và nhân viên.
8. Tối ưu theo nhiều mục tiêu và ràng buộc.
9. Trực quan hóa phương án và so sánh kết quả.
10. Hỗ trợ thực nghiệm, kiểm chứng và tái lập kết quả nghiên cứu.

Hệ thống cần có kiến trúc hỗ trợ bốn tầng:

- **T1 — Geometry & Layout:** Quản lý, kiểm tra và tối ưu mặt bằng, vị trí kệ, lối đi.
- **T2 — Category Allocation:** Tối ưu phân bổ ngành hàng.
- **T3 — Product Slotting & Planogram:** Tối ưu bố trí SKU trên từng kệ, từng tầng.
- **T4 — Customer & Picker Operations:** Mô phỏng hành vi, tuyến đường, thời gian và xung đột vận hành.

Mỗi tầng phải có thể chạy và kiểm thử độc lập trước khi kết nối thành workflow tổng thể.

## 4. Thiết kế lại hoàn toàn dữ liệu đầu vào

Hệ thống có **7 nhóm dữ liệu đầu vào chính thức**.

### Input 01 — Bản vẽ khu vực trưng bày

Đầu vào là **bản vẽ 2D của khu vực trưng bày có kích thước thực tế**, không chỉ là hai giá trị chiều dài và chiều rộng.

Yêu cầu:

- Có trình chỉnh sửa mặt bằng trực quan.
- Hỗ trợ hình chữ nhật và đa giác bất kỳ.
- Nhập hoặc hiệu chỉnh kích thước các cạnh.
- Có đơn vị đo và hệ tọa độ thống nhất.
- Hỗ trợ cửa ra vào, lối đi, cột, tường, vật cản, vùng cấm.
- Hỗ trợ nhập bản vẽ từ dữ liệu có cấu trúc.
- Có thể sử dụng hình ảnh làm nền tham chiếu khi dựng lại mặt bằng, nhưng phải hiệu chuẩn tỷ lệ; không tự coi ảnh là kích thước chính xác.
- Tự kiểm tra diện tích, ranh giới, hình học hợp lệ và khả năng bố trí.

### Input 02 — Thông tin kệ trưng bày

Yêu cầu nhập:

- Số lượng kệ.
- Mã kệ và loại kệ.
- Chiều dài, chiều rộng, chiều cao.
- Số tầng.
- Kích thước hữu dụng của từng tầng.
- Tải trọng tối đa nếu áp dụng.
- Kệ một mặt hoặc hai mặt.
- Hướng đặt.
- Các ràng buộc vị trí.

Phải phân biệt hai chế độ:

**Fixed Layout:** Vị trí kệ đã xác định, hệ thống chỉ tối ưu ngành hàng và sản phẩm.

**Optimizable Layout:** Người dùng cung cấp số lượng và kích thước kệ, hệ thống được phép tối ưu vị trí và hướng đặt trong khu vực trưng bày.

Không được bắt buộc người dùng nhập trước vị trí kệ trong trường hợp nhiệm vụ của T1 là tìm vị trí tối ưu.

### Input 03 — Dữ liệu ngành hàng

Bao gồm:

- Mã và tên ngành hàng.
- Mức độ ưu tiên.
- Nhu cầu.
- Diện tích hoặc sức chứa yêu cầu.
- Mức độ tương quan giữa các ngành hàng.
- Yêu cầu đặt gần hoặc tách xa.
- Điều kiện trưng bày đặc biệt.

### Input 04 — Dữ liệu sản phẩm

Bao gồm:

- SKU và tên sản phẩm.
- Ngành hàng.
- Chiều dài, chiều rộng, chiều cao sản phẩm.
- Trọng lượng nếu cần.
- Nhu cầu bán.
- Số lượng mặt trưng bày.
- Hướng đặt được phép.
- Số lớp chồng.
- Những yêu cầu vật lý đặc biệt.

Tính toán sức chứa phải dựa trên kích thước hữu dụng của tầng kệ, kích thước sản phẩm, khoảng hở và các giới hạn liên quan.

### Input 05 — Nhu cầu và hành vi khách hàng

Bao gồm:

- Lượng khách theo thời gian.
- Nhu cầu theo sản phẩm và ngành hàng.
- Giỏ hàng và sản phẩm thường mua cùng nhau.
- Mức độ quan tâm đến các khu vực.
- Mô hình di chuyển.
- Khung giờ cao điểm.

Nếu không có dữ liệu hành trình thực tế, hệ thống phải nêu rõ mô hình hành vi đang được giả định hoặc mô phỏng.

### Input 06 — Đơn hàng

Bao gồm:

- Mã đơn hàng.
- Thời gian đặt hàng.
- Loại đơn hàng.
- Danh sách SKU và số lượng.
- Thời gian cần xử lý.
- Dữ liệu vận hành picker khi cần mô phỏng lấy hàng.

Tách dữ liệu `orders` và `order_lines`, có khóa và ràng buộc toàn vẹn rõ ràng.

### Input 07 — Cấu hình tối ưu

Bao gồm:

- Mục tiêu tối ưu.
- Trọng số các mục tiêu.
- Ràng buộc cứng và mềm.
- Giới hạn thời gian chạy.
- Thuật toán và solver.
- Giới hạn bộ nhớ, số vòng lặp.
- Random seed.
- Mức độ chính xác và điều kiện dừng.

Phải chuẩn hóa đơn vị và thang đo của các mục tiêu trước khi kết hợp thành hàm mục tiêu.

Mọi nhóm dữ liệu cần có schema, validation, ví dụ hợp lệ, ví dụ không hợp lệ và thông báo lỗi dễ hiểu.

## 5. Công nghệ đề xuất

Sử dụng một nền tảng hiện đại, ưu tiên:

**Frontend**
- React
- TypeScript
- Vite
- Konva cho trình biên tập bản vẽ 2D
- Thư viện biểu đồ phù hợp
- Giao diện chia thành các trang nghiệp vụ

**Backend**
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

**Database**
- PostgreSQL

**Optimization**
- NumPy / SciPy
- HiGHS và Pyomo hoặc một công cụ mô hình MILP phù hợp
- pymoo
- NetworkX
- Shapely

**Simulation**
- SimPy hoặc bộ mô phỏng phù hợp với yêu cầu nghiên cứu.

**Testing**
- pytest
- Hypothesis
- Vitest
- Playwright

**Code Quality**
- Ruff
- mypy
- ESLint
- TypeScript strict mode

**Infrastructure**
- Docker Compose
- Database migrations
- Worker thực thi các tác vụ tối ưu
- Logging và quản lý artifact
- CI kiểm thử tự động

Kiểm tra phiên bản và khả năng tương thích của các thư viện trước khi chốt cấu hình. Không thêm framework hoặc dịch vụ chỉ vì xu hướng nếu chưa có nhu cầu kỹ thuật cụ thể.

## 6. Cấu trúc thư mục đích bắt buộc

Tổ chức lại trực tiếp thành:

```text
D:\Smart_Retail_Floor_Allocation\
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── pages/
│   │   ├── features/
│   │   │   ├── projects/
│   │   │   ├── floorplan-editor/
│   │   │   ├── shelves/
│   │   │   ├── categories/
│   │   │   ├── products/
│   │   │   ├── demand/
│   │   │   ├── orders/
│   │   │   ├── optimization/
│   │   │   └── results/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   └── tests/
│
├── backend/
│   ├── src/
│   │   └── smart_retail/
│   │       ├── api/
│   │       ├── application/
│   │       ├── domain/
│   │       │   ├── floorplan/
│   │       │   ├── shelves/
│   │       │   ├── categories/
│   │       │   ├── products/
│   │       │   ├── demand/
│   │       │   ├── orders/
│   │       │   └── optimization/
│   │       ├── engines/
│   │       │   ├── t1_layout/
│   │       │   ├── t2_allocation/
│   │       │   ├── t3_slotting/
│   │       │   └── t4_simulation/
│   │       ├── contracts/
│   │       ├── infrastructure/
│   │       ├── reporting/
│   │       └── workers/
│   ├── migrations/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── contracts/
│   │   ├── e2e/
│   │   ├── regression/
│   │   └── performance/
│   └── pyproject.toml
│
├── datasets/
│   ├── samples/
│   ├── synthetic/
│   └── schemas/
│
├── experiments/
├── configs/
├── scripts/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── data/
│   ├── modules/
│   ├── testing/
│   └── decisions/
│
├── .github/
│   └── workflows/
├── docker-compose.yml
├── AGENTS.md
├── HANDOFF.md
├── README.md
└── .gitignore
```

Đây là cấu trúc mục tiêu. Có thể điều chỉnh các thư mục con nếu có lý do kỹ thuật rõ ràng, nhưng không được quay lại mô hình để toàn bộ thuật toán nằm chung trong một thư mục `src` phẳng hoặc một module `system` quá lớn.

## 7. Quy tắc kiến trúc

Áp dụng **Modular Monolith kết hợp Clean Architecture**.

- Một module chỉ có một nhóm trách nhiệm rõ ràng.
- Tách domain model khỏi schema HTTP và ORM model.
- Tách logic nghiệp vụ khỏi database, API và giao diện.
- Thuật toán không được phụ thuộc vào FastAPI hoặc React.
- Các tầng T1–T4 có API Python rõ ràng.
- Tầng ứng dụng điều phối workflow; engine không tự quyết định quy trình toàn hệ thống.
- Không tạo import vòng.
- Không dùng global mutable state để trao đổi dữ liệu nghiệp vụ.
- Không đưa logic tính toán trực tiếp vào endpoint.
- Không đặt solver và mô phỏng đồng bộ trên request thread.
- Mỗi lần chạy có run ID, cấu hình, trạng thái và artifact riêng.
- Mỗi module có tài liệu đầu vào, đầu ra, trách nhiệm và lệnh test.

Phải thiết kế mô hình dữ liệu cho:

`Project`, `Store`, `DisplayArea`, `Floorplan`, `Shelf`, `ShelfLevel`, `Category`, `Product`, `DemandProfile`, `CustomerBehavior`, `Order`, `OrderLine`, `OptimizationConfig`, `OptimizationRun`, `LayoutSolution`, `Planogram`, `SimulationResult`.

## 8. Quy trình hoạt động mục tiêu

Thiết kế quy trình:

**Tạo dự án → Vẽ khu vực trưng bày → Khai báo kệ → Nhập ngành hàng → Nhập sản phẩm → Nhập nhu cầu và đơn hàng → Cấu hình tối ưu → Kiểm tra dữ liệu → Chạy T1/T2/T3/T4 → Hiển thị kết quả → So sánh phương án → Xuất báo cáo.**

Mỗi bước phải:

- Lưu được dữ liệu.
- Có validation.
- Có lỗi rõ ràng.
- Có trạng thái hoàn thành.
- Có khả năng chỉnh sửa và chạy lại.
- Không yêu cầu nhập lại toàn bộ dữ liệu khi chỉ thay đổi một phần.

Đầu ra phải có khả năng truy vết về dữ liệu và cấu hình ban đầu.

## 9. Yêu cầu giao diện

Thiết kế một ứng dụng web dễ sử dụng, không còn giao diện rời rạc.

Các trang chính:

1. Dashboard.
2. Project Management.
3. Floorplan Editor.
4. Shelf Configuration.
5. Category Management.
6. Product Management.
7. Demand & Behavior.
8. Orders.
9. Optimization Configuration.
10. Optimization Runs.
11. Layout Results.
12. Planogram Viewer.
13. Simulation & Analytics.
14. Reports.
15. System Diagnostics.

**Floorplan Editor là thành phần trọng tâm.**

Phải có:

- Thước tỷ lệ và hệ tọa độ.
- Lưới và snap-to-grid.
- Chức năng vẽ và chỉnh sửa đa giác.
- Hiển thị kích thước các cạnh.
- Kéo, thả, xoay và chọn kệ.
- Hiển thị kích thước kệ.
- Kiểm tra kệ vượt ranh giới.
- Kiểm tra chồng lấn.
- Hiển thị lối đi và vật cản.
- Chuyển đổi giữa chế độ kệ cố định và kệ cần tối ưu.
- Lưu và tải lại bản vẽ.

Không triển khai giả chức năng bằng các nút không có hành động thực.

## 10. Yêu cầu kiểm thử

Thiết lập kiểm thử ngay từ khi khởi tạo dự án.

Phải có:

- Unit test cho domain và thuật toán.
- Contract test cho input/output.
- Integration test cho API và database.
- E2E test cho quy trình người dùng.
- Property-based test cho hình học, sức chứa và ràng buộc.
- Regression test cho nghiệm tối ưu và kết quả mô phỏng.
- Performance test cho kích thước bài toán khác nhau.

Mỗi engine T1–T4 phải có bộ fixture nhỏ, xác định được đáp án hoặc kiểm chứng độc lập.

Đặc biệt kiểm tra:

- Mặt bằng không hợp lệ.
- Kệ nằm ngoài khu vực trưng bày.
- Kệ chồng lấn.
- Lối đi không đáp ứng ràng buộc.
- Sản phẩm không vừa tầng kệ.
- Số lượng hoặc kích thước âm.
- Khóa tham chiếu sai.
- Nhu cầu hoặc đơn hàng không hợp lệ.
- Bài toán không có nghiệm.
- Solver timeout.
- Hủy tác vụ giữa chừng.
- Kết quả không thể tái lập.

Không được công bố test thành công nếu chưa thực sự chạy và ghi nhận kết quả.

## 11. Kế hoạch thực thi

Thực hiện theo giai đoạn, nhưng phải triển khai thực tế trong repository.

### Phase 0 — Kiểm kê và bảo vệ dữ liệu

- Đọc `AGENTS.md`, `HANDOFF.md` và quy tắc liên quan.
- Kiểm tra Git.
- Xác định dữ liệu và công việc chưa commit.
- Tạo snapshot an toàn ngoài thư mục dự án.
- Xác định những nội dung cần bảo tồn làm nguồn tham chiếu nghiên cứu.
- Ghi nhận mọi thao tác có nguy cơ mất dữ liệu.

### Phase 1 — Thay thế cấu trúc thư mục cũ

- Tạo cấu trúc mới ngay trong thư mục gốc.
- Loại bỏ kiến trúc legacy khỏi cây mã nguồn chính sau khi đã bảo toàn dữ liệu.
- Không tạo project V2.
- Không duy trì `smart-retail-layout` là lõi ứng dụng.
- Tạo cấu hình package, dependency, lint, test và script.

### Phase 2 — Xây dựng backend foundation

- FastAPI.
- Database.
- Migrations.
- Domain models.
- API contracts.
- Validation.
- Error handling.
- Logging.
- Quản lý dự án, dataset và optimization run.

### Phase 3 — Xây dựng frontend foundation

- Layout ứng dụng.
- Routing.
- Dashboard.
- Các màn hình nhập dữ liệu.
- API client.
- Quản lý trạng thái.
- Form validation.
- Floorplan Editor phiên bản đầu tiên.

### Phase 4 — Xây dựng T1

- Mô hình hình học.
- Validation.
- Shelf placement.
- Lối đi.
- Objective và constraints.
- Thuật toán nền có kiểm chứng.
- Trực quan hóa phương án.

### Phase 5 — Xây dựng T2

- Category allocation.
- Hard/soft constraints.
- MILP baseline.
- Heuristic baseline.
- Đánh giá nghiệm.

### Phase 6 — Xây dựng T3

- Shelf-level capacity.
- Product dimensions.
- Facing.
- Orientation.
- Planogram optimization.
- Hiển thị sản phẩm theo tầng kệ.

### Phase 7 — Xây dựng T4

- Customer demand.
- Customer movement.
- Order picking.
- Route computation.
- Congestion.
- Simulation KPIs.

### Phase 8 — Tích hợp

- Workflow T1–T4.
- Job execution.
- Result storage.
- Replay.
- Dashboard kết quả.
- So sánh phương án.
- Export báo cáo.

### Phase 9 — Nghiệm thu

- Kiểm thử toàn hệ thống.
- Đánh giá hiệu năng.
- Kiểm tra kiến trúc.
- Chuẩn hóa tài liệu.
- Kiểm tra khả năng tái lập kết quả.
- Kiểm tra chạy lại trên môi trường sạch.

## 12. Yêu cầu bàn giao

Sau mỗi giai đoạn phải cung cấp:

1. Danh sách file được tạo, sửa, di chuyển hoặc loại bỏ.
2. Cấu trúc thư mục thực tế.
3. Những chức năng đã thực sự hoạt động.
4. Các chức năng chưa triển khai.
5. Lệnh khởi động.
6. Lệnh kiểm thử.
7. Kết quả test thực tế.
8. Lỗi còn tồn tại.
9. Quyết định kiến trúc quan trọng.
10. Công việc tiếp theo.

Cập nhật tài liệu `README.md`, `AGENTS.md` và `HANDOFF.md` phù hợp với kiến trúc mới, đồng thời giữ lại bằng chứng và lịch sử cần thiết.

## 13. Tiêu chí hoàn thành

Dự án mới chỉ được xem là hoàn thành khi:

- Mọi thành phần nằm trong `D:\Smart_Retail_Floor_Allocation`.
- Không phụ thuộc vào mã nguồn legacy.
- Có giao diện sử dụng được.
- Có backend và database hoạt động.
- Có thể tạo dự án và lưu dữ liệu.
- Có thể vẽ mặt bằng với số liệu kích thước thực tế.
- Có thể khai báo số lượng kệ, kích thước và số tầng.
- Có thể nhập ngành hàng, sản phẩm, nhu cầu và đơn hàng.
- Có thể cấu hình và thực thi các bài toán tối ưu đã triển khai.
- T1–T4 có thể kiểm thử độc lập.
- Có thể lưu và xem kết quả.
- Có tài liệu đầy đủ.
- Có kiểm thử tự động.
- Không còn các module legacy không sử dụng trong cây ứng dụng chính.
- Không có lỗi hồi quy hoặc lỗi cấu trúc chưa được giải thích tại thời điểm nghiệm thu.

Không đánh dấu hoàn thành toàn bộ nếu mới chỉ có skeleton, mock API, giao diện mẫu hoặc thuật toán placeholder.

## 14. Yêu cầu hành động ngay

**Hãy bắt đầu bằng việc truy cập trực tiếp `D:\Smart_Retail_Floor_Allocation`, kiểm kê mã nguồn và trạng thái Git, sau đó triển khai Phase 0, Phase 1 và nền tảng Phase 2–3 ngay trong thư mục gốc.**

Không dừng lại ở việc đề xuất một cấu trúc lý thuyết.

Không tạo dự án V2.

Không tiếp tục chắp vá kiến trúc V1.

Không xóa dữ liệu khi chưa có bản sao lưu có thể khôi phục.

Sau mỗi bước thực hiện, báo cáo chính xác kết quả và tiếp tục theo lộ trình cho đến khi gặp một quyết định có nguy cơ mất dữ liệu hoặc cần quyền xác nhận.

**Mục tiêu cuối cùng là một nền tảng Smart Retail Floor Allocation sạch, có kiến trúc chuẩn, có thể xây dựng và nghiên cứu lâu dài, được triển khai trực tiếp trong thư mục dự án hiện tại.**