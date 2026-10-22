# Hướng dẫn chạy thí nghiệm

E11–E15 và các chế độ joint feedback/exact/hybrid được hướng dẫn riêng tại
[HOW_TO_RUN_JOINT_OPTIMIZATION.md](HOW_TO_RUN_JOINT_OPTIMIZATION.md).

Thực hiện từ `D:\Smart_Retail_Floor_Allocation`. Dữ liệu tự sinh được ghi rõ
`SYNTHETIC`; kết quả không phải kiểm chứng thực địa. Cần Python 3.12 và Node tương
thích README nếu sử dụng dashboard. Mọi đường dẫn output dưới đây phải chưa tồn tại.

## Cài đặt

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1
```

Dependency Python/Matplotlib được khóa trong `backend/requirements-lock.txt`;
frontend dùng `package-lock.json`. Không dùng môi trường của mã đã nghỉ.

## Chọn và kiểm tra dataset

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli generate --scale tiny --scenario feasible --seed 101 --output datasets/generated/my-tiny
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli validate-dataset datasets/generated/my-tiny
```

Có Tiny, Small, Medium, Large; các kịch bản `feasible`, `infeasible`, `high_load`,
`volatile`, `uneven`. Manifest ghi nguồn, phiên bản, đơn vị, kích thước và checksum.
`feasible` mô tả thiết kế dữ liệu; chỉ nghiệm qua solver/replay mới là bằng chứng
khả thi. Không xem test kích thước lớn là lời hứa mọi solver đều giải được.

## Chạy pilot và campaign

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/pilot.json --output experiments/results/my-pilot
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli status experiments/results/my-pilot
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli verify experiments/results/my-pilot
```

Sau khi kiểm tra pilot, dùng `experiments/configs/main.json`. Các cấu hình riêng
gồm `algorithm_comparison`, `sensitivity`, `ablation`, `scalability`, `robustness`.
Chạy E01–E08 trước khi mở rộng robustness. Config chứa câu hỏi, giả thuyết,
baseline/treatment, dataset, seed, metrics, ngưỡng kiểm chứng, số lần lặp và ngân sách.

`--max-new-jobs 1` tạo checkpoint có chủ đích để thử resume. Tiếp tục bằng:

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli resume --config experiments/configs/pilot.json --output experiments/results/my-pilot
```

Resume kiểm source/dependency/config và checksum; giữ nguyên job hoàn tất hợp lệ.
Nếu đổi mã hoặc cấu hình, tạo campaign mới. Nếu worker lease chưa rõ trạng thái,
runner từ chối chạy trùng; kiểm process và artifact trước khi xử lý. Tổng ngân sách
campaign được cộng dồn qua resume. Job chưa chạy do giới hạn tài nguyên được ghi
rõ, không tự đổi giới hạn hoặc bỏ qua.

## Chạy riêng từng tầng

Trong treatment overrides, đặt `optimization.stop_after_stage` là `T1`, `T2`,
`T3` hoặc `T4`. Những tầng tiền đề cần thiết vẫn chạy hoặc được lấy từ cache đúng
hash. Thay input chỉ tính lại phần phụ thuộc; artifact cũ không bị ghi đè.

Thuật toán: T1 `grid`/`local_search`; T2 `greedy`/`milp`; T3 `first_fit`/`milp`;
T4 `nearest`/`return`/`exact`. Exact routing giới hạn 10 vị trí phục vụ mỗi hành trình.

## Phân tích và xuất kết quả

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze experiments/results/my-pilot --output experiments/reports/my-pilot
```

Mở `summary.md`, `results.csv`, `statistics.json`, `comparisons.csv`,
`failures.csv`, `manifest.json` và `figures/`. Hình PNG/SVG do Matplotlib sinh từ
run đã ghi nhận. RSS/CPU là số đo process con; wall time có cả startup. Không loại
failure khỏi mẫu một cách âm thầm. CI theo seed trên fixture không phải CI cho
toàn bộ cửa hàng thực tế; không diễn giải p-value thành chứng nhận readiness.

## Replay và so sánh

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli replay experiments/results/my-pilot --output experiments/results/my-replay
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli compare experiments/results/my-pilot experiments/results/my-replay --output experiments/reports/my-comparison.json
```

Phân biệt `byte_identical_result` với `numerically_equivalent` (absolute tolerance
1e-8, relative tolerance 1e-9). Thời gian/RSS/cache-hit nằm trong telemetry riêng,
không được sửa để ép kết quả khoa học khớp. Không cam kết byte giống nhau giữa
solver, hệ điều hành hoặc dependency khác.

## Dashboard

Dataset tùy chỉnh dùng `input_path` bên trong `datasets/` và
`input_file_sha256` trong DatasetSpec; hai trường phải có cùng nhau. Bundle chứa
đúng bảy nhóm schema hợp lệ và đều ghi `data_origin: SYNTHETIC`. Runner xác minh
SHA-256 file gốc và snapshot chuẩn hóa, giữ nguyên dữ liệu đầu vào.

Mặc định `cache_policy: isolated` để các nhánh benchmark có điều kiện cache độc
lập; chọn `reuse` rõ ràng nếu nghiên cứu khả năng tái sử dụng cache. Kế hoạch bị
chặn ở 1.000 job, một worker; ngân sách `max_jobs` và `max_wall_s` không được
đặt lại khi resume. Job đã hoàn tất hợp lệ được giữ nguyên, source/dependency đổi
thì resume bị từ chối. Xem cấu hình thực tế để dùng đúng tên trường ngân sách.

Đã kiểm tra một venv Python mới tại `var/clean-python-20261022`: cài lock và package
editable với `--no-deps`, `pip check` đạt, replay pilot khớp 19/19 input/result SHA.
Đây là môi trường Python mới trên cùng máy Windows, chưa phải kiểm chứng hệ điều
hành hoặc solver khác. Chi tiết và đường dẫn cuối cùng trong
[kết quả 22/10](RESULTS_20261022.md).

Chạy `scripts/start.ps1`, mở http://127.0.0.1:5173/#research. Chọn cấu hình,
experiment, dataset, số seed và thuật toán theo nhánh; bắt đầu, theo dõi, hủy,
resume hoặc replay. Bảng và biểu đồ chỉ xuất hiện từ runner thật. Có thể tải CSV,
JSON, SVG, báo cáo và manifest. CLI hoạt động độc lập, không cần mở trình duyệt.
