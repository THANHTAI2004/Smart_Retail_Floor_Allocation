# Thực nghiệm nghiên cứu

Thư mục chính duy nhất hiện tại là `E:\Smart_Retail_Floor_Allocation\experiments`.
Toàn bộ nội dung trước đây ở `thuc_nghiem` đã được đổi tên vào đây. Xem
[vị trí dữ liệu và hướng dẫn chạy](VI_TRI_DU_LIEU.md). Các đường dẫn lịch sử
trong artifact, biên nhận và báo cáo cũ được giữ nguyên để bảo toàn checksum.

Campaign runner dùng MongoDB riêng, production durable queue và process worker
có timeout, memory budget, snapshot/runtime/checksum. Chạy từ thư mục root.
Output phải là đích mới; không ghi đè kết quả, checkpoint hay scientific artifacts.

```powershell
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/pilot.json --output experiments/results/my-new-pilot
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli verify experiments/results/my-new-pilot
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli analyze experiments/results/my-new-pilot --output experiments/reports/my-new-pilot
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli replay experiments/results/my-new-pilot --output experiments/results/my-new-replay
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli compare experiments/results/my-new-pilot experiments/results/my-new-replay --output experiments/reports/my-new-comparison.json
```

`resume` nhận `--config` và `--output` của campaign paused, từ chối source/config
drift và giữ attempt identity. `verify` chỉ kiểm tra integrity, không chạy solver.
Chỉ dùng `replay` trong môi trường source/dependency tương thích.

Có 16 JSON configs bao phủ E01–E15, chưa đồng nghĩa mọi ma trận đã chạy đầy đủ.
Dữ liệu và holdout đều tổng hợp. Xem [README tổng thể](../README.md),
[trạng thái nghiên cứu](../docs/research/RESEARCH_STATUS.md),
[mô hình joint](../docs/research/JOINT_OPTIMIZATION_FORMULATION.md) và
[kiểm chứng campaign](../docs/system-audit/EXPERIMENT_VALIDATION.md).

Các kết quả nguyên bản không thuộc phạm vi vận hành hiện hành được định vị tại
[hồ sơ lưu trữ bên ngoài](../docs/architecture/HISTORICAL_ARCHIVE.md).

## Lặp k-fold trên đơn hàng (2026-10-23, campaign schema 1.1)

Thiết kế: [EXPERIMENT_DESIGN_DEEPMG.md](../docs/research/EXPERIMENT_DESIGN_DEEPMG.md).
Thêm khối `"evaluation": {"split": "kfold", "n_folds": 10}` (hoặc
`"temporal_holdout"` với `test_size`) và `"schema_version": "1.1"`. Mỗi seed là một
lượt lặp; mỗi phương pháp chạy trên cùng các fold. Dùng `facings` ≥ 4 để ràng buộc
sức chứa có hiệu lực và cho mọi phương pháp cùng một định nghĩa hàm mục tiêu.

```powershell
# Pilot: 2 instance x 4 phương pháp x 1 lượt x 10 fold = 80 job
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/pilot_cv.json --output experiments/results/<thư-mục-mới>
# Thiết kế > 1.000 job: tách, chạy từng phần, rồi phân tích gộp
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli split-config --config <thiết-kế>.json --output-dir experiments/configs/<thư-mục-mới>
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze experiments/results/<phần-1> experiments/results/<phần-2> --output experiments/reports/<thư-mục-mới>
```

Báo cáo có thêm `fold_results.csv`, `run_means.csv`, `status_matrix.csv`,
`rankings.csv`; `statistics.json` có Wilcoxon, Nadeau–Bengio, A12, bootstrap CI,
Friedman/Nemenyi. Hướng dẫn chạy đợt thực nghiệm bài báo:
[PAPER_EXPERIMENT_RUNBOOK.md](../docs/research/PAPER_EXPERIMENT_RUNBOOK.md).
