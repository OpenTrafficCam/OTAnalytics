from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame


class ButtonForm(AbstractFrame):

    def set_enabled_general_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_general_buttons(), enabled)

    def set_enabled_add_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_add_buttons(), enabled)

    def set_enabled_change_single_item_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_single_item_buttons(), enabled)

    def set_enabled_change_multiple_items_buttons(self, enabled: bool) -> None:
        self._set_enabled_buttons(self.get_multiple_items_buttons(), enabled)

    def _set_enabled_buttons(self, buttons: list[Button], enabled: bool) -> None:
        for button in buttons:
            if enabled:
                button.enable()
            else:
                button.disable()

    def get_general_buttons(self) -> list[Button]:
        return []

    def get_add_buttons(self) -> list[Button]:
        return []

    def get_single_item_buttons(self) -> list[Button]:
        return []

    def get_multiple_items_buttons(self) -> list[Button]:
        return []
