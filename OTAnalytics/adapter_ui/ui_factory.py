from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.file_export_dto import ExportFileDto
from OTAnalytics.adapter_ui.flow_dto import FlowDto
from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate


class UiFactory(ABC):

    @abstractmethod
    def info_box(
        self, message: str, initial_position: tuple[int, int], show_cancel: bool = False
    ) -> InfoBox:
        raise NotImplementedError

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
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
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
        initial_file_stem: str,
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
