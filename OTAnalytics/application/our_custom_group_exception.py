class OurCustomGroupException(Exception):
    """Placeholder for ExceptionGroups introduced in Python 3.11"""

    def __init__(self, exceptions: list[Exception], *args: object) -> None:
        super().__init__(*args)
        self._exceptions = exceptions

    def __str__(self) -> str:
        return "\n".join([str(exception) for exception in self._exceptions])
