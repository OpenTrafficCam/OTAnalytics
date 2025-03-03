from pathlib import Path
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.event_export_dto import EventExportDto
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.adapter_ui.view_model import ViewModel


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

    def ask_for_save_file_path(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        initialfile: str,
        initialdir: Path,
    ) -> Path:
        return Path("")

    def configure_export_file(
        self,
        default_values: dict[str, str],
        export_format_extensions: dict[str, str],
        viewmodel: ViewModel,
    ) -> EventExportDto:
        raise NotImplementedError
