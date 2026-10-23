# Thực nghiệm nghiên cứu

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
