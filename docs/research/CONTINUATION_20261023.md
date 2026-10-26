# Tiếp tục thực nghiệm bài báo — 23/10/2026

## Thanh tiến độ và phục hồi lưu trữ — 18:57 UTC+7

Người dùng yêu cầu hiển thị tiến độ, tiếp tục thực nghiệm và cho biết đã làm trống
dung lượng. Bảng trực tiếp đã mở tại **http://127.0.0.1:8766**, tự cập nhật khoảng
5 giây, chỉ đọc dữ liệu. Mã tại `scripts/paper_progress/`. Bảng có thanh tổng,
bảy thanh theo khối, job thành công/lỗi, campaign đang chạy và dung lượng đĩa.

Trong lúc kiểm tra phát hiện D: đã hết dung lượng khoảng 18:02, gây một job
EXECUTION_ERROR (ENOSPC), MongoDB và bộ điều phối dừng. Còn 758 kết quả gốc:
757 thành công và một lỗi. Đã chuyển và kiểm tra SHA-256 mọi tệp của 20 campaign
sang `C:/Users/admin/Documents/SmartRetailRuntime/paper-v2-results`; giữ đường dẫn
D: bằng junction ở cấp thư mục campaign. Việc chuyển cả campaign bảo đảm kiểm tra
đường dẫn artifact vẫn nằm trong root đã resolve. Dữ liệu và hash input không đổi.

Tên database được tính từ đường dẫn root đã resolve, vì vậy đã sao lưu BSON và
restore sang namespace tương ứng mới, kiểm tra run ID, số document, indexes và
integrity của cả 20 campaign. Namespace cũ được giữ nguyên. Bằng chứng:
`var/paper-storage-recovery.json` cùng `relocation.json` và
`database-relocation/` dưới SmartRetailRuntime. User đã giải phóng thêm dung lượng D:.

Job lỗi `58b19e75...` được chạy lại trong campaign chẩn đoán riêng gồm 10 fold:
10/10 SUCCEEDED, replay độc lập PASS và input SHA-256 khớp bản lỗi. Bản lỗi gốc
vẫn giữ trong kết quả chính. Receipt:
`C:/Users/admin/Documents/SmartRetailRuntime/disk-job-recovery-v2/recovery-receipt.json`.
Lần thử helper đầu thiếu main guard khi spawn trên Windows; đã sửa và giữ riêng
lần thử trước, không thay kết quả nghiên cứu gốc.

Hai campaign X2 Tiny đã chạy tiếp lúc 18:57:43 UTC+7, coordinator wrapper PID 19324,
watcher wrapper PID 3708. Log mới có tiền tố `storage-recovery-`; watcher giữ máy
thức, quét lỗi và đặt nơi sao lưu cuối tại `E:/SmartRetailBackups`. Scheduler thêm
kiểm tra còn ít nhất 2 GiB trên ổ thực sự chứa campaign và tránh đè log mồ côi.
Mã engine/dependency vẫn khớp preflight. Các job mới sau khởi động lại đã thành công.
Kiểm tra mới: Ruff cho các script PASS, API/DOM của dashboard có đủ 8 thanh, số
job/max khớp dữ liệu thật, không tràn ngang. Full backend tests không chạy lại cho
thay đổi script/UI này; receipt 198 test trước đó giữ nguyên phạm vi lịch sử.

## Phát hiện và xử lý lỗi — khoảng 17:00 UTC+7

Người dùng cho phép chẩn đoán, sửa lỗi và chạy tiếp mà không cần xin lại quyền
cho từng sửa chữa thông thường. Tại thời điểm kiểm tra có 331 kết quả, đều
SUCCEEDED, chưa có lỗi job hay đánh giá held-out thiếu ngân sách.

