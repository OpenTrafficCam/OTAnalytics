from abc import abstractmethod

from customtkinter import CTkButton

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    STATE_DISABLED,
    STATE_NORMAL,
)
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import EmbeddedCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position


class AbstractCTkFrame(AbstractFrame, WidgetPositionProvider, EmbeddedCTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    def set_enabled_general_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_general_buttons(), enabled)

    def set_enabled_add_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_add_buttons(), enabled)

    def set_enabled_change_single_item_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_single_item_buttons(), enabled)

    def set_enabled_change_multiple_items_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_multiple_items_buttons(), enabled)

    def _set_enabled_buttons(self, buttons: list[CTkButton], enabled: bool) -> None:
        new_state = STATE_NORMAL if enabled else STATE_DISABLED
        for button in buttons:
            button.configure(state=new_state)

    def get_general_buttons(self) -> list[CTkButton]:
        return []

    def get_add_buttons(self) -> list[CTkButton]:
        return []

    def get_single_item_buttons(self) -> list[CTkButton]:
        return []

    def get_multiple_items_buttons(self) -> list[CTkButton]:
        return []

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        x, y = get_widget_position(self, offset=offset)
        return x, y
