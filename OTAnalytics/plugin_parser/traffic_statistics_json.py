"""JSON codec for the daily traffic statistics files."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    TOTAL,
    DayTrafficStatistics,
    FlowInfo,
    PeakHour,
    minutes_in_day,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_histogram import (
    SpeedHistogram,
    SpeedValues,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from OTAnalytics.helpers.file_helpers import atomic_write

FORMAT = "otanalytics.traffic_statistics"
VERSION = 1

FORMAT_KEY = "format"
VERSION_KEY = "version"
DAY_KEY = "day"
TIMEZONE_KEY = "timezone"
COUNTING_EVENT_KEY = "counting_event"
INTERVAL_MINUTES_KEY = "interval_minutes"
SPEED_PROFILE_INTERVAL_MINUTES_KEY = "speed_profile_interval_minutes"
PEAK_WINDOW_MINUTES_KEY = "peak_window_minutes"
PEAK_STEP_MINUTES_KEY = "peak_step_minutes"
CLASS_GROUPS_KEY = "class_groups"
AS_OF_KEY = "as_of"
COVERAGE_KEY = "coverage"
FLOWS_KEY = "flows"
STATISTICS_KEY = "statistics"
STATE_KEY = "state"
TOTAL_KEY = "total"
COUNTS_KEY = "counts"
TOTALS_KEY = "totals"
PEAK_HOUR_KEY = "peak_hour"
SPEED_KEY = "speed"
SPEED_PROFILE_KEY = "speed_profile"
ROAD_USER_IDS_KEY = "road_user_ids"
SPEED_HISTOGRAMS_KEY = "speed_histograms"
BINS_KEY = "bins"
TOTAL_SPEED_KEY = "total_speed"
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

_TOP_LEVEL_KEYS = (
    FORMAT_KEY,
    VERSION_KEY,
    DAY_KEY,
    TIMEZONE_KEY,
    COUNTING_EVENT_KEY,
    INTERVAL_MINUTES_KEY,
    SPEED_PROFILE_INTERVAL_MINUTES_KEY,
    PEAK_WINDOW_MINUTES_KEY,
    PEAK_STEP_MINUTES_KEY,
    CLASS_GROUPS_KEY,
    AS_OF_KEY,
    COVERAGE_KEY,
    FLOWS_KEY,
    STATISTICS_KEY,
    STATE_KEY,
)


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
        TIMEZONE_KEY: config.timezone,
        COUNTING_EVENT_KEY: stats.counting_event.value,
        INTERVAL_MINUTES_KEY: config.interval_minutes,
        SPEED_PROFILE_INTERVAL_MINUTES_KEY: config.speed_profile_interval_minutes,
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
        STATE_KEY: {
            ROAD_USER_IDS_KEY: sorted(stats.road_user_ids),
            SPEED_HISTOGRAMS_KEY: _histograms_to_dict(stats),
        },
    }


def _format_datetime(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


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
        COUNTS_KEY: stats.counts(flow_id),
        TOTALS_KEY: stats.totals(flow_id),
        PEAK_HOUR_KEY: {
            group: _peak_to_dict(peak)
            for group, peak in stats.peak_hour(flow_id).items()
        },
        SPEED_KEY: {
            group: _speed_to_dict(values)
            for group, values in stats.speed(flow_id).items()
        },
        SPEED_PROFILE_KEY: {
            group: [None if v is None else _speed_to_dict(v) for v in slots]
            for group, slots in stats.speed_profile(flow_id).items()
        },
    }


def _peak_to_dict(peak: PeakHour) -> dict[str, Any]:
    return {
        START_KEY: peak.start.isoformat(),
        END_KEY: peak.end.isoformat(),
        COUNT_KEY: peak.count,
    }


def _speed_to_dict(values: SpeedValues) -> dict[str, Any]:
    return {AVG_KEY: values.avg, V85_KEY: values.v85, COUNT_KEY: values.count}


def _histograms_to_dict(stats: DayTrafficStatistics) -> dict[str, Any]:
    return {
        flow: {
            group: [
                (
                    None
                    if histogram.count == 0
                    else {
                        BINS_KEY: {
                            str(key): n for key, n in sorted(histogram.bins.items())
                        },
                        TOTAL_SPEED_KEY: histogram.total_speed,
                    }
                )
                for histogram in slots
            ]
            for group, slots in groups.items()
        }
        for flow, groups in stats.histograms().items()
    }


def from_dict(
    data: dict[str, Any], config: TrafficStatisticsConfig
) -> DayTrafficStatistics:
    """Restore a statistics from the file format (v1).

    timezone, interval_minutes, speed_profile_interval_minutes and class_groups
    of the file must match the config, because the stored counts and speed
    histograms depend on them. peak_window_minutes and peak_step_minutes only
    affect derived values: the restored statistics uses the values of the given
    config, so changing them on resume is allowed.

    Raises:
        TrafficStatisticsFormatError: if the data is not a valid v1 file or
            does not match the given config.
    """
    try:
        return _from_dict(data, config)
    except TrafficStatisticsFormatError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError) as cause:
        raise TrafficStatisticsFormatError(
            f"Invalid traffic statistics data: {cause!r}"
        ) from cause


def _from_dict(
    data: dict[str, Any], config: TrafficStatisticsConfig
) -> DayTrafficStatistics:
    if not isinstance(data, dict):
        raise TrafficStatisticsFormatError("Traffic statistics must be a JSON object.")
    if data.get(FORMAT_KEY) != FORMAT:
        raise TrafficStatisticsFormatError(f"Unknown format: {data.get(FORMAT_KEY)!r}.")
    if data.get(VERSION_KEY) != VERSION:
        raise TrafficStatisticsFormatError(
            f"Unknown version: {data.get(VERSION_KEY)!r}."
        )
    missing = [key for key in _TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise TrafficStatisticsFormatError(f"Missing keys: {missing}.")
    for key, expected in (
        (TIMEZONE_KEY, config.timezone),
        (INTERVAL_MINUTES_KEY, config.interval_minutes),
        (SPEED_PROFILE_INTERVAL_MINUTES_KEY, config.speed_profile_interval_minutes),
    ):
        if data[key] != expected:
            raise TrafficStatisticsFormatError(
                f"{key} of the file ({data[key]!r}) differs from the config "
                f"({expected!r})."
            )
    _check_class_groups(data[CLASS_GROUPS_KEY], config)
    day = date.fromisoformat(data[DAY_KEY])
    flows = [_flow_from_dict(entry) for entry in data[FLOWS_KEY]]
    flow_ids = {flow.id for flow in flows}
    minutes = minutes_in_day(day, ZoneInfo(config.timezone))
    interval_count = _ceil_div(minutes, config.interval_minutes)
    slot_count = _ceil_div(minutes, config.speed_profile_interval_minutes)
    raw_counts = _counts_from_dict(
        data[STATISTICS_KEY][FLOWS_KEY], flow_ids, interval_count
    )
    histograms = _histograms_from_dict(
        data[STATE_KEY][SPEED_HISTOGRAMS_KEY], flow_ids, slot_count
    )
    coverage = [
        (datetime.fromisoformat(start), datetime.fromisoformat(end))
        for start, end in data[COVERAGE_KEY]
    ]
    as_of = None if data[AS_OF_KEY] is None else datetime.fromisoformat(data[AS_OF_KEY])
    return DayTrafficStatistics.restore(
        day=day,
        config=config,
        flows=flows,
        raw_counts=raw_counts,
        histograms=histograms,
        coverage=coverage,
        road_user_ids=[str(i) for i in data[STATE_KEY][ROAD_USER_IDS_KEY]],
        as_of=as_of,
        counting_event=CountingEvent.parse(data[COUNTING_EVENT_KEY]),
    )


def _check_class_groups(file_groups: Any, config: TrafficStatisticsConfig) -> None:
    file_mapping = {
        group: frozenset(classifications)
        for group, classifications in file_groups.items()
    }
    config_mapping = {
        group: frozenset(classifications)
        for group, classifications in config.class_groups.items()
    }
    if file_mapping != config_mapping:
        raise TrafficStatisticsFormatError(
            f"{CLASS_GROUPS_KEY} of the file ({file_groups!r}) differ from the config "
            f"({config_mapping!r})."
        )


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _flow_from_dict(entry: dict[str, Any]) -> FlowInfo:
    return FlowInfo(
        id=entry[ID_KEY],
        name=entry[NAME_KEY],
        index=entry[INDEX_KEY],
        start_section_id=entry[START_SECTION_KEY][ID_KEY],
        start_section_name=entry[START_SECTION_KEY][NAME_KEY],
        end_section_id=entry[END_SECTION_KEY][ID_KEY],
        end_section_name=entry[END_SECTION_KEY][NAME_KEY],
    )


def _counts_from_dict(
    flows: dict[str, Any], flow_ids: set[str], interval_count: int
) -> dict[str, dict[str, list[int]]]:
    result: dict[str, dict[str, list[int]]] = {}
    for flow_id, block in flows.items():
        if flow_id not in flow_ids:
            raise TrafficStatisticsFormatError(f"Unknown flow '{flow_id}' in counts.")
        groups: dict[str, list[int]] = {}
        for group, values in block[COUNTS_KEY].items():
            if len(values) != interval_count:
                raise TrafficStatisticsFormatError(
                    f"counts of flow '{flow_id}' group '{group}' has "
                    f"{len(values)} entries, expected {interval_count}."
                )
            ints = [0 if value is None else int(value) for value in values]
            # Groups without any count were never recorded, only reported.
            if any(ints):
                groups[group] = ints
        if groups:
            result[flow_id] = groups
    return result


def _histograms_from_dict(
    flows: dict[str, Any], flow_ids: set[str], slot_count: int
) -> dict[str, dict[str, list[SpeedHistogram]]]:
    result: dict[str, dict[str, list[SpeedHistogram]]] = {}
    for flow_id, groups in flows.items():
        if flow_id not in flow_ids:
            raise TrafficStatisticsFormatError(
                f"Unknown flow '{flow_id}' in speed histograms."
            )
        restored: dict[str, list[SpeedHistogram]] = {}
        for group, slots in groups.items():
            if len(slots) != slot_count:
                raise TrafficStatisticsFormatError(
                    f"speed histograms of flow '{flow_id}' group '{group}' has "
                    f"{len(slots)} slots, expected {slot_count}."
                )
            restored[group] = [_histogram_from_dict(slot) for slot in slots]
        result[flow_id] = restored
    return result


def _histogram_from_dict(slot: dict[str, Any] | None) -> SpeedHistogram:
    if slot is None:
        return SpeedHistogram()
    bins = {int(key): int(value) for key, value in slot[BINS_KEY].items()}
    return SpeedHistogram(bins, float(slot[TOTAL_SPEED_KEY]))


def write(stats: DayTrafficStatistics, path: Path) -> None:
    """Write the statistics atomically to the path, see atomic_write."""
    content = json.dumps(to_dict(stats), ensure_ascii=False)
    with atomic_write(path) as file:
        file.write(content.encode("utf-8"))


def read(path: Path, config: TrafficStatisticsConfig) -> DayTrafficStatistics:
    """Read a statistics file.

    Raises:
        TrafficStatisticsFormatError: if the file is not valid JSON or does not
            fit the format or config.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as cause:
        raise TrafficStatisticsFormatError(f"Corrupt file {path}: {cause}") from cause
    return from_dict(data, config)
