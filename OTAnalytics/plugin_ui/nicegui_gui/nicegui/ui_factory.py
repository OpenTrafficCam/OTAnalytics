from pathlib import Path
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.file_export_dto import EventFileDto
from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)


class NiceGuiMessageBox(MessageBox):

    def close(self) -> None:
        pass

    def update_message(self, message: str) -> None:
        pass


class NiceGuiInfoBox(InfoBox):
    @property
    def canceled(self) -> bool:
        return False


class NiceGuiUiFactory(UiFactory):

    def info_box(
        self, message: str, initial_position: tuple[int, int], show_cancel: bool = False
    ) -> InfoBox:
        return NiceGuiInfoBox()

    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        return NiceGuiMessageBox()

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
        title: str,
        input_values: dict[str, str],
        export_format_extensions: dict[str, str],
        initial_file_stem: str,
        viewmodel: ViewModel,
    ) -> EventFileDto:
        raise NotImplementedError

    def configure_export_counts(
        self,
        input_values: dict,
        modes: list,
        export_formats: dict[str, str],
        viewmodel: ViewModel,
    ) -> CountingSpecificationDto:
        raise NotImplementedError