Watcher được bổ sung quét lỗi mỗi 30 giây, lưu cảnh báo bất biến và bản sao bằng
chứng có SHA-256 vào `var/paper-unattended/job-errors/`. Phân loại riêng: retry
hạ tầng đã hết lượt, giới hạn tài nguyên, kết quả mô hình/tìm kiếm, giới hạn đánh
giá held-out và lỗi cần chẩn đoán mã nguồn. Không đổi kết quả lỗi thành PASS.
Campaign đã có retry WORKER_CRASH/WORKER_LOST; watcher kiểm tra kết nối database
tối đa ba lần trước khi thử chạy tiếp supervisor trong giới hạn đã đặt.

Tiến trình Python nền không tự viết/kiểm thử bản vá cho lỗi mã nguồn bất kỳ.
Những lỗi chưa biết được ghi NEEDS_CODE_DIAGNOSIS để assistant đang hoạt động
xử lý. Nếu sửa backend/dependency, phải tái hiện, kiểm thử và dùng identity/output
mới; không trộn kết quả trước và sau sửa. Quyền sửa lỗi của người dùng được giữ
cho các phiên tiếp tục, không yêu cầu duyệt lại từng sửa chữa đã nằm trong phạm vi.

Kiểm chứng mới cho phần giám sát: Ruff PASS; kiểm tra phân loại, lưu bằng chứng,
gọi lại không tạo cảnh báo trùng và giữ nguyên byte kết quả gốc đều PASS. Chỉ
khởi động lại watcher, không tác động runner/job. PID hiện tại nằm trong
`var/paper-unattended/process.json`; log `live-alerts-watcher.*.log`.

## Chuyển sang hai campaign song song — 14:03:45 UTC+7

Người dùng đồng ý tăng tốc bằng hai campaign độc lập. Bộ điều phối mới là
`scripts/run_paper_parallel.py`, PID wrapper 27548, PID thực thi 3232. Mỗi campaign
vẫn có một worker, database và artifact riêng. Tối đa hai campaign chạy cùng lúc;
có rào chắn giữa các khối X1 → X4 → X2 → X2b → X5 → X6 → X3, giữ X3 ở cuối.
Không sửa backend, dependency, cấu hình khoa học hoặc ngân sách job.

Đã lưu và đọc lại xác minh 266 mục tại
`C:/Users/admin/Documents/SmartRetailBackups/20261023T070215Z-parallel-handover/`.
Sau khi X4 Small ghi checkpoint job thứ 23, đặt các cờ tạm dừng campaign tại
ranh giới sau job. Runner tuần tự kết thúc; chỉ gỡ các cờ do thao tác này tạo.
233 kết quả đã hoàn thành đều SUCCEEDED, không có job bị hủy giữa chừng;
235 tệp record/identity có trước vẫn khớp SHA-256. Receipt:
`var/paper-parallel/handover.json`.

Các campaign chưa chạy có checkpoint CANCELLED với 0 job do quá trình bàn giao;
coordinator mới tự resume chúng. Đây là trạng thái tạm dừng có chủ đích, không
phải bỏ thực nghiệm. Báo cáo X4 ở thư mục gốc được runner cũ xuất lúc bàn giao
là báo cáo **chưa đủ job**. Sau khi chạy hết, watcher xác minh và xuất báo cáo
đầy đủ vào thư mục mới; đường dẫn chính xác nằm trong completion receipt.

Đã quan sát X4 Small và Medium phần 1 chạy đồng thời và đều ghi job mới thành
công. Kiểm tra Ruff, giới hạn hai slot và X3-cuối đạt. Mẫu tài nguyên ban đầu còn
khoảng 11 GiB RAM khả dụng; chưa thấy lỗi resource limit. CPU tổng vẫn có thể thấp
khi hai job đang xử lý các bước chủ yếu một luồng. Chưa đủ số đo để kết luận hệ
số tăng tốc hay cập nhật ETA.

