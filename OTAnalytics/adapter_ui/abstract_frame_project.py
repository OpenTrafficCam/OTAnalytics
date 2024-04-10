from abc import abstractmethod
from datetime import datetime
from typing import Optional


class AbstractFrameProject:
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update(self, name: str, start_date: Optional[datetime]) -> None:
        pass

    @abstractmethod
    def set_enabled_general_buttons(self, enabled: bool) -> None:
        raise NotImplementedError


class AbstractFrameSvzMetadata:
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update(self, metadata: dict) -> None:
        pass
