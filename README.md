# Smart Retail Floor Allocation

**Database hiện tại: MongoDB (22/10/2026).** API, worker và experiment runner đã
chuyển sang PyMongo đồng bộ. Đã chuyển và đối chiếu 16 project, 24 SKU, 12 đơn hàng,
24 dòng đơn, 8 optimization run; giữ nguyên SQLite gốc và 32 artifact gốc.
Heartbeat cũ được lưu offline. MongoDB thật đã restart và kiểm tra lại dữ liệu.

- [Nghiệm thu migration và bằng chứng kiểm thử](docs/migration/MONGODB_MIGRATION_ACCEPTANCE.md)
- [Khởi chạy, cấu hình, migration và vận hành MongoDB](docs/migration/MONGODB_OPERATIONS.md)
- [Phục hồi ứng dụng SQL từ bản sao ngoài repository](docs/migration/SQLITE_ROLLBACK.md)
- [Bàn giao mới nhất](HANDOFF.md)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
# Dừng API/worker/frontend; MongoDB tiếp tục giữ dữ liệu.
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
# Khi bảo trì cần dừng cả MongoDB cục bộ do project quản lý:
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1 -StopMongoDB
```

Ứng dụng: http://127.0.0.1:5173/#research. Các số liệu SQLite/joint bên dưới là
checkpoint trước migration; kết quả kiểm thử hiện tại nằm trong báo cáo MongoDB
phía trên. Không cần Alembic cho runtime hiện tại. Docker/Compose và Atlas chưa
được chạy kiểm chứng trên máy này. Không xóa `var/mongodb`: đây là database chính.

## Checkpoint joint trước migration database

**Mở rộng hiện tại — Joint T1–T4 (22/10/2026).** Đã triển khai vòng phản hồi thật
từ T4 sang T1/T2/T3, strict descent nhiều vòng, snapshot/trace bất biến, tính lại
theo phụ thuộc, exact oracle cho miền hữu hạn và verifier certificate độc lập.
Không suy ra tối ưu toàn cục của bài toán tổng quát từ hội tụ feedback.

Trạng thái cuối: **CLOSED_LOOP_FEEDBACK_READY**;
**JOINT_EXACT_SMALL_INSTANCE_CERTIFIED** cho miền bốn/128 trạng thái công bố;
**JOINT_GENERAL_OPTIMALITY_NOT_PROVEN**. JO01–JO18 PASS theo
[receipt cuối](docs/research/evidence/20261022-joint-readiness-02.json).
Kiểm chứng mới: **155 pytest, 4 Vitest, 9 Playwright PASS**; E11–E15 có 69/69
job chính thành công, hai đối chứng no-incumbent giữ đúng FAILED/INFEASIBLE.

- [Phát biểu mô hình và phạm vi chứng nhận](docs/research/JOINT_OPTIMIZATION_FORMULATION.md)
- [Kết quả E11–E15](docs/research/JOINT_OPTIMIZATION_RESULTS_20261022.md)
- [Hướng dẫn chạy joint/verify/replay](docs/research/HOW_TO_RUN_JOINT_OPTIMIZATION.md)
- [Ma trận JO01–JO18](docs/research/JOINT_OPTIMIZATION_ACCEPTANCE.md)

Dashboard hiện có thêm Sequential, Multistart, Closed-Loop Feedback, Exact Joint
và Hybrid; chọn campaign `joint_*` để giữ thiết kế so sánh đầy đủ. Mở
http://127.0.0.1:5173/#research. Các trạng thái feedback, chứng nhận finite-instance
và chưa chứng minh bài toán tổng quát được hiển thị riêng.

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/joint_effectiveness.json --output experiments/results/my-joint
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze experiments/results/my-joint --output experiments/reports/my-joint
```

Output phải là đường dẫn mới. Dữ liệu/kết quả bên dưới thuộc checkpoint trước
phần mở rộng joint; bằng chứng mới theo các liên kết phía trên và HANDOFF.md.

