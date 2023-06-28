from abc import ABC, abstractmethod

from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider


class AbstractMainWindow(WidgetPositionProvider, ABC):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError
