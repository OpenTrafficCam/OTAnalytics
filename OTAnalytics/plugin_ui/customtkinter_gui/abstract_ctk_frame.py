from abc import abstractmethod

from customtkinter import CTkButton, CTkFrame

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"


class AbstractCTkFrame(AbstractFrame, WidgetPositionProvider, CTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    def set_enabled_add_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.add_buttons(), enabled)

    def set_enabled_change_single_item_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.single_item_buttons(), enabled)

    def set_enabled_change_multiple_items_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.multiple_items_buttons(), enabled)

    def _set_enabled_buttons(self, buttons: list[CTkButton], enabled: bool) -> None:
        new_state = STATE_NORMAL if enabled else STATE_DISABLED
        for button in buttons:
            button.configure(state=new_state)

    @abstractmethod
    def add_buttons(self) -> list[CTkButton]:
        raise NotImplementedError

    @abstractmethod
    def single_item_buttons(self) -> list[CTkButton]:
        raise NotImplementedError

    @abstractmethod
    def multiple_items_buttons(self) -> list[CTkButton]:
        raise NotImplementedError