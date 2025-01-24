from abc import abstractmethod

from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider


class AbstractTreeviewInterface(WidgetPositionProvider):
    # TODO: add property viewmodel

    @abstractmethod
    def _introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_items(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_selected_items(self, item_ids: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def enable(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disable(self) -> None:
        raise NotImplementedError