- Trạng thái điều phối: `var/paper-parallel/status.json`.
- Nhật ký và danh sách hash kết quả có trước: `var/paper-parallel/journal.json`.
- Log từng campaign: `var/paper-parallel/*-attempt*.log`.
- Watcher wrapper hiện tại 37416, PID thực thi 8092; keep-awake được chấp nhận.
- Watcher thử lại bằng runner song song, rồi xác minh, báo cáo và sao lưu như dưới.
- Receipt chế độ thực thi được xuất cùng báo cáo cuối. Số đo wall của phần tuần
  tự và phần song song không phải phép so sánh tốc độ có kiểm soát. Cạnh tranh tài
  nguyên có thể ảnh hưởng nghiệm của tìm kiếm bị giới hạn theo thời gian.

## Chạy không cần giám sát trực tiếp

Người dùng đã yêu cầu chạy toàn bộ và sẽ để máy hoạt động. Runner hiện hữu được
giữ nguyên. Watcher `scripts/watch_paper_campaigns.py` bắt đầu lúc 13:50:44 UTC+7,
PID wrapper 36480, PID Python thực thi 11564. Windows đã chấp nhận yêu cầu giữ
máy thức; màn hình vẫn được phép tắt. Máy đang cắm điện, pin 100%, AC sleep vốn
đã tắt. Không thay đổi thiết lập nguồn điện toàn hệ thống.

Watcher chờ runner và supervisor numerical kết thúc; sau gián đoạn có thể chạy
tiếp tối đa hai lần, chờ lease hết hạn và từ chối nếu source/dependency drift.
Không tự tăng ngân sách hoặc chạy lại job đã có kết quả terminal. Sau lượt chạy,
nó xác minh job key/receipt/integrity, checksum báo cáo, tạo lại báo cáo thiếu vào
thư mục mới, rồi sao lưu và đọc lại ZIP ngoài repo ở
`C:/Users/admin/Documents/SmartRetailBackups/<UTC>-paper-complete/`.

- Trạng thái cập nhật mỗi khoảng 30 giây: `var/paper-unattended/status.json`.
- Hoàn tất xác minh và sao lưu: `var/paper-unattended/completion.json`.
- Lỗi giám sát/xác minh/sao lưu: `var/paper-unattended/failure.json`.
- `VERIFIED_ALL_JOBS_SUCCEEDED`: không thiếu job, không có job thất bại hay đánh
  giá held-out chưa hoàn tất.
- `FINISHED_WITH_LIMITATIONS`: có job thiếu, thất bại hoặc đánh giá chưa hoàn tất;
  số lượng chi tiết được giữ nguyên trong receipt.
- `NEEDS_ATTENTION`: watcher gặp lỗi; đọc failure/log, không xem là hoàn tất.

Đã chạy Ruff cho script, check-only cho đủ 20 cấu hình/4.276 job, verifier trên
X1 hoàn tất (150 records), xác minh 110 file báo cáo và thử sao lưu/đọc lại ZIP.
Các bước này đạt; chưa có bằng chứng hoàn tất toàn bộ watcher trên lượt dài.
`powercfg /requests` không đọc được vì cần quyền administrator; trạng thái
keep-awake được xác nhận trực tiếp từ giá trị trả về của Windows API.

## Phạm vi và trạng thái

Người dùng yêu cầu đọc code và tiếp tục thực nghiệm. Checkout là
`D:/Smart_Retail_Floor_Allocation`, nhánh `main`, HEAD
`b94b2f706c1ceec1af89b8025cfd56fd1778a3a6`. Worktree và index sạch khi bắt đầu.
Không có tiến trình Python/MongoDB đang chạy tại thời điểm kiểm tra đầu tiên.

Đã rà soát các luồng HTTP/UI, contracts/domain, T1–T4, feedback/exact/hybrid,
queue/worker, persistence, chia fold, đánh giá held-out, thống kê, báo cáo,
kiểm thử và công cụ vận hành. Danh mục đọc/parse và SHA-256 tại
`var/continue-20261023-01/source-inventory.json` gồm 283 tệp được Git quản lý,
38.105 dòng, bao gồm cả khóa dependency, cấu hình và schema; không bao gồm
dependency đã cài hoặc báo cáo/kết quả sinh ra. Danh mục không phải chứng nhận
rằng mọi nhánh chương trình đã được kiểm thử.