**Trạng thái hiện tại — 22/10/2026: `EXPERIMENT_READY_SYNTHETIC`, ER01–ER15 PASS.**
Đã triển khai nền tảng thực nghiệm tổng hợp chạy thật trên Windows/SQLite:
schema 1.1 và JSON/CSV; T1 local search và kiểm tra liên thông; T2 soft affinity;
T3 facing range; T4 routing/picker hữu hạn/demand theo kỳ; workflow và cache bền
vững; campaign/checkpoint/resume/replay; thống kê và Matplotlib PNG/SVG; dashboard
điều khiển runner thật.

Kiểm chứng mới: **133 pytest, 4 Vitest, 8 Playwright PASS**, kèm Ruff/mypy/ESLint,
build, audit dependency và kiểm tra kiến trúc. Pilot 19/19, main 105/105, robustness
20/20, reproducibility 4/4 thành công; replay pilot ở môi trường Python mới khớp
input/result SHA-256 **19/19**. Đối chứng không khả thi giữ riêng failure/infeasible.

- [Bàn giao hiện tại](HANDOFF.md)
- [Ma trận ER01–ER15](docs/research/EXPERIMENT_READINESS_MATRIX.md)
- [Kết quả và giới hạn diễn giải](docs/research/RESULTS_20261022.md)
- [Hướng dẫn chạy đầy đủ](docs/research/HOW_TO_RUN_EXPERIMENTS.md)
- [Mô hình hiện tại và giả định](docs/research/MODEL_SCOPE_20261022.md)
- [Lệnh và kết quả kiểm chứng](docs/research/evidence/20261022-release-01/verification.json)

```powershell
cd D:\Smart_Retail_Floor_Allocation
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
Push-Location frontend
npx playwright install chromium
Pop-Location
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Ứng dụng: **http://127.0.0.1:5173**; dashboard thực nghiệm:
**http://127.0.0.1:5173/#research**; API: **http://127.0.0.1:8010/docs**.
Dùng Python 3.12.10 và Node 22.22.3 đã kiểm chứng. PostgreSQL/Compose và remote
GitHub Actions chưa chạy; kết quả tổng hợp chưa xác nhận hiệu quả cửa hàng thật.

Chạy pilot độc lập (thư mục output phải mới):

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/pilot.json --output experiments/results/my-pilot
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze experiments/results/my-pilot --output experiments/reports/my-pilot
```

## Checkpoint lịch sử — 21/10/2026

Phần dưới giữ ngữ cảnh checkpoint cũ. Các test count, trạng thái acceptance,
giới hạn mô hình và đường dẫn cũ trong phần này không đại diện cho bản 22/10;
tài liệu hiện hành nằm trong các liên kết phía trên.

Nền tảng nghiên cứu thiết kế mặt bằng bán lẻ, phân bổ ngành hàng, xếp SKU và mô
phỏng hoạt động khách/picker. Mã ứng dụng nằm trực tiếp trong thư mục gốc:
`frontend/` và `backend/`. Kiến trúc modular monolith tách domain, application,
engine, hợp đồng dữ liệu và infrastructure.

**Trạng thái 21/10/2026:** đã tái cấu trúc và có workflow baseline chạy thật từ
giao diện → API → database → worker → T1–T4 → kết quả/báo cáo. Chưa nghiệm thu
toàn bộ nền tảng theo prompt; các baseline chưa phải tối ưu liên tầng hoàn chỉnh.
PostgreSQL/Compose có cấu hình nhưng chưa được chạy tại máy Windows này.

Checkpoint nghiên cứu mới: **`RESEARCH_ACCEPTANCE_INCOMPLETE`**. Đã có T3 MILP
strip-packing bên cạnh first-fit, replay vật lý độc lập, workflow so sánh hữu hạn
1–8 phương án T1–T4, chuẩn hóa mục tiêu và cache phụ thuộc trong một run. T4 lấy
đúng mặt kệ từ T3, xuất route points và tính cả đoạn nối cửa vào. Đây chưa phải
tối ưu toàn cục hoặc nghiệm thu đầy đủ master prompt.

Kiểm chứng mới: **86 pytest, 4 Vitest, 6 Playwright passed**. Chiến dịch tổng hợp
E01–E08 có 80 job/5 seed mỗi nhánh: 75 thành công, 5 first-fit thất bại có chủ đích
ở E03; MILP giải được cả 5 trường hợp đó. Replay mới khớp input/result hash.
Xem [ma trận 14 gate](docs/research/ACCEPTANCE_MATRIX.md),
[kết quả](docs/research/RESULTS_AND_DISCUSSION.md) và
[giới hạn còn lại](docs/research/LIMITATIONS.md).

