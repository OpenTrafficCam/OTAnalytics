from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Iterable

from OTAnalytics.adapter_ui.file_export_dto import ExportFileDto
from OTAnalytics.adapter_ui.flow_dto import FlowDto
from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.message_type import MessageType
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate


class UiFactory(ABC):
    """Builds the dialogs and messages of a front-end.

    `show_message` and `ask_for_confirmation` are deliberately not abstract:
    other front-ends (e.g. OTCloud) implement this port, and a new abstract
    method would break them on instantiation. Their defaults fall back to
    `info_box`, which keeps the behaviour of such front-ends unchanged.
    """

    @abstractmethod
    def info_box(self, message: str, initial_position: tuple[int, int]) -> InfoBox:
        raise NotImplementedError

    def show_message(
        self,
        message: str,
        initial_position: tuple[int, int],
        message_type: MessageType,
    ) -> None:
        """Show a message of the given severity to the user.

        Args:
            message (str): text to show.
            initial_position (tuple[int, int]): position of the message on
                screen, if the front-end supports it.
            message_type (MessageType): severity of the message.
        """
        self.info_box(message=message, initial_position=initial_position)

    async def ask_for_confirmation(
        self, message: str, initial_position: tuple[int, int]
    ) -> bool:
        """Ask the user to confirm or cancel an action.

        Args:
            message (str): what will happen on confirmation.
            initial_position (tuple[int, int]): position of the dialog on
                screen, if the front-end supports it.

        Returns:
            bool: True if the user confirmed, False if the user canceled.
        """
        info_box = self.info_box(message=message, initial_position=initial_position)
        return not info_box.canceled

    @abstractmethod
    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        raise NotImplementedError

    @abstractmethod
    async def askopenfilename(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        extension_options: dict[str, list[str] | None] | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
        extension_options: dict[str, list[str] | None] | None = None,
    ) -> list[Path]:
        raise NotImplementedError

    @abstractmethod
    async def ask_for_save_file_path(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        initialfile: str,
        initialdir: Path,
    ) -> Path:
        raise NotImplementedError

    @abstractmethod
    async def configure_export_file(
        self,
        title: str,
        export_format_extensions: dict[str, str],
        context_file_type: str,
        viewmodel: ViewModel,
    ) -> ExportFileDto:
        raise NotImplementedError

    @abstractmethod
    async def configure_export_counts(
        self,
        start: datetime | None,
        end: datetime | None,
        default_format: str,
        modes: list,
        export_formats: dict[str, str],
        viewmodel: ViewModel,
    ) -> CountingSpecificationDto:
        raise NotImplementedError

    @abstractmethod
    async def configure_section(
        self,
        title: str,
        section_offset: RelativeOffsetCoordinate,
        initial_position: tuple[int, int],
        input_values: dict | None,
        show_offset: bool,
        viewmodel: ViewModel,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def configure_flow(
        self,
        title: str,
        initial_position: tuple[int, int],
        section_ids: ColumnResources,
        input_values: FlowDto | None,
        name_generator: FlowNameGenerator,
        show_distance: bool,
    ) -> FlowDto:
        raise NotImplementedError
