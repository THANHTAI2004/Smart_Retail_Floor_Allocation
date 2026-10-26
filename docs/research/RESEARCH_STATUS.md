# Phạm vi và trạng thái nghiên cứu

Mốc cập nhật 23/10/2026: hạ tầng repeated k-fold/temporal holdout, đánh giá trên
đơn hàng giữ lại, Nadeau–Bengio/Wilcoxon/Friedman/Nemenyi và xuất deepmg đã có
trong source. Bộ bài báo gồm 20 cấu hình paper-v2 với 4.276 job đã được validate;
lượt mới bắt đầu lúc 13:35:59 UTC+7, đang chạy, chưa có kết luận toàn bộ.
Kiểm chứng source mới: 198 pytest, 4 Vitest, lint/build frontend, Ruff, mypy và
kiến trúc đều đạt. Xem [biên bản tiếp tục](CONTINUATION_20261023.md),
[thiết kế](EXPERIMENT_DESIGN_DEEPMG.md) và mục đầu [HANDOFF](../../HANDOFF.md).
Những mô tả và số liệu ngày 22/10 ở dưới là lịch sử trước phần mở rộng này.

Mốc 13:45 UTC+7: X1 đã hoàn tất 150/150 job thành công, kiểm tra độc lập và
integrity đạt PASS; 60 job exact/hybrid có chứng nhận trong miền hữu hạn, cùng
điểm theo từng seed. [Báo cáo X1](../../experiments/reports/20261023-paper-v2/X1/summary.md).
Runner đã chuyển sang X4 Tiny; chưa có kết luận cho toàn bộ 4.276 job.

Nguồn hiện hành dùng MongoDB/PyMongo. Có 16 cấu hình JSON cho E01–E15 trong
`experiments/configs/`, generators có Tiny/Small/Medium/Large và provenance
SYNTHETIC. Cấu hình tồn tại không đồng nghĩa đã chạy đủ mọi scale/seed.

Audit ngày 22/10/2026 ghi nhận 38 pilot jobs và replay, 10 joint jobs và replay,
cùng kiểm tra số học giới hạn. Đây là bằng chứng thực thi và tái lập trong phạm
vi tổng hợp, không phải bằng chứng hiệu quả tại cửa hàng hoặc nghiên cứu Large.
Các kết quả cũ trên môi trường khác được giữ nguyên ngoài checkout; không dùng
chúng như kiểm chứng mới cho source hiện tại.

Xem [mô hình joint](JOINT_OPTIMIZATION_FORMULATION.md),
[hướng dẫn joint](HOW_TO_RUN_JOINT_OPTIMIZATION.md),
[thực nghiệm đã kiểm chứng](../system-audit/EXPERIMENT_VALIDATION.md) và
[README](../../README.md) để biết mô hình toán, lệnh run/replay/compare và giới hạn.

Thống kê dùng mô tả, khoảng tin cậy t, ghép cặp theo seed và điều chỉnh Holm
khi đủ mẫu không suy biến. Repetition cùng seed được gộp trước khi ghép cặp.
Giữ mọi thất bại trong mẫu số completion; không gán KPI giả cho job thất bại.
