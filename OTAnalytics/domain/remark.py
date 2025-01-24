class RemarkRepository:
    def __init__(self) -> None:
        self._remark: str | None = None

    def add(self, remark: str) -> None:
        self._remark = remark

    def get(self) -> str | None:
        return self._remark
