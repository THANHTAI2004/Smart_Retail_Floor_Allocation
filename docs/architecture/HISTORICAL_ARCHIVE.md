# Hồ sơ lưu trữ ngoài dự án

Ngày 23/10/2026, người dùng yêu cầu tài liệu hiện hành chỉ mô tả hệ thống MongoDB
đang triển khai và giữ bằng chứng lịch sử trong bản lưu bên ngoài dự án.

Bản lưu đã được đọc lại và xác minh trước khi chuyển bất kỳ tệp nào:

```text
C:/Users/admin/Documents/SmartRetailBackups/20261023-documentation-cleanup-c0a98c35/
  tracked-before.zip
  manifest.json
  relocation-plan.json
  historical-files/
```

Archive ban đầu chứa 1.664 tệp được Git quản lý. `manifest.json` ghi SHA-256
của từng tệp và toàn bộ archive; mọi mục trong ZIP đã được đọc lại và so sánh.
Các tệp chuyển ra được kiểm tra SHA-256 trước và sau khi chuyển.

Đây là bản sao của tệp dự án, không phải bản sao nhất quán của cơ sở dữ liệu
đang chạy. Dữ liệu MongoDB, các kết quả nghiên cứu không thuộc danh sách chuyển,
dịch vụ chính, Git HEAD và Git index được giữ nguyên trong công việc này.
Các bản sao an toàn có thể chứa cấu hình và bằng chứng riêng tư; không công bố.

Những liên kết bằng chứng cũ được chuyển sang trang này để không trỏ tới tệp
đã rời checkout. Muốn đọc một hồ sơ cụ thể, tra đường dẫn tương đối trong
`relocation-plan.json`, sau đó mở đúng tệp trong `historical-files/` hoặc ZIP.
Không coi bản tóm lược tài liệu sau biên tập là một lần kiểm chứng mới.
