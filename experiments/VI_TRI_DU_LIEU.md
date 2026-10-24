# Hồ sơ thực nghiệm Smart Retail

## Chạy dự án trên E

Mở workspace `E:\Smart_Retail_Floor_Allocation\Smart_Retail_E.code-workspace`
trong VS Code. Python và terminal được cấu hình dùng thư mục dự án hiện tại.

Ứng dụng: http://127.0.0.1:5173 — API: http://127.0.0.1:8010/api/health.
Bảng tiến độ xác minh thực nghiệm: http://127.0.0.1:8766.

Khi dịch vụ chưa chạy, khởi động từ PowerShell:

```powershell
Set-Location -LiteralPath 'E:\Smart_Retail_Floor_Allocation'
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start.ps1
```

Để dừng các dịch vụ ứng dụng do dự án này quản lý, dùng `scripts/stop.ps1`.
Lệnh đó không dừng bộ xác minh kết quả thực nghiệm riêng đang chạy nền.

Thư mục chính của toàn bộ đợt thực nghiệm là:

```text
E:\Smart_Retail_Floor_Allocation\experiments
```

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `configs/` | Cấu hình và ma trận thực nghiệm gốc |
| `results/` | Đầu vào bất biến, kế hoạch, checkpoint, artifact và bản ghi từng job |
| `reports/` | Báo cáo, bảng CSV, biểu đồ và thống kê đã xuất |
| `visualization/` | Các hình và công cụ trực quan hóa đã có |
| `docs/research/` | Thiết kế, giả thuyết, mô hình và hướng dẫn nghiên cứu |
| `scripts/` | Công cụ điều phối, chạy bù, thống kê và giám sát |
| `runtime/var/` | Nhật ký, trạng thái điều phối, bằng chứng lỗi và nguồn đã đóng băng |
| `runtime/external/` | Hồ sơ khôi phục ổ đĩa, các lần bàn giao và trạng thái bảng tiến độ |
| `databases/` | Bản xuất BSON có kiểm chứng của các cơ sở dữ liệu campaign |
| `migration/` | Biên bản, checksum và công cụ phục vụ lần gom thư mục này |

## Báo cáo đọc nhanh

[Thống kê kết quả bằng tiếng Việt](reports/20261023-paper-v2/user-statistics-20261024T064920Z/THONG_KE_KET_QUA.md).

Đã có kết quả cho 4.276 job duy nhất. Theo kết quả chạy lại đã được yêu cầu:
4.228 thành công và 48 thất bại tìm cách xếp hàng bằng first-fit. Kết quả gốc,
kết quả chạy lại và fold đi kèm được giữ riêng để tránh đếm trùng.

## Đường dẫn cũ và bản sao khôi phục

`experiments/` là thư mục dữ liệu thật và là tên chính duy nhất. Thư mục
`thuc_nghiem/` đã được gộp bằng cách đổi tên, không còn tồn tại trong dự án E.
`docs/research/` và các thư mục runtime cũ vẫn là liên kết đến vị trí tương ứng
trong `experiments`. Những liên kết này giữ các lệnh và đường dẫn đã ghi trong
tài liệu cũ hoạt động. Các tệp công cụ ở `scripts/` có đường dẫn
cũ được giữ làm hard link; nên chỉnh sửa và chạy công cụ tại `experiments/scripts/`.

Dữ liệu được đưa từ C vào D được nén NTFS trong suốt: mở tệp như bình thường,
nội dung và SHA-256 không thay đổi. Bản gốc ngoài dự án được giữ làm bản sao
khôi phục tại:

```text
C:\Users\admin\Documents\SmartRetailBackups\20261024-consolidation
```

Đây là vị trí bản sao khôi phục trước di chuyển. Theo yêu cầu dọn dung lượng
ngày 24/10, các tệp tại đây có bản trùng SHA-256 đã xác minh trên E đang được xóa.
Những phiên bản khác hoặc chưa chứng minh được bản tương ứng trên E được giữ lại.
Xem trạng thái và biên nhận tại `migration/duplicate-cleanup/`. Không dùng các bản
cũ trên C/D làm thư mục chạy dự án; vị trí làm việc chính là dự án trên E.

## Cơ sở dữ liệu

`databases/manifest.json` chứa checksum và kết quả kiểm tra đọc lại của các bản
xuất BSON. Cơ sở dữ liệu chính và dịch vụ MongoDB đang chạy không bị di chuyển
hoặc khởi động lại. Các namespace campaign còn được giữ trong MongoDB để khôi phục.

Tên database campaign được tính từ đường dẫn thực đã resolve. Sau khi đổi vị trí,
không tự ý resume campaign đã hoàn tất vào một namespace rỗng mới. Xem
`databases/namespace-map.json` và phục hồi bản BSON vào namespace phù hợp nếu cần
thực hiện một đợt tiếp tục riêng. Phân tích báo cáo và kiểm tra checksum tệp không
cần thay đổi namespace database.

## Trạng thái xác minh cuối

Phần tính toán đã kết thúc. Bộ xác minh được tạm dừng trong lúc di chuyển dữ liệu
và được tiếp tục sau khi kiểm tra vị trí mới. Không coi việc gom thư mục là biên
nhận đã hoàn tất toàn bộ xác minh nghiên cứu hoặc sao lưu cuối; kiểm tra trạng thái
mới nhất trong `runtime/var/paper-unattended/`.