## Chạy trên Windows

Yêu cầu Python 3.12, Node ≥22.12. Phiên này đã dùng Python 3.12.10 và Node 22.22.3.
Dependency Python được khóa tại `backend/requirements-lock.txt`; frontend có
version cụ thể và `package-lock.json`. Không dùng môi trường Python của mã cũ.

```powershell
cd D:\Smart_Retail_Floor_Allocation
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Mở **http://127.0.0.1:5173**. API: **http://127.0.0.1:8010/docs**.
Cổng 8000 được giữ cho tiến trình có sẵn, không bị dừng hoặc thay cấu hình.
`start.ps1` chạy API, worker, Vite ở cửa sổ ẩn, kiểm tra cổng và health, ghi PID
riêng để có thể dừng đúng các dịch vụ đã tạo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
```

Database local là SQLite file `var/smart_retail.db`; artifact ở `var/artifacts`.
Đây là dữ liệu bền vững qua restart, không phải mock/in-memory repository.
Log ở `var/logs`; PID/start time của dịch vụ ở `var/services.json`.

Để chạy từng tiến trình thủ công, dùng ba terminal riêng:

```powershell
.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head
.venv\Scripts\python.exe -m uvicorn smart_retail.api.main:app --host 127.0.0.1 --port 8010
# Terminal 2:
.venv\Scripts\python.exe -m smart_retail.workers.runner
# Terminal 3:
npm --prefix frontend run dev
```

## Thử quy trình đầu-cuối

1. Vào **Dự án**, chọn **Tạo dự án mẫu**. Dữ liệu được đánh dấu tổng hợp và lưu đủ
   bảy nhóm; có thể thay bằng dữ liệu nghiên cứu của bạn.
2. Trong **Mặt bằng**, chỉnh đa giác/độ dài cạnh/tọa độ, vật cản, cửa vào và lưới.
   Có thể kéo kệ, đổi góc 0/90 và khóa vị trí. Dùng bảng tọa độ để chỉnh bằng bàn phím.
3. Chọn **Optimizable** nếu muốn T1 tìm vị trí; không cần nhập x/y trước. Chọn
   **Fixed** khi các kệ đã có vị trí hợp lệ. Bấm **Lưu bản vẽ & kệ**.
4. Các trang kệ/ngành hàng/SKU/nhu cầu/đơn hàng/cấu hình có form và JSON editor,
   nhập file JSON, lưu riêng từng nhóm và trả lỗi kiểm tra tham chiếu cụ thể.
5. Vào **Lần chạy**, kiểm tra dữ liệu và **Chạy baseline**. API xếp hàng; worker
   chạy trong process con, UI cập nhật trạng thái. Nút hủy thực sự dừng child process.
6. Xem **Kết quả mặt bằng**, **Planogram**, **Mô phỏng & phân tích**. Nền mặt bằng
   và nghiệm đều lấy từ snapshot của lần chạy, kể cả khi dự án hiện tại đã sửa.
7. **Replay** tạo run mới từ snapshot cũ; **So sánh & báo cáo** đối chiếu các
   nghiệm và tải JSON có truy vết hoặc CSV planogram.

Không có dữ liệu hành trình thực trong fixture. T4 là mô phỏng với giả định công
khai. Ảnh tham chiếu editor phải được hiệu chuẩn chiều rộng thực và chỉ nằm trong
phiên trình duyệt; chưa có kho lưu ảnh bền vững.

## Năng lực thực tế

