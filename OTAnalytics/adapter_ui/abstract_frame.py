from abc import ABC, abstractmethod


class AbstractFrame(ABC):
    @abstractmethod
    def set_enabled_general_buttons(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_enabled_add_buttons(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_enabled_change_single_item_buttons(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_enabled_change_multiple_items_buttons(self, enabled: bool) -> None:
        raise NotImplementedError
