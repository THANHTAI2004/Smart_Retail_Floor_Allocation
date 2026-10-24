# Đối chiếu dự án từ D sang E — 24/10/2026

## Kết luận

Mã nguồn, cấu hình, tài liệu và dữ liệu thực nghiệm chính đã có trên E. Tuy nhiên,
bản E chưa phải bản sao toàn bộ từng tệp của D: thiếu 5.481 tệp kiểm thử đường dẫn
dài (69.930.056 byte), thiếu 229.824 đối tượng Git rời không thuộc các refs hiện
có, và một số launcher trong môi trường Python sao chép còn chạy môi trường D.

Đây là rà soát chỉ đọc; không chép bù, xóa hoặc ghi đè các khác biệt. Bộ xác minh
thực nghiệm đang chạy trên E không bị dừng. Báo cáo và script rà soát là các tệp
mới được tạo trên E.

## Mã nguồn và tài liệu

Đối chiếu 1.784 tệp được Git quản lý: không thiếu tệp nào trên E; 1.782 tệp khớp
SHA-256. Hai khác biệt là `.gitignore` và `HANDOFF.md`, đã được cập nhật cho việc
chuyển ổ. Trong đó có 131 tệp backend, 60 tệp frontend, 19 tệp datasets, 337 tệp
docs, 1.207 tệp dưới đường dẫn experiments và 21 tệp scripts.

Kiểm tra thêm các tệp nguồn/tài sản ở vị trí vật lý, bỏ qua cache và thư mục liên
kết trùng dữ liệu: 789 tệp có ở cả hai bản; 785 khớp SHA-256. Bốn khác biệt là
`.gitignore`, `HANDOFF.md`, `thuc_nghiem/VI_TRI_DU_LIEU.md` và
`thuc_nghiem/scripts/paper_progress/server.py`; đều liên quan đến chuyển đường dẫn
hoặc hướng dẫn hiện hành. Không phát hiện khác biệt mã thuật toán backend/frontend.

## Dữ liệu và kết quả thực nghiệm

| Nhóm | Tệp trên D | Tệp trên E | Tổng byte D/E |
|---|---:|---:|---:|
| `thuc_nghiem/results` | 1.006.001 | 1.006.001 | 135.380.429.037 |
| `thuc_nghiem/reports` | 980 | 980 | 59.539.089 |
| `thuc_nghiem/databases` | 244 | 244 | 299.616.656 |

Các nhóm trên khớp tên tệp và kích thước từng tệp trong lần kiểm kê. Không đọc lại
SHA-256 của toàn bộ 126 GiB artifact trong báo cáo này; bộ xác minh cuối tiếp tục
kiểm tra checksum theo manifest. 241 archive BSON đã được đối chiếu SHA-256 riêng
trong biên bản E-validation trước đó; không dùng điều đó để thay thế kiểm tra
toàn bộ artifact.

Các thư mục liên kết trên E đều trỏ về bên trong dự án E, không trỏ D. Các tệp
runtime đang chạy có một số khác biệt về PID, nhật ký và trạng thái là bình thường.

## Các tệp kiểm thử còn thiếu

Lượt kiểm kê thông thường gặp 74 thư mục D có đường dẫn dài. Rà lại bằng tiền tố
Windows `\\?\` đọc được thêm 5.481 tệp; toàn bộ 5.481 tệp này chưa có trên E.
Tổng dung lượng 69.930.056 byte, khoảng 66,69 MiB.

Các tệp này nằm trong hồ sơ kiểm thử đường dẫn dài và kiểm chứng cũ, như
`var/system-audit/20261022-afbb7971`, `var/lp-*`, `var/pytest-*`,
`var/verify-current-20261023-01` và các fixture dưới
`thuc_nghiem/runtime/var/continue-20261023-01/pytest-final`.
Chúng không phải mã nguồn ứng dụng đang chạy hoặc các kết quả canonical của
4.276 job nghiên cứu. Chúng vẫn là bằng chứng kiểm thử cần bảo tồn nếu muốn giữ
bản sao đầy đủ. Danh sách chính xác ở `long-path-missing.csv` và
`long-path-audit.json`.

## Git

- Hai bản cùng HEAD `b94b2f706c1ceec1af89b8025cfd56fd1778a3a6`.
- Sáu refs trùng tên và giá trị; không thiếu ref trên E.
- 50.967 đối tượng truy cập được từ các refs đều có trên E.
- `git fsck --connectivity-only --no-reflogs` trên E trả về 0; các thông báo
  dangling tree không phải báo thiếu đối tượng đang được refs sử dụng.
- 229.824 tệp `.git/objects/xx/...` chỉ có trên D; không có tệp nào trong số này
  thuộc tập đối tượng cần bởi các refs hiện tại. Không tự xóa hoặc gọi chúng là
  dữ liệu vô giá trị; bản D vẫn giữ để phục hồi lịch sử không còn được tham chiếu.
- Giữ nguyên index của từng bản; không reset, clean, commit hoặc push.

## Môi trường Python chưa hoàn toàn độc lập

Đã xác nhận trực tiếp:

```text
E:\...\.venv\Scripts\python.exe -m pip --version
  -> pip được nạp từ E:\Smart_Retail_Floor_Allocation\.venv\...

E:\...\.venv\Scripts\pip.exe --version
  -> pip được nạp từ D:\Smart_Retail_Floor_Allocation\.venv\...
```

`pip.exe`, `pytest.exe`, `uvicorn.exe`, `activate.bat` và `activate` vẫn chứa
đường dẫn gốc D. Gọi Python trực tiếp trên E và dùng `python -m ...` hiện nạp
backend từ E, không có đường dẫn D trong `sys.path` của phép kiểm tra này.

Theo tài liệu Python, venv chứa đường dẫn interpreter tuyệt đối và thường cần
được tạo lại ở vị trí mới: https://docs.python.org/3.12/library/venv.html . Báo cáo
này không cài lại hoặc thay đổi thư viện trong khi bộ xác minh còn hoạt động.

## Giới hạn

Kiểm kê không đi theo reparse point để tránh đếm trùng hoặc đọc ra ngoài dự án;
thư mục đích vật lý được kiểm kê riêng. Đã xử lý lại toàn bộ 74 lỗi đường dẫn dài
và không còn lỗi đọc trong phần bổ sung đó. Các tệp mới do bộ xác minh hoặc báo
cáo tạo ra sau lúc kiểm kê không nằm trong số đếm snapshot ban đầu. Đối chiếu
SHA-256 bao phủ mã nguồn, cấu hình, tài liệu/tài sản và các tệp Git quản lý;
không tuyên bố toàn bộ artifact, cache hoặc dependency đã được so sánh từng byte.
