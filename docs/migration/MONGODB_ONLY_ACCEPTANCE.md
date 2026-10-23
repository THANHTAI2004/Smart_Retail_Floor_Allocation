# Kiểm chứng persistence hiện hành

MongoDB là backend duy nhất. Bộ integration tests kiểm tra CAS, atomic claim,
fencing, cancellation race, kết quả bất biến, GridFS, checksum và backup/restore.
Kiểm tra kiến trúc cấm engines phụ thuộc database.

Báo cáo ngày 22/10/2026 ghi nhận 178 pytest, 4 Vitest, 10 Playwright và các kiểm
tra Compose trong phạm vi xác định. Đây là kết quả lịch sử; xem
[audit](../system-audit/FINAL_SYSTEM_AUDIT.md). Thay đổi công cụ/tài liệu hiện tại
được ghi riêng trong [HANDOFF](../../HANDOFF.md).

Các biên bản nguyên bản không còn thuộc tài liệu vận hành được giữ trong
[bản lưu ngoài dự án](../architecture/HISTORICAL_ARCHIVE.md).
