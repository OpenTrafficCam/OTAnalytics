"""JSON codec for the daily traffic statistics files."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    TOTAL,
    DayTrafficStatistics,
    FlowInfo,
    PeakHour,
    as_utc,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_values import SpeedValues
from OTAnalytics.helpers.file_helpers import atomic_write
from OTAnalytics.plugin_parser.json_parser import parse_json, write_json

FORMAT = "otanalytics.traffic_statistics"
VERSION = 1

FORMAT_KEY = "format"
VERSION_KEY = "version"
DAY_KEY = "day"
COUNTING_EVENT_KEY = "counting_event"
INTERVAL_MINUTES_KEY = "interval_minutes"
PEAK_WINDOW_MINUTES_KEY = "peak_window_minutes"
PEAK_STEP_MINUTES_KEY = "peak_step_minutes"
CLASS_GROUPS_KEY = "class_groups"
AS_OF_KEY = "as_of"
COVERAGE_KEY = "coverage"
FLOWS_KEY = "flows"
STATISTICS_KEY = "statistics"
TOTAL_KEY = "total"
TOTALS_KEY = "totals"
PEAK_HOUR_KEY = "peak_hour"
SPEED_KEY = "speed"
AVG_KEY = "avg"
V85_KEY = "v85"
COUNT_KEY = "count"
START_KEY = "start"
END_KEY = "end"
ID_KEY = "id"
NAME_KEY = "name"
INDEX_KEY = "index"
START_SECTION_KEY = "start_section"
END_SECTION_KEY = "end_section"


class TrafficStatisticsFormatError(ValueError):
    """Raised if a traffic statistics file is corrupt or does not fit the config."""


def to_dict(stats: DayTrafficStatistics) -> dict[str, Any]:
    """Convert the statistics to the JSON serializable file format (v1)."""
    config = stats.config
    flow_statistics = {
        flow.id: _statistics_block(stats, flow.id) for flow in stats.flows
    }
    return {
        FORMAT_KEY: FORMAT,
        VERSION_KEY: VERSION,
        DAY_KEY: stats.day.isoformat(),
        COUNTING_EVENT_KEY: stats.counting_event.value,
        INTERVAL_MINUTES_KEY: config.interval_minutes,
        PEAK_WINDOW_MINUTES_KEY: config.peak_window_minutes,
        PEAK_STEP_MINUTES_KEY: config.peak_step_minutes,
        CLASS_GROUPS_KEY: {
            group: sorted(classifications)
            for group, classifications in config.class_groups.items()
        },
        AS_OF_KEY: _format_datetime(stats.as_of),
        COVERAGE_KEY: [
            [_format_datetime(start), _format_datetime(end)]
            for start, end in stats.coverage
        ],
        FLOWS_KEY: [_flow_to_dict(flow) for flow in stats.flows],
        STATISTICS_KEY: {
            TOTAL_KEY: _statistics_block(stats, TOTAL),
            FLOWS_KEY: flow_statistics,
        },
    }


def _format_datetime(value: datetime | None) -> str | None:
    return None if value is None else _format_utc(value)


def _format_utc(value: datetime) -> str:
    """Format a UTC time in the notation of the counts CSV, without an offset.

    Fractions of a second are kept if there are any, e.g. at the end of a video.
    """
    return as_utc(value).replace(tzinfo=None).isoformat(sep=" ")


def _flow_to_dict(flow: FlowInfo) -> dict[str, Any]:
    return {
        ID_KEY: flow.id,
        NAME_KEY: flow.name,
        INDEX_KEY: flow.index,
        START_SECTION_KEY: {
            ID_KEY: flow.start_section_id,
            NAME_KEY: flow.start_section_name,
        },
        END_SECTION_KEY: {ID_KEY: flow.end_section_id, NAME_KEY: flow.end_section_name},
    }


def _statistics_block(stats: DayTrafficStatistics, flow_id: str) -> dict[str, Any]:
    return {
        TOTALS_KEY: stats.totals(flow_id),
        PEAK_HOUR_KEY: {
            group: _peak_to_dict(peak)
            for group, peak in stats.peak_hour(flow_id).items()
        },
        SPEED_KEY: {
            group: _speed_to_dict(values)
            for group, values in stats.speed(flow_id).items()
        },
    }


def _peak_to_dict(peak: PeakHour) -> dict[str, Any]:
    return {
        START_KEY: _format_utc(peak.start),
        END_KEY: _format_utc(peak.end),
        COUNT_KEY: peak.count,
    }


def _speed_to_dict(values: SpeedValues) -> dict[str, Any]:
    return {AVG_KEY: values.avg, V85_KEY: values.v85, COUNT_KEY: values.count}


def write(stats: DayTrafficStatistics, path: Path) -> None:
    """Write the statistics as compact JSON atomically to the path."""
    with atomic_write(path) as temp:
        write_json(to_dict(stats), temp, indent=0)


@dataclass(frozen=True)
class DayProgress:
    """The part of a day file needed to continue the day: coverage and as_of."""

    coverage: list[tuple[datetime, datetime]]
    as_of: datetime | None


def read_progress(path: Path) -> DayProgress:
    """Read coverage and as_of of a day file.

    Raises:
        TrafficStatisticsFormatError: if the file is not a valid day file or
            holds times that are not UTC.
    """
    try:
        data = parse_json(path)
        if not isinstance(data, dict):
            raise TrafficStatisticsFormatError("Day file must be a JSON object.")
        if data.get(FORMAT_KEY) != FORMAT or data.get(VERSION_KEY) != VERSION:
            raise TrafficStatisticsFormatError(
                f"Unknown format {data.get(FORMAT_KEY)!r} "
                f"version {data.get(VERSION_KEY)!r}."
            )
        coverage = [
            (_parse_utc(start), _parse_utc(end)) for start, end in data[COVERAGE_KEY]
        ]
        as_of = data[AS_OF_KEY]
        return DayProgress(coverage, None if as_of is None else _parse_utc(as_of))
    except TrafficStatisticsFormatError as cause:
        raise TrafficStatisticsFormatError(
            f"Invalid day file {path}: {cause}"
        ) from cause
    except (ValueError, OSError, EOFError, KeyError, TypeError) as cause:
        raise TrafficStatisticsFormatError(
            f"Invalid day file {path}: {cause!r}"
        ) from cause


def _parse_utc(value: str) -> datetime:
    return as_utc(datetime.fromisoformat(value))
