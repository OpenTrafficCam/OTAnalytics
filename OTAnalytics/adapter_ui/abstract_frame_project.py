from abc import abstractmethod
from datetime import datetime


class AbstractFrameProject:
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update(self, name: str, start_date: datetime) -> None:
        pass
