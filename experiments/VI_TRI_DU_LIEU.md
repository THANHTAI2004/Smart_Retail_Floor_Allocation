> Cập nhật 10/11/2026: Đã xoá kết quả, báo cáo, checkpoint và nhật ký campaign V3/V4 trong checkout này; không resume/replay từ đầu ra đã xoá. Đã xoá 225 database `sr_campaign_`, giữ nguyên 775 database khác. Cấu hình, mã nguồn và tài liệu nghiên cứu được giữ nguyên. Còn 39 tệp ZIP/metadata cũ (1.727.996.185 byte) trong `var/github-publication` do lệnh xoá trước bị kiểm duyệt chặn. Bản lưu ngoài checkout không thuộc lần xoá này. Biên nhận: `var/experiment-cleanup-20261110/`.

# Thư mục thực nghiệm sau khi xoá kết quả cũ

Cập nhật 26/10/2026. Thư mục thực nghiệm của dự án là
`D:\Smart_Retail_Floor_Allocation\experiments`.

Kết quả và các tệp phát sinh từ các đợt thực nghiệm cũ đã được xoá theo yêu cầu,
không tạo bản sao lưu mới. Các thư mục `results/`, `reports/`, `runtime/`,
`databases/`, `migration/` và `.migration-staging/` không còn dữ liệu cũ.
Bảng tiến độ cũ không chạy; các liên kết runtime cũ trong `var/` đã được gỡ.

Các thành phần được giữ lại:

| Thư mục | Nội dung |
|---|---|
| `configs/` | Cấu hình và thiết kế thực nghiệm để chạy mới |
| `scripts/` | Công cụ điều phối, phân tích và giám sát |
| `visualization/` | Mã nguồn vẽ biểu đồ |
| `docs/research/` | Thiết kế, mô hình, giả thuyết và hướng dẫn nghiên cứu |

Xem [hướng dẫn chạy campaign mới](README.md). Các thư mục đầu ra sẽ được
tạo khi chạy mới. Không resume hoặc replay từ các đường dẫn kết quả đã xoá.

MongoDB đã xoá 249 database riêng có tiền tố `sr_campaign_`; các database khác
được giữ nguyên. Dịch vụ MongoDB khởi động tạm để thực hiện việc này đã dừng.

39 tệp ZIP, ZIP dở dang, metadata ZIP và inventory của lần xuất cũ trong
`var/github-publication` vẫn còn: cơ chế kiểm duyệt tự động chặn lệnh xoá.
Biên nhận nằm trong `var/old-experiment-cleanup/`; đây là nhật ký thao tác,
không chứa bản sao kết quả. Các bản lưu ngoài checkout không thuộc lần xoá này.
