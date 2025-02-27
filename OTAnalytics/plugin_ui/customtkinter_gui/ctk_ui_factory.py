from tkinter.filedialog import askopenfilename, askopenfilenames
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import MinimalInfoBox


class CtkUiFactory(UiFactory):
    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        return MinimalInfoBox(message=message, initial_position=initial_position)

    def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        return askopenfilenames(title=title, filetypes=filetypes)

    def askopenfilename(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
    ) -> str:
        return askopenfilename(
            title=title, filetypes=filetypes, defaultextension=defaultextension
        )
