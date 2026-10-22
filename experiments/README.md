# Thực nghiệm nghiên cứu

Runner dùng production durable queue, SQLite riêng, process worker với timeout,
snapshot/runtime/checksum. Không dùng engine hoặc bằng chứng V4 cũ.

```powershell
.venv\Scripts\python.exe experiments/run_campaign.py --output experiments/results/my-new-campaign --seeds 11,23,37,53,71
.venv\Scripts\python.exe experiments/analyze_campaign.py experiments/results/my-new-campaign
```

Chạy từ root. Output phải là thư mục mới; không ghi đè kết quả cũ. `--replay
<input.json>` chạy lại snapshot nếu source/dependency identity khớp.

- `results/20261021-research-01`: bị ngắt bởi Windows sharing violation khi đọc
  progress; giữ nguyên, không coi là chiến dịch hoàn tất.
- `results/20261021-research-02`: 80 job, 5 seed/nhánh, 75 thành công và 5 first-fit
  thất bại có chủ đích ở E03. Có configuration, database, snapshot/result/receipt,
  raw runs, summary và independent audit/paired statistics.
- `results/20261021-replay-01`: run ID mới, input/result hash giống lượt gốc.

E01–E08 hiện là smoke **SYNTHETIC** nhỏ; chưa đủ nghiệm thu robustness,
scalability hoặc hiệu quả tổng quát. Peak child memory chưa instrument, ghi null.
Xem [protocol](../docs/research/EXPERIMENT_PROTOCOL.md),
[tái lập](../docs/research/REPRODUCIBILITY.md),
[ma trận gate](../docs/research/ACCEPTANCE_MATRIX.md).
