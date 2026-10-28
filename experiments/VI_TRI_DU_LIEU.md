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
