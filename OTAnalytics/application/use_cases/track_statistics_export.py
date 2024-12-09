from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from OTAnalytics.application.analysis.traffic_counting_specification import ExportFormat
from OTAnalytics.application.export_formats import track_statistics as ts
from OTAnalytics.application.use_cases.track_statistics import (
    CalculateTrackStatistics,
    TrackStatistics,
)


class TrackStatisticsBuildError(Exception):
    pass


class TrackStatisticsBuilder:
    def build(self, track_statistics: TrackStatistics) -> list[dict]:
        return self.__create(track_statistics)

    def __create(self, track_statistics: TrackStatistics) -> list[dict]:
        return [
            {
                ts.TRACK_COUNT: track_statistics.track_count,
                ts.TRACK_COUNT_OUTSIDE: track_statistics.track_count_outside,
                ts.TRACK_COUNT_INSIDE: track_statistics.track_count_inside,
                ts.TRACK_COUNT_INSIDE_NOT_INTERSECTING: track_statistics.track_count_inside_not_intersecting,  # noqa
                ts.TRACK_COUNT_INSIDE_INTERSECTING_BUT_UNASSIGNED: track_statistics.track_count_inside_intersecting_but_unassigned,  # noqa
                ts.TRACK_COUNT_INSIDE_ASSIGNED: track_statistics.track_count_inside_assigned,  # noqa
                ts.PERCENTAGE_INSIDE_ASSIGNED: track_statistics.percentage_inside_assigned,  # noqa
                ts.PERCENTAGE_INSIDE_NOT_INTERSECTING: track_statistics.percentage_inside_not_intersection,  # noqa
                ts.PERCENTAGE_INSIDE_INTERSECTING_BUT_UNASSIGNED: track_statistics.percentage_inside_intersecting_but_unassigned,  # noqa
                ts.NUMBER_OF_TRACKS_TO_BE_VALIDATED: track_statistics.number_of_tracks_to_be_validated,  # noqa
            }
        ]


class TrackStatisticsExportError(Exception):
    pass


class TrackStatisticsExporter(ABC):
    @property
    @abstractmethod
    def format(self) -> ExportFormat:
        raise NotImplementedError

    def __init__(
        self,
        builder: TrackStatisticsBuilder,
        output_file: Path,
    ) -> None:
        self._builder = builder
        self._outputfile = output_file

    def export(self, track_statistics: TrackStatistics) -> None:
        dtos = self._convert(track_statistics)
        self._serialize(dtos)

    @abstractmethod
    def _serialize(self, dtos: list[dict]) -> None:
        """Hook for implementations to serialize in their respective save format.

        Args:
            dtos (list[dict]): the vehicle flow assignments as dtos.
        """
        raise NotImplementedError

    def _convert(self, track_statistics: TrackStatistics) -> list[dict]:
        return self._builder.build(track_statistics)


@dataclass(frozen=True)
class TrackStatisticsExportSpecification:
    save_path: Path
    format: str


class TrackStatisticsExporterFactory(Protocol):
    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats.
        """
        ...

    def create(
        self, specification: TrackStatisticsExportSpecification
    ) -> TrackStatisticsExporter:
        """
        Create the exporter for the given track statistic export specification.

        Args:
            specification (TrackStatisticsExportSpecification): specification of the
            Exporter.

        Returns:
            TrackStatisticsExporter: Exporter to export track statistics.
        """
        ...


class ExportTrackStatistics:
    """Use case to export track statistics"""

    def __init__(
        self,
        calculate_track_statistics: CalculateTrackStatistics,
        exporter_factory: TrackStatisticsExporterFactory,
    ) -> None:
        self._calculate_track_statistics = calculate_track_statistics
        self._exporter_factory = exporter_factory

    def export(self, specification: TrackStatisticsExportSpecification) -> None:
        track_statistics = self._calculate_track_statistics.get_statistics()
        exporter = self._exporter_factory.create(specification)
        exporter.export(track_statistics)

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats
        """
        return self._exporter_factory.get_supported_formats()