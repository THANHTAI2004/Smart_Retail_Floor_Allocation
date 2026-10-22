# Tái cấu trúc trực tiếp tại thư mục gốc — 21/10/2026

Yêu cầu tái xây dựng trong tệp người dùng gửi thay thế nhiệm vụ tiếp tục V4 theo
gate trước đây. Không tạo repository mới, không dùng thư mục V2 đang tồn tại,
không reset/clean/stash/stage/commit/push. `.git` vẫn ở vị trí cũ.

## Kiểm kê và snapshot

- Nhánh: `main`; HEAD ban đầu: `2cbce4751f5fea6cd2ea30dffc0a198d60a34187`.
- Trước phiên này: `AGENTS.md` và nhiều artifact `.playwright-mcp` đã bị xóa;
  README/HANDOFF đã có chỉnh sửa; có dữ liệu runtime và tài liệu chưa track.
- Snapshot: `C:\Users\admin\Documents\SmartRetailBackups\20261021-rebuild-00301a95`.
- `snapshot.zip`: toàn bộ cây thực tế lúc bắt đầu, kể cả `.git`, ignored/untracked,
  môi trường Python, dữ liệu nghiên cứu và kết quả.
- `manifest.json`: SHA-256 cho 58.862 mục, 7.743.411.608 byte tệp thông thường;
  24 symlink được lưu bằng loại Unix symlink và nguyên văn đường dẫn đích.
- `VERIFIED.json`: toàn bộ nội dung archive đã được đọc lại và đối chiếu SHA-256;
  thời gian tạo + xác minh 636,23 giây.
- `git-status.txt`, `git-diff.patch`, `git-index.patch`, `git-log.txt`: trạng thái
  trước di chuyển, gồm diff nhị phân của thay đổi có sẵn.

## Di chuyển và bảo tồn

Sau khi snapshot qua kiểm chứng, chuyển nguyên `smart-retail-layout` sang
`D:\04_Archives\SmartRetail\20261021-retired-source-358740e0` bằng di chuyển
cùng ổ D:. Không xóa tệp bên trong. Đây là nguồn tham chiếu nghiên cứu bên ngoài
cây ứng dụng; hệ thống mới không import, gọi lệnh hoặc dùng môi trường của nó.
Các symlink fixture có đường dẫn tuyệt đối cũ vẫn giữ nguyên đích như lúc snapshot.

`de-cuong`, `docx`, `Retail_TestPack`, `HANDOFF.html`, `HANDOFF_files` được bảo
toàn tại chỗ vì là tài liệu/dữ liệu có sẵn. Chưa phân loại chúng thành dữ liệu đầu
vào chính thức của hệ thống mới. HANDOFF lịch sử được giữ nguyên phía sau con trỏ
mới; README cũ có thể khôi phục từ snapshot. Không chuyển bằng chứng V4 cũ thành
bằng chứng chấp nhận engine mới.

Mã mới được chuẩn bị tạm bên ngoài dự án trong lúc backup, sau đó chép vào
`frontend/`, `backend/`, `datasets/` tại thư mục gốc. Không có repository con.

## Khôi phục

Đọc hướng dẫn `RESTORE.md` và `restore_snapshot.py` bên cạnh snapshot. Khôi phục
vào một thư mục trống bằng Python; chương trình không ghi đè tệp đã có và kiểm tra
SHA-256 trước khi xuất. Muốn hoàn nguyên đúng đường dẫn gốc, trước hết phải dừng
dịch vụ và bảo toàn cây mới ra ngoài; không giải nén đè lên công việc mới.

Snapshot còn chứa toàn bộ `.git` trước tái cấu trúc. Không cần Git reset để truy
cập hoặc phục hồi nội dung chưa commit.
