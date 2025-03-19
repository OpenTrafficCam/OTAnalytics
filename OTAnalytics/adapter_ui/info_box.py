from abc import ABC


class InfoBox(ABC):
    @property
    def canceled(self) -> bool:
        raise NotImplementedError
