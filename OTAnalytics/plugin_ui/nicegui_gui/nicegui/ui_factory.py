from typing import Iterable, Literal

from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.ui_factory import UiFactory


class NiceGuiInfoBox(MessageBox):

    def close(self) -> None:
        pass

    def update_message(self, message: str) -> None:
        pass


class NiceGuiUiFactory(UiFactory):

    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        return NiceGuiInfoBox()

    def askopenfilename(
        self, title: str, filetypes: list[tuple[str, str]], defaultextension: str
    ) -> str:
        return ""

    def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        return tuple([""])
