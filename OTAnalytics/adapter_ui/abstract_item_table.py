from abc import abstractmethod
from typing import Optional


class AbstractItemTable:
    # TODO: add property viewmodel

    @abstractmethod
    def _introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _notify_viewmodel_about_selected_item_id(
        self, line_section_id: Optional[str]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_items(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_selected_items(self, item_id: Optional[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_position(self) -> tuple[int, int]:
        raise NotImplementedError
