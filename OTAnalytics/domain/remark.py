class RemarkRepository:
    def __init__(self) -> None:
        self._remark: str = ""

    def add(self, remark: str) -> None:
        self._remark = remark

    def get(self) -> str:
        return self._remark
