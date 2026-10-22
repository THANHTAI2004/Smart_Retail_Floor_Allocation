> Historical checkpoint: 2026-10-21. For the current 2026-10-22 implementation, use [model scope](MODEL_SCOPE_20261022.md), [ER readiness](EXPERIMENT_READINESS_MATRIX.md), and [actual results](RESULTS_20261022.md). The historical gates and limits below are not the current synthetic-readiness assessment.

# Ma trận nghiệm thu — 21/10/2026

**Trạng thái chung: `RESEARCH_ACCEPTANCE_INCOMPLETE`.**

Không công bố `SOFTWARE_RESEARCH_READY` hoặc `REAL_WORLD_VALIDATED`. Ma trận giữ phạm vi master prompt; các chứng minh cho mô hình hẹp không tự đóng gate rộng hơn. `FAIL` thể hiện phần còn thiếu, kể cả khi các test hiện có đều qua. `BLOCKED` chỉ rõ thiếu môi trường hoặc bằng chứng bên ngoài.

| Gate | Trạng thái | Bằng chứng mới | Phần thiếu / hành động tiếp theo |
|---|---|---|---|
| 01 Architecture | PASS | [Audit dependency/cycle](evidence/20261021/architecture.json), [test boundaries](../../backend/tests/unit/test_architecture.py), [kiểm thử](evidence/20261021/pytest.xml) | Backend và frontend độc lập, không dependency legacy; tiếp tục tách App để giảm độ lớn module |
| 02 Input Data | FAIL | Bảy schema/fixture; 19 test mới kiểm schema đồng bộ, fixture lỗi và cấu hình; [manifest](../../datasets/manifest-research-v1.json) | Chưa có version trong từng envelope; còn trường chuyên sâu, form lồng orders/levels, giờ nhu cầu và vùng chức năng |
| 03 T1 | FAIL | Geometry replay, deterministic variants, [E01/E05](../../experiments/results/20261021-research-02/analysis.json) | Chưa kiểm toàn mạng lối đi liên thông, cửa ra/vùng chức năng; chưa nghiệm thu đầy đủ phạm vi T1 |
| 04 T2 | FAIL | HiGHS/greedy, reference enumeration, replay assignment/objective độc lập | Chưa category splitting, soft affinity và các mục tiêu phân bổ mở rộng |
| 05 T3 | FAIL | MILP strip với reference optimum 14, first-fit đối chứng; replay orientation/width/depth/layers/facings/load/overlap; E03 | Mô hình hiện cố định facings, một khối/SKU; chưa hỗ trợ min/max facings và toàn phạm vi planogram yêu cầu |
| 06 T4 | FAIL | Mặt lấy hàng từ T3; route points, connector cửa, quantities; audit từng đoạn/độ dài/thời gian | Chưa picker pool, routing policy comparison, nhu cầu theo giờ hoặc hiệu chuẩn; không phải crowd dynamics |
| 07 Integrated Workflow | FAIL | Bounded 1–8 candidates, score chuẩn hóa, tập không bị trội, cache theo nội dung trong run; [E2E](evidence/20261021/playwright-results.json) | Chưa generic partial rerun, persistent cache, retry hữu hạn và cơ chế feedback đầy đủ |
| 08 Reproducibility | FAIL | Snapshot/runtime/hash/seed, 80 receipts; replay run mới có cùng input/result hash; [audit](../../experiments/results/20261021-research-02/analysis.json) | Thiếu contract/model version trong từng envelope và audit start/end đầy đủ cho mọi API run |
| 09 Experiments | FAIL | E01–E08: 80 job, 5 seed/nhánh, giữ cả failure; [protocol](EXPERIMENT_PROTOCOL.md) | Mới là smoke nhỏ; thiếu sweep/factorial/robustness/scalability và memory benchmark đủ rộng |
| 10 Statistics | FAIL | Mean/SD/t CI, paired differences, exploratory p/Holm, test đường zero variance và failure | Chưa power/design đại diện; không dùng 5 seed một fixture để kết luận quần thể |
| 11 Software Quality | PASS | [86 pytest](evidence/20261021/pytest.xml), [6 E2E](evidence/20261021/playwright-results.json), [axe](evidence/20261021/playwright-axe-results.json), [lệnh/check](evidence/20261021/verification.json), [dependency audit](evidence/20261021/npm-audit.json) | PASS cho nguồn hiện tại trên Windows/SQLite; không thay bằng chứng PostgreSQL/clean deployment ở gate 13 |
| 12 Documentation | PASS | Đủ 15 tài liệu nghiên cứu ở thư mục này, công thức theo mã thực, kết quả/failure/giới hạn, README và HANDOFF cập nhật | Tiếp tục cập nhật cùng milestone; không dùng tài liệu làm thay chứng minh thuật toán |
| 13 Deployment | BLOCKED | Local app/worker online; SQLite upgrade/check/downgrade/upgrade qua; [health](evidence/20261021/live-health.json) | `BLOCKED_ENVIRONMENT`: docker/psql không có trên PATH; chưa có PostgreSQL disposable, Compose runtime, clean install hoặc CI remote |
| 14 Research Evidence | BLOCKED | Synthetic manifest, hash, seed, independent replay đầy đủ cho campaign này | `BLOCKED_EXTERNAL_EVIDENCE`: chưa S05 đo đạc, S06 nguồn/quyền sử dụng, S07 số đo SKU/kệ để đạt kiểm chứng thực tế |

Thứ tự phụ thuộc tiếp theo: versioned input contract → T1 topology/functional zones và T2/T3 mở rộng → T4 pool/hourly/routing → partial rerun/retry/cache → thiết kế thí nghiệm rộng → kiểm chứng môi trường sạch. Dữ liệu thực và PostgreSQL có thể được chuẩn bị song song, không thay thế phần kỹ thuật còn thiếu.

Chiến dịch bị ngắt `research-01` được giữ nguyên. `research-02`: 75 run thành công, 5 first-fit `SLOTTING_FAILED` có chủ đích ở E03. Đây là kết quả thuật toán được giữ để so sánh; bộ kiểm thử phần mềm có 0 failure.
