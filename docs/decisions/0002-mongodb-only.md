# ADR 0002 — MongoDB là persistence duy nhất

MongoDB/PyMongo đồng bộ lưu project aggregate, run snapshot/result và worker
heartbeat. Revision CAS bảo vệ cập nhật project. Claim/renew/publish kiểm tra
owner, token, trạng thái và thời hạn lease. Không giả định transaction nhiều
document. GridFS chứa JSON lớn hoặc số nguyên vượt BSON int64, có SHA-256.

Sao lưu hiện hành dùng BSON/GridFS và lưu kèm filesystem artifacts. Phải dừng
mọi writer khi dùng công cụ sao lưu của dự án; phục hồi chỉ vào database mới.
Không có TTL tự xóa dữ liệu nghiên cứu. Lịch sử quyết định nguyên bản được giữ
trong [bản lưu ngoài](../architecture/HISTORICAL_ARCHIVE.md).