| Thành phần | Đã thực hiện | Giới hạn chính |
|---|---|---|
| Dữ liệu | 7 hợp đồng Pydantic, JSON Schema, fixture hợp lệ/lỗi, FK | Chưa có mọi trường chuyên sâu trong prompt; xem input-contracts |
| Lưu trữ | Project aggregate theo revision; orders/order_lines riêng | Mỗi project một mặt bằng; chưa có nhiều store hoặc phân quyền |
| Floorplan Editor | Polygon, tọa độ/cạnh, lưới/snap, kệ kéo/đổi hướng, cửa/vật cản, lưu/tải | Chưa có DXF import, undo history hoặc hiệu chuẩn bằng hai điểm ảnh |
| T1 | Geometry/clearance replay; constructive grid và multistart variants | Chưa chứng minh tối ưu hình học hoặc kiểm toàn mạng lối đi liên thông |
| T2 | HiGHS MILP + greedy, capacity/fixed/proximity, replay độc lập | Mỗi ngành chọn một kệ, nhiều ngành có thể chung kệ; chưa split/soft affinity |
| T3 | First-fit + MILP strip, replay facings/orientation/stack/load/overlap | Facings cố định, một khối/SKU; chưa tối ưu doanh thu hoặc facing range |
| T4 | Shortest-path grid, mặt lấy SKU từ T3, entrance connectors, routes/picks, shelf queues | Chưa crowd dynamics, giới hạn đội picker hoặc hành vi thực nghiệm |
| Worker | Queue bền vững, process isolation, hủy/timeout, checksum | Chưa scheduler phân tán; chưa stress nhiều worker |
| Kết quả | Lưu nghiệm, snapshot, source/dependencies, replay, so sánh, JSON/CSV | Chưa PDF report hoặc generic partial rerun/invalidation |
| Triển khai | Local chạy thật; Compose PostgreSQL + nginx; CI | Docker/PostgreSQL/CI chưa được chạy trong phiên này |

T3 có MILP finite strip với số facings cố định, chia tải chung
hai mặt, mục tiêu demand-weighted capacity; T1 có các sweep variant; workflow
lưu mọi candidate và chọn theo route/wait/stock shortfall chuẩn hóa. Cache chỉ
trong run, chưa generic partial rerun hoặc cache bền vững. Editor có hoàn tác/làm
lại cho các thao tác trong editor (50 bước, không lưu qua reload); chưa gồm các
control bên ngoài editor. Chi tiết hiện hành ở ma trận gate.

T1 không tìm được trên lưới và greedy/first-fit thất bại được báo riêng với
infeasibility do solver chứng minh. Không coi baseline này là hoàn thành toàn bộ V4
cũ hoặc một nghiên cứu đã được nghiệm thu.

## Kiểm thử

```powershell
.venv\Scripts\python.exe -m pytest backend/tests -q --basetemp var/pytest-manual
.venv\Scripts\python.exe -m ruff check backend
.venv\Scripts\python.exe -m mypy --config-file backend/pyproject.toml backend/src/smart_retail
.venv\Scripts\python.exe -m pip check
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend test
# API, worker và frontend phải đang chạy trước E2E:
cd frontend
npx playwright install chromium
npm run test:e2e
```

