from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from OTAnalytics.application.export_formats.export_mode import ExportMode


@dataclass(frozen=True)
class TrafficStatisticsExportSpecification:
    """Describes one traffic statistics export call (typically one chunk).

    Attributes:
        export_directory: directory the day files are written to.
        export_filename_stem: stem of the day file names.
        config: traffic statistics configuration.
        counting_event: event determining the time of a road user.
        covered_start: start of the time range covered by this call.
        covered_end: end of the time range covered by this call.
        export_mode: bulk or stream mode; does not change the file content.
    """

    export_directory: Path
    export_filename_stem: str
    config: TrafficStatisticsConfig
    counting_event: CountingEvent
    covered_start: datetime
    covered_end: datetime
    export_mode: ExportMode


class ExportTrafficStatistics(ABC):
    """Exports traffic statistics as one file per local day."""

    @abstractmethod
    def export(self, specification: TrafficStatisticsExportSpecification) -> list[Path]:
        """Write the statistics of all days touched by this call.

        Returns:
            the written files in ascending order of their day.
        """
        raise NotImplementedError
