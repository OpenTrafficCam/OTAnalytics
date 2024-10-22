from dataclasses import dataclass


@dataclass(frozen=True)
class ExportMode:
    name: str
    first: bool
    flush: bool

    def is_first_write(self) -> bool:
        return self.first

    def is_subsequent_write(self) -> bool:
        return not self.first

    def is_final_write(self) -> bool:
        return self.flush

    @staticmethod
    def values() -> list["ExportMode"]:
        return [OVERWRITE, INITIAL_MERGE, MERGE, FLUSH]

    @staticmethod
    def create(is_first: bool, flush: bool) -> "ExportMode":
        if is_first and flush:
            return OVERWRITE

        elif is_first and not flush:
            return INITIAL_MERGE

        elif not is_first and not flush:
            return MERGE

        else:  # not is_first and is_last
            return FLUSH


OVERWRITE = ExportMode("overwrite", True, True)
INITIAL_MERGE = ExportMode("initial_merge", True, False)
MERGE = ExportMode("merge", False, False)
FLUSH = ExportMode("final_merge", False, True)
