# Vai trò: Đóng gói snapshot đã đánh giá bằng nội dung niêm phong.
# Mỗi lần đọc trả về bản sao để tránh ứng viên mới làm thay đổi nghiệm đang giữ.
"""Immutable, content-sealed evaluated snapshots; readers always get fresh copies."""

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class FeedbackSnapshot:
    payload_json: str
    sha256: str

    @classmethod
    # Hàm capture: xử lý bước capture trong phạm vi module hiện tại.
    def capture(cls, value):
        # Hàm scientific: xử lý bước scientific trong phạm vi module hiện tại.
        def scientific(item):
            if isinstance(item, dict):
                return {k: scientific(v) for k, v in item.items() if k not in ("hit", "telemetry")}
            if isinstance(item, (tuple, list)):
                return [scientific(v) for v in item]
            return item

        payload = json.dumps(
            scientific(value), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return cls(payload, hashlib.sha256(payload.encode()).hexdigest())

    # Hàm read: đọc dữ liệu đầu vào từ nơi lưu trữ.
    def read(self):
        if hashlib.sha256(self.payload_json.encode()).hexdigest() != self.sha256:
            raise ValueError("Snapshot checksum differs")
        return json.loads(self.payload_json)
