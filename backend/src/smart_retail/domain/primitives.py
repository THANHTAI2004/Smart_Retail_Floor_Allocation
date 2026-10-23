"""Shared SI coordinate type and explicit engine failure."""

Point = tuple[float, float]


class EngineError(ValueError):
    def __init__(self, code: str, message: str):
        # args must rebuild the error: SimPy re-raises process failures as
        # type(exc)(*exc.args), and pickling uses the same contract.
        super().__init__(code, message)
        self.code = code
        self.message = message
        self.stage: str | None = None

    def __str__(self) -> str:
        return self.message
