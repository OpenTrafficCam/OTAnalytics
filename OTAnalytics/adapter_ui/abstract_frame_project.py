from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class AbstractFrameProject(ABC):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update(self, name: str, start_date: Optional[datetime]) -> None:
        pass

    @abstractmethod
    def set_enabled_general_buttons(self, enabled: bool) -> None:
        raise NotImplementedError


class AbstractFrameSvzMetadata(ABC):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update(self, metadata: dict) -> None:
        pass