Dữ liệu thô `experiments/results/20261023-paper-v2/` và file PID được nhắc trong
bàn giao cũ không tồn tại ở checkout này. Vì vậy lượt hiện tại bắt đầu từ đầu;
không tuyên bố đã phục hồi 18 job được ghi trong bàn giao trước. Các kết quả
ngày 22/10 còn trên ổ đĩa được giữ nguyên, không gộp với lượt mới.

## Sửa lỗi trước khi chạy

1. `reports.py` gọi exporter joint cho từng campaign, trong khi exporter tạo
   các file CSV bằng chế độ không ghi đè. Báo cáo gộp thất bại ở campaign thứ hai
   với `FileExistsError: joint-comparison.csv`. Đã đổi sang gom mọi campaign
   trước khi xuất các CSV, ví dụ và hình hội tụ một lần.
2. Exporter deepmg chỉ giữ cấu hình của phần cuối khi cùng một phương án xuất
   hiện ở nhiều phần chia theo seed. Đã hợp nhất seed và kiểm tra các tham số
   còn lại tương thích; file cấu hình xuất ra dựng lại đúng toàn bộ job key.

Test mới `test_pooled_joint_report_retains_every_campaign` chạy hai campaign
thật qua durable queue/worker. Đã quan sát test FAIL trước sửa lỗi (1), rồi PASS
sau sửa. Test kiểm tra đủ hàng CSV và trace của hai seed, hình hội tụ, cùng
đồng nhất job key khi khởi tạo kế hoạch từ cấu hình deepmg đã gộp.

Không đổi thuật toán, hàm mục tiêu, ngân sách job, dữ liệu gốc hoặc 20 cấu hình
paper-v2. Thay đổi reporting cũng thay đổi source identity; lượt mới dùng identity
sau sửa, không dùng lại identity lịch sử.

## Kiểm chứng mới

Các lệnh chạy từ thư mục gốc, trừ khi nêu khác:

| Lệnh | Kết quả mới |
|---|---|
| `.venv/Scripts/python.exe -m pip check` | PASS |
| `.venv/Scripts/python.exe -m ruff check --config backend/pyproject.toml backend scripts` | PASS |
| `.venv/Scripts/python.exe -m mypy --config-file backend/pyproject.toml backend/src/smart_retail` | PASS, 102 source files |
| `.venv/Scripts/python.exe scripts/verify_architecture.py --output var/continue-20261023-01/architecture-frozen.json` | PASS, 102 Python modules, 40 frontend modules |
| `npm.cmd --prefix frontend run lint` | PASS |
| `npm.cmd --prefix frontend run test` | 4/4 PASS |
| `npm.cmd --prefix frontend run build` | PASS, TypeScript và Vite |
| `.venv/Scripts/python.exe -m pytest backend/tests -q -p no:cacheprovider --basetemp var/continue-20261023-01/pytest-frozen --junitxml var/continue-20261023-01/pytest-frozen.xml` | 198 PASS, 0 FAIL, 0 SKIP, 106,12 s |
| `.venv/Scripts/python.exe var/continue-20261023-01/preflight.py` | 20 cấu hình, 4.276 đầu vào job hợp lệ |
| So schema đã lưu với `SECTIONS[*].model_json_schema()` | 7/7 khớp |
| So `runtime_identity()` với receipt preflight sau kiểm thử | Khớp |
| `git diff --check` | PASS; có cảnh báo chuyển LF sang CRLF theo cấu hình Git |

Pytest có một cảnh báo deprecation Starlette/httpx. Không chạy lại Playwright,
Docker Compose, tải dài hoặc kiểm chứng thực địa trong mốc này. Không chạy thêm
benchmark cạnh tranh CPU sau khi khởi động lượt nghiên cứu.

