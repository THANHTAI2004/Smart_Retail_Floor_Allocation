# Kiểm chứng triển khai MongoDB và Docker Compose

Compose gồm database có authentication, initialize, backend, worker và frontend.
Verifier tạo project UUID, database riêng, mật khẩu ngẫu nhiên, cổng loopback
trống và named volumes riêng. Nó kiểm tra config/build/readiness, authentication,
CRUD/revision, queue, spawned worker, kết quả/SHA, restart, cancel và recovery.
Biến `SMART_RETAIL_COMPOSE_JOINT_SMOKE=1` bật joint/outage checks bổ sung.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_mongodb_compose.ps1 -Output var/my-new-compose-check
```

Output phải mới. Script dừng riêng stack do nó tạo và giữ volume/log đã che bí
mật. Không xóa volume trong thao tác vận hành thông thường. Docker CLI/runtime
vắng mặt trả BLOCKED với exit 2; chạy thành công trả exit 0.

Audit ngày 22/10/2026 có kết quả Compose thực trong môi trường cục bộ.
Không suy ra remote CI, failover hay vận hành dài hạn đã được kiểm chứng.
Biên bản nguyên bản ở [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md);
bản tổng hợp có giới hạn ở [audit](../system-audit/FINAL_SYSTEM_AUDIT.md).
