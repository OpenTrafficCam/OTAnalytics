from abc import ABC, abstractmethod


class AbstractFrameRemark(ABC):
    @abstractmethod
    def load_remark(self) -> None:
        pass