Các lượt chưa đạt được giữ để truy vết:

- Lần khởi động MongoDB đầu tiên: health check ngay sau bootstrap chưa sẵn sàng;
  lần kiểm tra sau xác thực, ping và indexes đều đạt, không đổi credentials.
- `pytest.xml`: 153 PASS, 44 lỗi thiết lập do thư mục cha của `--basetemp` chưa
  tồn tại. Đã sửa cách gọi, không sửa source để xử lý lỗi thiết lập này.
- `pytest-rerun.xml`: 197 PASS trước bản sửa báo cáo đầy đủ.
- `pytest-final.xml`: 197 PASS, 1 FAIL do source reporting còn được sửa khi test
  replay đang chạy. Drift guard từ chối trộn source đúng thiết kế. Lượt
  `pytest-frozen.xml` sau khi giữ source cố định đã đạt 198/198.

## Lượt chính đang chạy

Khởi động lúc `2026-10-23T06:35:59Z` (13:35:59, UTC+7) bằng
`Start-Process -WindowStyle Hidden` với command:

```powershell
.venv/Scripts/python.exe -u scripts/run_paper_campaigns.py
```

Supervisor PID ban đầu: **30636**. File PID kèm thời điểm tạo, HEAD và hash index:
`var/paper-v2-run.pid.json`. Phải kiểm tra PID và command line hiện tại trước khi
thao tác, vì PID có thể được hệ điều hành tái sử dụng.

- Log: `var/paper-v2-run.log`, `var/paper-v2-run.err.log`.
- Raw results: `experiments/results/20261023-paper-v2/<campaign>/`.
- Journal: `experiments/results/20261023-paper-v2/journal.json`.
- Báo cáo: `experiments/reports/20261023-paper-v2/<block>/`.
- Thứ tự: X1 → X4 → X2 → X2b → X5 → X6 → X3.
- Tổng kế hoạch: 4.276 job; một worker/campaign, job chạy trong process có thể dừng.

MongoDB portable 8.0.16 đã khởi động qua script của repo. Mỗi campaign dùng database
riêng theo hash thư mục output. Không khởi động API/frontend chính, không commit,
push, reset hoặc thay index.

**Không sửa `backend/src/*.py` hoặc dependency trong lúc runner chạy.** Nếu phải
sửa, cần một lượt output mới với identity mới. Ước lượng khoảng 27 giờ trong
runbook là lịch sử trên máy trước, chưa phải thời gian hoàn tất được đo ở lượt
hiện tại. Thất bại, timeout và resource limit vẫn phải giữ trong kết quả.

## Bước tiếp theo

Mốc **13:45:09 UTC+7**: X1 hoàn tất **150/150 SUCCEEDED**, mọi kiểm tra độc lập
PASS, thời gian campaign 548,548 s. Integrity kiểm tra 12.095 tệp JSON đạt PASS.
30 job exact và 30 job hybrid đều có `GLOBAL_OPTIMAL_CERTIFIED` với certificate
`PASS`; exact và hybrid có cùng điểm theo từng seed. Đã chạy thêm CLI verifier
riêng trên certificate exact seed 1: PASS, kiểm tra đủ bốn trạng thái của miền.
Receipt: `var/continue-20261023-01/offline-proof.json`.

| Phương án | Job thành công | Mục tiêu trung bình | Wall worker trung bình (s) |
|---|---:|---:|---:|
| baseline | 30/30 | 0,1527143397 | 1,8755 |
| multistart | 30/30 | 0,1527143397 | 2,0111 |
| feedback | 30/30 | 0,1427143397 | 2,5048 |
| exact | 30/30 | 0,1027143397 | 2,4880 |
| hybrid | 30/30 | 0,1027143397 | 3,2094 |

