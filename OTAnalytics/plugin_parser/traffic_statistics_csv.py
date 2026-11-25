"""CSV files of the daily traffic statistics in the format of the counts export."""

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    Tag,
    create_flow_tag,
    create_mode_tag,
    create_section_info_tag,
    create_timeslot_tag,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    TOTAL,
    DayTrafficStatistics,
    FlowInfo,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_values import SpeedValues
from OTAnalytics.application.config import DEFAULT_COUNT_INTERVAL_TIME_UNIT
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_parser.export import CsvExport, tag_values_to_dataframe

SPEED_COUNT = "speed count"
AVG_SPEED = "avg speed"
V85 = "v85"

SPEEDS = "speeds"
SPEEDS_ALL_FLOWS = "speeds_all_flows"
SPEEDS_TOTAL = "speeds_total"


def _flow_tag(flow: FlowInfo) -> Tag:
    return create_flow_tag(flow.name).combine(
        create_section_info_tag(flow.start_section_name, flow.end_section_name)
    )


def _timeslot_tag(stats: DayTrafficStatistics, index: int) -> Tag:
    interval = timedelta(minutes=stats.config.interval_minutes)
    return create_timeslot_tag(stats.interval_start(index), interval)


@dataclass(frozen=True)
class DayStatisticsCount(Count):
    """Counts of a day per flow, class group and interval.

    The class group takes the place of the classification. Intervals that are
    not covered and have no count are left out.
    """

    stats: DayTrafficStatistics

    def to_dict(self) -> dict[Tag, int]:
        result: dict[Tag, int] = {}
        for flow in self.stats.flows:
            flow_tag = _flow_tag(flow)
            for group, values in self.stats.counts(flow.id).items():
                group_tag = flow_tag.combine(create_mode_tag(group))
                for index, value in enumerate(values):
                    if value is None:
                        continue
                    result[group_tag.combine(_timeslot_tag(self.stats, index))] = value
        return result


def statistics_filename_stem(export_filename_stem: str, day: date) -> str:
    """Stem of the CSV files of the day, next to the day's JSON file."""
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
        export_filename_stem=statistics_filename_stem(export_filename_stem, stats.day),
        interval_in_minutes=stats.config.interval_minutes,
    )
    return exporter.export(DayStatisticsCount(stats), OVERWRITE)


def _speed_columns(values: SpeedValues | None) -> dict[str, Any]:
    if values is None:
        return {SPEED_COUNT: 0, AVG_SPEED: None, V85: None}
    return {SPEED_COUNT: values.count, AVG_SPEED: values.avg, V85: values.v85}


def _add_speed_rows(
    result: dict[Tag, dict[str, Any]],
    stats: DayTrafficStatistics,
    base_tag: Tag,
    profile: Sequence[SpeedValues | None],
    covered: Sequence[bool],
) -> None:
    """Add a row per interval that is covered or has speeds."""
    for index, values in enumerate(profile):
        if values is None and not covered[index]:
            continue
        result[base_tag.combine(_timeslot_tag(stats, index))] = _speed_columns(values)


def speeds_per_flow(stats: DayTrafficStatistics) -> dict[Tag, dict[str, Any]]:
    """Speed values per flow, class group and interval."""
    covered = stats.covered_intervals()
    result: dict[Tag, dict[str, Any]] = {}
    for flow in stats.flows:
        flow_tag = _flow_tag(flow)
        for group, profile in stats.speed_profile(flow.id).items():
            base_tag = flow_tag.combine(create_mode_tag(group))
            _add_speed_rows(result, stats, base_tag, profile, covered)
    return result


def speeds_all_flows(stats: DayTrafficStatistics) -> dict[Tag, dict[str, Any]]:
    """Speed values per class group and interval over all flows."""
    covered = stats.covered_intervals()
    result: dict[Tag, dict[str, Any]] = {}
    for group, profile in stats.speed_profile(TOTAL).items():
        _add_speed_rows(result, stats, create_mode_tag(group), profile, covered)
    return result


def speeds_total(stats: DayTrafficStatistics) -> dict[Tag, dict[str, Any]]:
    """Speed values per interval over all flows and class groups.

    The classification is TOTAL.
    """
    result: dict[Tag, dict[str, Any]] = {}
    _add_speed_rows(
        result,
        stats,
        create_mode_tag(TOTAL),
        stats.total_speed_profile(),
        stats.covered_intervals(),
    )
    return result


def _write_speeds(
    values: dict[Tag, dict[str, Any]],
    stats: DayTrafficStatistics,
    export_directory: Path,
    export_filename_stem: str,
    file_type: str,
) -> Path | None:
    path = export_directory / (
        f"{statistics_filename_stem(export_filename_stem, stats.day)}.{file_type}"
        f"_{stats.config.interval_minutes}{DEFAULT_COUNT_INTERVAL_TIME_UNIT}.csv"
    )
    dataframe = tag_values_to_dataframe(values)
    if dataframe.empty:
        logger().info(f"No speeds to write to {path}.")
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)
    return path


def write_speeds(
    stats: DayTrafficStatistics, export_directory: Path, export_filename_stem: str
) -> list[Path]:
    """Write the speed values of the day per interval as CSV files.

    One file each per flow and class group, per class group over all flows and
    over all flows and class groups. Files without rows are not written.

    Returns:
        the written files.
    """
    files = [
        (speeds_per_flow(stats), SPEEDS),
        (speeds_all_flows(stats), SPEEDS_ALL_FLOWS),
        (speeds_total(stats), SPEEDS_TOTAL),
    ]
    paths = [
        _write_speeds(values, stats, export_directory, export_filename_stem, name)
        for values, name in files
    ]
    return [path for path in paths if path is not None]
