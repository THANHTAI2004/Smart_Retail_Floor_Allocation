# Kiểm tra đủ hồ sơ từ C đến E — 24/10/2026

Đã đối chiếu với bản gốc khôi phục trên C và các biên nhận chuyển dữ liệu.
Tất cả **742.103 tệp nguồn C đã được tính đủ và có vị trí tương ứng trên E**.
Tổng dung lượng logic của hồ sơ nguồn là **116.567.224.410 byte**.

| Nhóm | Số tệp | Kết quả |
|---|---:|---|
| Dữ liệu bên trong 20 campaign gốc | 741.446 | Hiện diện đầy đủ, kích thước từng tệp khớp |
| Hồ sơ runtime trong các thư mục con | 632 | Không thiếu tệp |
| Công cụ và biên nhận ở cấp gốc runtime | 5 | SHA-256 khớp bản C |
| Danh mục checksum ở cấp ngoài campaign | 20 | Vừa chép bổ sung, SHA-256 khớp bản C |
| **Tổng** | **742.103** | **Không thiếu tệp nguồn C** |

Phát hiện và hoàn tất 20 tệp `paper-*.sha256.json` trước đó còn ở cấp ngoài
các thư mục campaign trong bản C. Chúng hiện nằm cùng tên tại
`experiments/results/20261023-paper-v2/`. Không có kết quả job bị thiếu trong
phát hiện này; đây là các danh mục checksum lịch sử.

Các campaign hiện ở:

```text
E:\Smart_Retail_Floor_Allocation\experiments\results\20261023-paper-v2
```

Hồ sơ runtime chuyển từ C ở `experiments/runtime/external/`. Một tệp
`progress/process.json` có kích thước khác bản C vì PID và đường dẫn đã được
cập nhật cho tiến trình hiện chạy trên E. Các tệp gốc trên C vẫn được giữ.

Phạm vi kiểm chứng: các manifest C-to-D được kiểm tra SHA-256, sau đó kiểm tra
mới sự hiện diện và kích thước từng tệp E trong các manifest đó; các tệp checksum
và công cụ cấp gốc được đối chiếu SHA-256 trực tiếp với C. Báo cáo này không
tuyên bố đã đọc lại SHA-256 toàn bộ 108,56 GiB artifact trên E. Bộ xác minh cuối
tiếp tục kiểm tra checksum riêng, chưa có biên nhận hoàn tất sao lưu cuối.

Bản gốc khôi phục:

```text
C:\Users\admin\Documents\SmartRetailBackups\20261024-consolidation
```

Các campaign chạy bù được tạo trực tiếp trong dự án, không thuộc số tệp nguồn C
trên. Chúng đã được kiểm tra trong đợt đối chiếu D-to-E riêng. Tổng kết quả nghiên
cứu vẫn là 4.276 job duy nhất, không cộng lượt chạy lại hoặc fold đi kèm.

Chi tiết máy đọc được: `summary.json` trong cùng thư mục.
