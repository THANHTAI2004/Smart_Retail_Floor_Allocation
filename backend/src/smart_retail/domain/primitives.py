# Vai trò: Kiểu tọa độ dùng đơn vị SI và lỗi engine có mã trạng thái rõ ràng để application xử lý nhất quán.
"""Shared SI coordinate type and explicit engine failure."""

Point = tuple[float, float]


class EngineError(ValueError):
    # Hàm __init__: khởi tạo đối tượng và các phụ thuộc ban đầu.
    def __init__(self, code: str, message: str):
        # args must rebuild the error: SimPy re-raises process failures as
        # type(exc)(*exc.args), and pickling uses the same contract.
        super().__init__(code, message)
        self.code = code
        self.message = message
        self.stage: str | None = None

    # Hàm __str__: xử lý bước str trong phạm vi module hiện tại.
    def __str__(self) -> str:
        return self.message
