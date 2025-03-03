from abc import abstractmethod

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame


class AbstractFrameOffset(AbstractFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def enable_update_offset_button(self, enabled: bool) -> None:
        raise NotImplementedError
