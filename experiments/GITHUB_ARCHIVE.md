# Dữ liệu thực nghiệm trên GitHub

Mã nguồn, cấu hình, tài liệu và báo cáo được lưu trong nhánh `main` của
[Smart_Retail_Floor_Allocation](https://github.com/THANHTAI2004/Smart_Retail_Floor_Allocation).

Bản chụp toàn bộ các tệp dữ liệu trong `experiments/` tại thời điểm kiểm kê ngày
24/10/2026 được đóng gói tại
[Releases: experiments-2026-10-24](https://github.com/THANHTAI2004/Smart_Retail_Floor_Allocation/releases/tag/experiments-2026-10-24).
Đợt tải lên chỉ hoàn tất khi release hết trạng thái draft và biên nhận cục bộ
`var/github-publication/status.json` có `status: COMPLETE`.

Các gói gồm kết quả gốc, bản xuất cơ sở dữ liệu, runtime thực nghiệm, cấu hình,
báo cáo, mã nguồn thực nghiệm và biên nhận di chuyển có trong thời điểm kiểm kê.
Các tệp nhật ký đang mở được chụp tới kích thước khi bắt đầu đọc; báo cáo được
sinh sau thời điểm kiểm kê không thuộc bản chụp này. Tệp mật, khóa riêng,
bytecode và liên kết tạm của pytest được liệt kê riêng trong manifest.

Tải `ARCHIVE_MANIFEST.json`, `SHA256SUMS` và tất cả `experiments-*.zip`.
Mỗi ZIP độc lập: giải nén tất cả vào thư mục gốc của bản clone, giữ cấu trúc
`experiments/...`. Mỗi ZIP có `ARCHIVE_CONTENTS.json` chứa SHA-256 từng tệp;
`SHA256SUMS` chứa SHA-256 các ZIP. Có thể kiểm tra một ZIP bằng PowerShell:

```powershell
Get-FileHash .\experiments-0001.zip -Algorithm SHA256
```

Đối chiếu với `SHA256SUMS` trước khi giải nén. Các đường dẫn ổ C/D/E trong kết quả
lịch sử được giữ nguyên để bảo toàn checksum. Máy khác cần cài môi trường theo
README của dự án; `.venv`, `node_modules` và thông tin đăng nhập không được phát hành.

Lệnh đóng gói/tải lên có khả năng tiếp tục:

```powershell
.venv/Scripts/python.exe scripts/publish_experiment_archive.py
```

Lệnh cần GitHub CLI ở `var/github-tools/gh/bin/gh.exe` và tài khoản Git Credential
Manager `THANHTAI2004`. Tiến độ, log và các ZIP đã kiểm tra nằm trong
`var/github-publication/`. Script không xóa hay chạy lại dữ liệu gốc. Mỗi ZIP
được giải nén đọc lại và so khớp SHA-256 từng tệp trước khi tải lên; sau tải lên,
script đối chiếu kích thước và SHA-256 do GitHub trả về trước khi xuất bản release.