Mục tiêu nhỏ hơn là tốt hơn. Campaign wall còn bao gồm điều phối, lưu trữ và
fingerprint nên khác tổng wall worker. Chạy trên máy không kiểm soát tải; không
suy ra ưu thế hiệu năng tổng quát từ các thời gian này.

Báo cáo X1: `experiments/reports/20261023-paper-v2/X1/summary.md`, 150 records,
5/5 phương án xuất đủ `_file_sum_ok`, 6 hình PNG/SVG. Đã kiểm tra SHA-256 của
toàn bộ 110 file trong manifest báo cáo. Số liệu máy đọc:
`var/continue-20261023-01/x1-summary.json`. Đây là X1 không CV trên một fixture
`local_trap`, chưa phải kết quả tổng quát hóa trên tập thử của X2/X2b/X3.

Runner đã sang X4 Tiny: 15/60 SUCCEEDED tại 13:45:58 UTC+7; các khối còn lại
chưa hoàn tất. `verification.json` lưu checkpoint tại mốc này. PID wrapper ban
đầu là 30636, Python thực thi con là 7892; khi dừng phải xác minh và xử lý cả
cây tiến trình thuộc runner như runbook, không chỉ wrapper.

Theo dõi checkpoint/journal; khi campaign hoàn tất, kiểm tra integrity và các
trạng thái, rồi xuất báo cáo. Chỉ diễn giải số liệu của campaign đã xác minh.
Sau khi toàn bộ runner kết thúc, kiểm tra đủ job dự kiến, các báo cáo theo khối
và checksum; lưu bản sao dữ liệu thô ra ngoài repo. X3 giữ ở cuối như thiết kế.
Mọi dữ liệu vẫn là SYNTHETIC; chứng nhận exact chỉ trong miền hữu hạn đã khai báo.
# Milestone 21:34 UTC+7: adaptive three-campaign execution

User requested three simultaneous campaigns, falling back to two if RAM or CPU
pressure causes problems. The new coordinator adopts the two live X2 processes;
X2 and X2b share a pool while X3 remains last. Inputs, engine source, dependency
identity and scientific budgets are unchanged. The optional third slot resumes
one job at a time so reducing the cap can finish its current job without cancelling
it or rewriting a historical record. This adds resume/checksum overhead.

`var/paper-parallel/concurrency.json` persists the limit. Sampling every 5 seconds
latches it to two for RAM >=90% or available <2 GiB for 15 seconds, CPU >=95% for
120 seconds, or new resource/worker-crash failures (timeout only with CPU >=90%).
These conservative triggers do not prove CPU contention or insufficient memory.
Old disk-exhaustion failures are excluded from new-failure detection. Concurrency
changes can affect wall-limited results and must accompany published timing data.

8 fresh resource-policy tests and Ruff PASS. Existing two scientific supervisors
stayed alive; the third campaign completed and resumed one-job slices. Verified
pre-change external snapshot and initial metadata BOM correction are documented
in HANDOFF.md. Live validation: `var/paper-parallel/three-slot-verification.json`.

# Follow-up 2026-10-24: explicit extra-budget reruns

User authorized rerunning failed and campaign-budget-limited states. Initial
supplemental index contains 21 shards, 590 target job keys (557 missing, 33 failed)
and 28 extra paired-fold jobs. All job keys/input hashes match original plans;
original data and configurations are retained. Per-job budgets are unchanged,
while additional campaign budgets are explicitly recorded for each new namespace.
X6+RECOVERY runs before X3 with the existing adaptive concurrency cap. Future
budget omissions and newly failed original jobs are discovered when campaigns end.
Deterministic failures get one explicit follow-up, not endless identical retries.

Coverage manifest separates original records, follow-up outcomes and 4276 unique
primary jobs. Supplemental reports remain separate to avoid pooling duplicate
keys or hiding historical failures. Dashboard excludes paired duplicates from its
overall progress. Latest ownership/logs and fresh 11-test verification are in
HANDOFF.md; index/configs and coverage are under `var/paper-parallel/recovery/`.

