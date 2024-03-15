from typing import Any

from customtkinter import CTkButton, ThemeManager

from OTAnalytics.adapter_ui.abstract_button_quick_save_config import (
    AbstractButtonQuickSaveConfig,
)
from OTAnalytics.plugin_ui.customtkinter_gui.style import COLOR_ORANGE


class ButtonQuickSaveConfig(AbstractButtonQuickSaveConfig, CTkButton):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def set_state_changed_color(self) -> None:
        self.configure(fg_color=COLOR_ORANGE)

    def set_default_color(self) -> None:
        self.set_color(ThemeManager.theme["CTkButton"]["fg_color"])

    def set_color(self, color: str) -> None:
        self.configure(fg_color=color)
