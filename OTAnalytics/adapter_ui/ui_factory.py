from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.file_export_dto import EventFileDto
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.view_model import ViewModel


class UiFactory(ABC):

    @abstractmethod
    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        pass

    @abstractmethod
    def askopenfilename(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
    ) -> str:
        pass

    @abstractmethod
    def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        pass

    @abstractmethod
    def ask_for_save_file_path(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        initialfile: str,
        initialdir: Path,
    ) -> Path:
        raise NotImplementedError

    def configure_export_file(
        self,
        title: str,
        default_values: dict[str, str],
        export_format_extensions: dict[str, str],
        initial_file_stem: str,
        viewmodel: ViewModel,
    ) -> EventFileDto:
        raise NotImplementedError
