from abc import ABC, abstractmethod

from customtkinter import CTkButton

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"


class AbstractFrame(ABC):
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

    def _disable_button(self, button: CTkButton) -> None:
        button.configure(state=STATE_DISABLED)

    def _enable_button(self, button: CTkButton) -> None:
        button.configure(state=STATE_NORMAL)