E2E cô lập có thể chạy trực tiếp từ root, tự tạo database/artifact riêng và dừng
đúng process thử đã tạo, không thêm dự án thử vào database ứng dụng đang dùng:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_e2e.ps1
.venv\Scripts\python.exe experiments/run_campaign.py --output experiments/results/my-new-campaign --seeds 11,23,37,53,71
.venv\Scripts\python.exe experiments/analyze_campaign.py experiments/results/my-new-campaign
```

Thư mục campaign phải chưa tồn tại. Cấu hình tối ưu có `slotting_algorithm`
(`first_fit`/`milp`), `candidate_count` (1–8), `travel_weight`, `wait_weight`,
`stock_weight` không âm và ít nhất một trọng số dương. Mọi candidate dùng chung
`time_limit_s`; không nhân ngân sách theo số candidate. Xem
[hướng dẫn tái lập/replay](docs/research/REPRODUCIBILITY.md).

Các ca backend kiểm tra contracts/engine/property/integration/regression/
performance. E2E kiểm tra lưu qua reload, chạy thật, replay, tải report, lỗi nhập,
dự án rỗng/partial, desktop/mobile và accessibility trên hai màn hình chính.
Test tạo các project nghiên cứu thử riêng trong database local; không xóa dự án
người dùng. Các lượt E2E mới ghi report, screenshot, download và trace vào
`var/playwright/`; TypeScript ghi build info vào `var/typescript/`. Các thư mục này
được Git bỏ qua. Bằng chứng nghiệm thu đã lưu trong `docs/testing/` được giữ lại
theo checkpoint, không bị các lượt chạy thường xuyên ghi đè.

Kết quả checkpoint tái cấu trúc ở [docs/testing/verification.md](docs/testing/verification.md),
[JUnit](docs/testing/pytest-results.xml), [Playwright JSON](docs/testing/playwright-results.json)
và [screenshot](docs/testing/ui/). Không trộn số test lịch sử của nguồn cũ.

## PostgreSQL và Docker Compose

Khi có Docker, tạo `.env` ở root với `POSTGRES_PASSWORD` dùng ký tự URL-safe,
sau đó chạy:

```powershell
docker compose up --build -d
```

Compose khởi động PostgreSQL 17, chạy migration trước API/worker và phục vụ
frontend qua nginx; database và artifact có named volumes. Local Python/Vite cần
được dừng trước vì dùng cùng cổng 8010/5173. Không dùng `down -v` nếu cần giữ dữ liệu.

Với PostgreSQL có sẵn, đặt `$env:SMART_RETAIL_DATABASE_URL` trước khi migrate và
khởi động dịch vụ. Dùng `scripts/verify_postgres.py` với database thử nghiệm riêng.
File CI có PostgreSQL service và kiểm thử thực nhưng chưa được push/chạy trên GitHub.

## Cấu trúc chính

```text
frontend/             React strict TS, shell/pages, feature inputs, Konva, result viewers
backend/
  src/smart_retail/
    api/               HTTP adapters
    application/       Transactions, snapshots, workflow orchestration
    domain/            Business models by module
    contracts/         Seven validated input groups
    engines/           t1_layout, t2_allocation, t3_slotting, t4_simulation
    infrastructure/    ORM, connections, provenance
    reporting/         JSON/CSV export
    workers/           Durable queue, child-process supervision
  migrations/          Alembic schema history
  tests/               Contracts, unit, integration, regression, performance
datasets/              Samples and JSON schemas
experiments/           E01–E08 runner, independent audit, paired statistics and immutable results
configs/               Environment examples
scripts/               Setup, start/stop, PostgreSQL and preservation verification
docs/                  Architecture, migration, data/API/modules/testing
.github/workflows/     Automated verification definition
```

Cấu trúc thực tế được ghi trong [actual-tree.txt](docs/architecture/actual-tree.txt).
Các tài liệu gốc `de-cuong/`, `docx/`, `Retail_TestPack/` và HANDOFF HTML được giữ
tại chỗ, chưa dùng làm dataset của engine mới.

Đợt [dọn mã nguồn ngày 21/10/2026](docs/testing/cleanup-20261021.md) đã bỏ mã/export
và dependency dư, đồng thời chuyển đầu ra test mới về `var/`. Thao tác xóa nhóm
cache/build tạm bị chính sách thực thi chặn; danh sách còn lại được ghi trong báo cáo.

## Dữ liệu cũ và bàn giao

Snapshot đã xác minh nằm ngoài dự án:
`C:\Users\admin\Documents\SmartRetailBackups\20261021-rebuild-00301a95`.
Cây nguồn cũ nguyên vẹn được chuyển tới:
`D:\04_Archives\SmartRetail\20261021-retired-source-358740e0`.
Ứng dụng mới không phụ thuộc chúng. `.git` được giữ nguyên, không commit/push.

- [Migration và phục hồi](docs/architecture/migration.md)
- [Kiến trúc và persistence](docs/architecture/overview.md)
- [Quyết định công nghệ](docs/decisions/0001-modular-monolith.md)
- [Hợp đồng 7 input](docs/data/input-contracts.md)
- [API routes](docs/api/routes.md)
- [T1–T4 và giới hạn](docs/modules/engines.md)
- [Trạng thái từng phase](docs/architecture/phase-status.md)
- [HANDOFF hiện tại và lịch sử](HANDOFF.md)

Bước kế tiếp là versioned input contract, topology/vùng chức năng T1 và các
phần thuật toán chưa đạt trong ma trận nghiệm thu. PostgreSQL/Compose cần môi
trường sẵn sàng để kiểm chứng riêng. Đã có bounded integrated search và tập không
bị trội hữu hạn; hiệu chuẩn thực nghiệm, partial rerun và tối ưu liên tầng đầy đủ
vẫn chưa hoàn thành.
