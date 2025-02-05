from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from OTAnalytics.application.project import Project
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video


@dataclass(frozen=True)
class ExportConfig:
    save_name: str
    save_suffix: str
    event_formats: set[str]
    count_intervals: set[int]


@dataclass(frozen=True)
class AnalysisConfig:
    do_events: bool
    do_counting: bool
    track_files: set[Path]
    export_config: ExportConfig
    num_processes: int
    logfile: Path


@dataclass(frozen=True)
class OtConfig:
    project: Project
    analysis: AnalysisConfig
    videos: Sequence[Video]
    sections: Sequence[Section]
    flows: Sequence[Flow]
    remark: str | None


class ConfigParser(ABC):
    """
    Serialize and parse config files generated by OTConfig
    """

    @abstractmethod
    def parse(
        self,
        file: Path,
    ) -> OtConfig:
        """Parse a OTConfig file to a OtConfig object.

        Args:
            file: Path to the OTConfig file.

        Returns:
            OtConfig: The parsed OtConfig object.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_from_dict(self, data: dict, base_folder: Path) -> OtConfig:
        """Parse a OTConfig from a dictionary.

        Args:
            data (dict): the contents of an OTConfig.
            base_folder: the base folder of the OTConfig.

        Returns:
            OtConfig: The parsed OtConfig object.
        """
        raise NotImplementedError

    @abstractmethod
    def serialize(
        self,
        project: Project,
        video_files: Iterable[Video],
        track_files: Iterable[Path],
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
        remark: str | None,
    ) -> None:
        """Serializes the project with the given videos, sections and flows into the
        file.

        Args:
            project (Project): description of the project
            video_files (Iterable[Video]): video files to reference
            track_files (Iterable[Path]): track files to reference
            sections (Iterable[Section]): sections to store
            flows (Iterable[Flow]): flows to store
            file (Path): output file
            remark(str | None): comment on this file

        Raises:
            StartDateMissing: if start date is not configured
        """

        raise NotImplementedError

    @abstractmethod
    def serialize_from_config(self, config: OtConfig, file: Path) -> None:
        """Serializes OTConfig using the given file as a save location.

        Args:
            config: the config to serialize.
            file: the location to save the config to.
        """
        raise NotImplementedError

    @abstractmethod
    def convert(
        self,
        project: Project,
        video_files: Iterable[Video],
        track_files: Iterable[Path],
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
        remark: str | None,
    ) -> dict:
        """Converts the given information into a dictionary."""
        raise NotImplementedError


class StartDateMissing(Exception):
    pass
