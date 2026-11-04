"""Counts CSV of the daily traffic statistics, written by the counts CSV export."""

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    Tag,
    create_flow_tag,
    create_mode_tag,
    create_section_info_tag,
    create_timeslot_tag,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    DayTrafficStatistics,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.plugin_parser.export import CsvExport


@dataclass(frozen=True)
class DayStatisticsCount(Count):
    """Counts of a day per flow, class group and interval.

    The class group takes the place of the classification. Intervals that are
    not covered and have no count are left out.
    """

    stats: DayTrafficStatistics

    def to_dict(self) -> dict[Tag, int]:
        interval = timedelta(minutes=self.stats.config.interval_minutes)
        result: dict[Tag, int] = {}
        for flow in self.stats.flows:
            flow_tag = create_flow_tag(flow.name).combine(
                create_section_info_tag(flow.start_section_name, flow.end_section_name)
            )
            for group, values in self.stats.counts(flow.id).items():
                group_tag = flow_tag.combine(create_mode_tag(group))
                for index, value in enumerate(values):
                    if value is None:
                        continue
                    timeslot = create_timeslot_tag(
                        self.stats.interval_start(index), interval
                    )
                    result[group_tag.combine(timeslot)] = value
        return result


def counts_filename_stem(export_filename_stem: str, day: date) -> str:
    """Stem of the counts CSV of the day, next to the day's JSON file."""
    return f"{export_filename_stem}.traffic_statistics_{day.isoformat()}"


def write_counts(
    stats: DayTrafficStatistics, export_directory: Path, export_filename_stem: str
) -> Path:
    """Write the counts of the day as CSV in the format of the counts export.

    Returns:
        the path of the CSV file. It is not written if there is nothing to count.
    """
    exporter = CsvExport(
        export_directory=export_directory,
        export_filename_stem=counts_filename_stem(export_filename_stem, stats.day),
        interval_in_minutes=stats.config.interval_minutes,
    )
    return exporter.export(DayStatisticsCount(stats), OVERWRITE)
