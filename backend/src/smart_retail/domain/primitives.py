"""Shared SI coordinate type and explicit engine failure."""

Point = tuple[float, float]


class EngineError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.stage: str | None = None
