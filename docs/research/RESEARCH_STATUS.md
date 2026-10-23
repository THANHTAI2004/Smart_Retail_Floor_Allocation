# Phạm vi và trạng thái nghiên cứu

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
