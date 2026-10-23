# Vận hành MongoDB

Ứng dụng dùng PyMongo đồng bộ. Môi trường Windows do script quản lý dùng MongoDB
Community 8.0.16, authentication và loopback. `var/mongodb/data` là dữ liệu chính;
`var/mongodb/private.json` là bí mật cục bộ. Không coi các thư mục này là cache.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_mongodb.ps1
.venv/Scripts/python.exe -m smart_retail.infrastructure.mongodb.health
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
```

Máy mới cần tạo `.venv`, cài lock và backend trước khi chạy helper với
`-InstallPortable`. Helper xác minh archive tải về bằng SHA-256.
Windows scripts đọc biến môi trường process, không tự nạp `.env`.
Đặt `MONGODB_URI` riêng tư khi dùng máy chủ tự quản lý; đặt `MONGODB_DATABASE`
và `SMART_RETAIL_ARTIFACTS` phù hợp deployment. Không ghi URI có mật khẩu vào log.

Projects dùng CAS revision, giới hạn aggregate 8 MiB. HTTP trả 409 khi revision
cũ và 413 khi payload quá lớn. Runs dùng claim nguyên tử, lease 30 giây và owner
fencing; hết lease chuyển trạng thái terminal, không tự chạy lại cùng ID.
GridFS dùng hai collection `research_payloads.files` và `research_payloads.chunks`;
payload JSON được kiểm tra byte count và SHA khi đọc lại.

Compose có authentication, volume bền vững, initialization và cổng web/API chỉ
bind loopback. Database không publish host port. Địa chỉ database trong container
là hostname `database`. Xem [sao lưu/phục hồi](MONGODB_BACKUP_RESTORE.md) và
[kiểm chứng deployment](../release/DEPLOYMENT_VERIFICATION.md).
