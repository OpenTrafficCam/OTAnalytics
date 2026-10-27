"""JSON codec for the daily traffic statistics files."""

import json
import os
import tempfile
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

FORMAT = "otanalytics.traffic_statistics"
VERSION = 1

_TOP_LEVEL_KEYS = (
    "format",
    "version",
    "day",
    "timezone",
    "counting_event",
    "interval_minutes",
    "speed_profile_interval_minutes",
    "peak_window_minutes",
    "peak_step_minutes",
    "class_groups",
    "as_of",
    "coverage",
    "flows",
    "statistics",
    "state",
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
        "format": FORMAT,
        "version": VERSION,
        "day": stats.day.isoformat(),
        "timezone": config.timezone,
        "counting_event": stats.counting_event.value,
        "interval_minutes": config.interval_minutes,
        "speed_profile_interval_minutes": config.speed_profile_interval_minutes,
        "peak_window_minutes": config.peak_window_minutes,
        "peak_step_minutes": config.peak_step_minutes,
        "class_groups": {
            group: sorted(classifications)
            for group, classifications in config.class_groups.items()
        },
        "as_of": _format_datetime(stats.as_of),
        "coverage": [
            [_format_datetime(start), _format_datetime(end)]
            for start, end in stats.coverage
        ],
        "flows": [_flow_to_dict(flow) for flow in stats.flows],
        "statistics": {
            "total": _statistics_block(stats, TOTAL),
            "flows": flow_statistics,
        },
        "state": {
            "road_user_ids": sorted(stats.road_user_ids),
            "speed_histograms": _histograms_to_dict(stats),
        },
    }


def _format_datetime(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _flow_to_dict(flow: FlowInfo) -> dict[str, Any]:
    return {
        "id": flow.id,
        "name": flow.name,
        "index": flow.index,
        "start_section": {"id": flow.start_section_id, "name": flow.start_section_name},
        "end_section": {"id": flow.end_section_id, "name": flow.end_section_name},
    }


def _statistics_block(stats: DayTrafficStatistics, flow_id: str) -> dict[str, Any]:
    return {
        "counts": stats.counts(flow_id),
        "totals": stats.totals(flow_id),
        "peak_hour": {
            group: _peak_to_dict(peak)
            for group, peak in stats.peak_hour(flow_id).items()
        },
        "speed": {
            group: _speed_to_dict(values)
            for group, values in stats.speed(flow_id).items()
        },
        "speed_profile": {
            group: [None if v is None else _speed_to_dict(v) for v in slots]
            for group, slots in stats.speed_profile(flow_id).items()
        },
    }


def _peak_to_dict(peak: PeakHour) -> dict[str, Any]:
    return {
        "start": peak.start.isoformat(),
        "end": peak.end.isoformat(),
        "count": peak.count,
    }


def _speed_to_dict(values: SpeedValues) -> dict[str, Any]:
    return {"avg": values.avg, "v85": values.v85, "count": values.count}


def _histograms_to_dict(stats: DayTrafficStatistics) -> dict[str, Any]:
    return {
        flow: {
            group: [
                (
                    None
                    if histogram.count == 0
                    else {
                        "bins": {
                            str(key): n for key, n in sorted(histogram.bins.items())
                        },
                        "total_speed": histogram.total_speed,
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
    if data.get("format") != FORMAT:
        raise TrafficStatisticsFormatError(f"Unknown format: {data.get('format')!r}.")
    if data.get("version") != VERSION:
        raise TrafficStatisticsFormatError(f"Unknown version: {data.get('version')!r}.")
    missing = [key for key in _TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise TrafficStatisticsFormatError(f"Missing keys: {missing}.")
    for key in (
        "timezone",
        "interval_minutes",
        "speed_profile_interval_minutes",
    ):
        if data[key] != getattr(config, key):
            raise TrafficStatisticsFormatError(
                f"{key} of the file ({data[key]!r}) differs from the config "
                f"({getattr(config, key)!r})."
            )
    _check_class_groups(data["class_groups"], config)
    day = date.fromisoformat(data["day"])
    flows = [_flow_from_dict(entry) for entry in data["flows"]]
    flow_ids = {flow.id for flow in flows}
    minutes = minutes_in_day(day, ZoneInfo(config.timezone))
    interval_count = _ceil_div(minutes, config.interval_minutes)
    slot_count = _ceil_div(minutes, config.speed_profile_interval_minutes)
    raw_counts = _counts_from_dict(
        data["statistics"]["flows"], flow_ids, interval_count
    )
    histograms = _histograms_from_dict(
        data["state"]["speed_histograms"], flow_ids, slot_count
    )
    coverage = [
        (datetime.fromisoformat(start), datetime.fromisoformat(end))
        for start, end in data["coverage"]
    ]
    as_of = None if data["as_of"] is None else datetime.fromisoformat(data["as_of"])
    return DayTrafficStatistics.restore(
        day=day,
        config=config,
        flows=flows,
        raw_counts=raw_counts,
        histograms=histograms,
        coverage=coverage,
        road_user_ids=[str(i) for i in data["state"]["road_user_ids"]],
        as_of=as_of,
        counting_event=CountingEvent.parse(data["counting_event"]),
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
            f"class_groups of the file ({file_groups!r}) differ from the config "
            f"({config_mapping!r})."
        )


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _flow_from_dict(entry: dict[str, Any]) -> FlowInfo:
    return FlowInfo(
        id=entry["id"],
        name=entry["name"],
        index=entry["index"],
        start_section_id=entry["start_section"]["id"],
        start_section_name=entry["start_section"]["name"],
        end_section_id=entry["end_section"]["id"],
        end_section_name=entry["end_section"]["name"],
    )


def _counts_from_dict(
    flows: dict[str, Any], flow_ids: set[str], interval_count: int
) -> dict[str, dict[str, list[int]]]:
    result: dict[str, dict[str, list[int]]] = {}
    for flow_id, block in flows.items():
        if flow_id not in flow_ids:
            raise TrafficStatisticsFormatError(f"Unknown flow '{flow_id}' in counts.")
        groups: dict[str, list[int]] = {}
        for group, values in block["counts"].items():
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
    bins = {int(key): int(value) for key, value in slot["bins"].items()}
    return SpeedHistogram(bins, float(slot["total_speed"]))


def write(stats: DayTrafficStatistics, path: Path) -> None:
    """Write the statistics atomically to the path.

    The content is written to a temp file in the same directory, flushed to
    disk and then moved over the path with os.replace.
    """
    content = json.dumps(to_dict(stats), ensure_ascii=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


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
