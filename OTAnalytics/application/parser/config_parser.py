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


class ConfigParser(ABC):
    """
    Serialize and parse config files generated by OTConfig
    """

    @abstractmethod
    def parse(
        self,
        file: Path,
    ) -> OtConfig:
        raise NotImplementedError

    @abstractmethod
    def serialize(
        self,
        project: Project,
        video_files: Iterable[Video],
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def convert(
        self,
        project: Project,
        video_files: Iterable[Video],
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
    ) -> dict:
        raise NotImplementedError


class StartDateMissing(Exception):
    pass
