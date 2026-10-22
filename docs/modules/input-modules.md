# Module dữ liệu

Mỗi domain module dưới `backend/src/smart_retail/domain/` chỉ quản lý mô hình nghiệp
vụ của mình. Chuyển đổi từ JSON và kiểm tra schema ở contracts, persistence ở
infrastructure, điều phối ở application. Không đặt ORM/FastAPI trong domain.

| Module | Trách nhiệm / đầu vào / đầu ra | Kiểm thử |
|---|---|---|
| projects | Project/Store/DisplayArea; dữ liệu dự án → aggregate có revision | tests/integration/test_api.py |
| floorplan | Polygon/entrance/obstacles → Floorplan/LayoutSolution | tests/contracts/test_inputs.py + unit/test_engines.py |
| shelves | Vật lý kệ, tầng, mặt và vị trí → Shelf/ShelfLevel | tests/contracts/test_inputs.py + unit/test_engines.py |
| categories | Nhu cầu, capacity, proximity/fixed → Category | tests/contracts/test_inputs.py + T2 independent enumeration |
| products | Kích thước, facing/orientation/stack → Product/Planogram | contracts + unit property-based physical capacity |
| demand | Arrivals/baskets/behavior → DemandProfile/CustomerBehavior/SimulationResult | contracts + deterministic T4/routing checks |
| orders | Đơn và dòng đơn có khóa → Order/OrderLine | contracts + relational FK integration test |
| optimization | Ngân sách/seed/algorithm → OptimizationConfig/OptimizationRun | contracts + timeout/cancel/replay integration |

Chạy các lệnh trên từ root bằng `.venv\Scripts\python.exe -m pytest backend/`
và đường dẫn test trong bảng; thêm `-q`. Public domain exports ở domain/models.py,
không chứa thuật toán. Engine chỉ nhận domain types; HTTP output contracts nằm ở
contracts/outputs.py, không dùng ORM object làm response.

Frontend features chứa định nghĩa default/template và hướng dẫn của từng input;
DataInputPage dùng InputEditor chung để giữ cơ chế JSON/import/error thống nhất.
FloorplanEditor, PlanogramViewer và SimulationAnalytics có component riêng. Các
route đi qua một app shell để chia sẻ lựa chọn project/run và revision hiện tại.
