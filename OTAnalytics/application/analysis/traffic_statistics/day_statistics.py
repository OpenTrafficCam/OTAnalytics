"""Per local day statistics of road users per flow and class group."""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Sequence
from zoneinfo import ZoneInfo

from OTAnalytics.application.analysis.road_user_assignment import RoadUserAssignment
from OTAnalytics.application.analysis.traffic_counting import aggregation_time
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_values import (
    SpeedValues,
    compute_speed_values,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)

LOGGER = logging.getLogger(__name__)

TOTAL = "total"


@dataclass(frozen=True)
class FlowInfo:
    """Descriptive data of a flow in the statistics."""

    id: str
    name: str
    index: int
    start_section_id: str
    start_section_name: str
    end_section_id: str
    end_section_name: str


@dataclass(frozen=True)
class PeakHour:
    """Strongest sliding window of a group: local start, end and count."""

    start: datetime
    end: datetime
    count: int


def day_start(day: date, tz: ZoneInfo) -> datetime:
    """Return the timezone aware start of the given local day."""
    return datetime(day.year, day.month, day.day, tzinfo=tz)


def minutes_in_day(day: date, tz: ZoneInfo) -> int:
    """Return the real number of minutes of the local day (DST aware)."""
    start = day_start(day, tz).astimezone(timezone.utc)
    end = day_start(day + timedelta(days=1), tz).astimezone(timezone.utc)
    return int((end - start).total_seconds() // 60)


class ClassGroupResolver:
    """Maps classifications to class groups defined in the config.

    Without configured class groups every classification is its own group.
    Unknown classifications resolve to None and are warned about once.
    """

    def __init__(self, config: TrafficStatisticsConfig) -> None:
        self._lookup: dict[str, str] = {
            classification: group
            for group, classifications in config.class_groups.items()
            for classification in classifications
        }
        self._use_identity = not config.class_groups
        self._warned: set[str] = set()

    def group_of(self, classification: str) -> str | None:
        """Return the group of the classification or None if it is unknown."""
        if self._use_identity:
            return classification
        group = self._lookup.get(classification)
        if group is None and classification not in self._warned:
            self._warned.add(classification)
            LOGGER.warning(
                "Classification '%s' is not part of any class group. "
                "Road users of this classification are ignored.",
                classification,
            )
        return group


def _as_utc(value: datetime) -> datetime:
    """Return the datetime in UTC, treating naive values as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


class DayTrafficStatistics:
    """Counts and speeds of one local day per flow and class group.

    Counts are kept per interval of `config.interval_minutes`. An interval is
    reported as covered if it overlaps any range marked with `mark_covered`.
    Uncovered intervals without counts are reported as None. A road user is
    counted at most once per day, regardless of flow and class group.
    """

    def __init__(
        self,
        day: date,
        config: TrafficStatisticsConfig,
        flows: Sequence[FlowInfo],
        counting_event: CountingEvent = CountingEvent.START,
    ) -> None:
        self.day = day
        self.flows = list(flows)
        self.counting_event = counting_event
        self.as_of: datetime | None = None
        self.road_user_ids: set[str] = set()
        self._config = config
        self._tz = ZoneInfo(config.timezone)
        self._start = _as_utc(day_start(day, self._tz))
        self._end = _as_utc(day_start(day + timedelta(days=1), self._tz))
        minutes = minutes_in_day(day, self._tz)
        self._interval_count = _ceil_div(minutes, config.interval_minutes)
        self._slot_count = _ceil_div(minutes, config.speed_profile_interval_minutes)
        self._flow_ids = {flow.id for flow in self.flows}
        self._counts: dict[str, dict[str, list[int]]] = {}
        # flow -> group -> speed profile slot -> plausible speeds in km/h
        self._speeds: dict[str, dict[str, list[list[float]]]] = {}
        self._coverage: list[tuple[datetime, datetime]] = []

    @property
    def config(self) -> TrafficStatisticsConfig:
        """The configuration this statistics was created with."""
        return self._config

    @property
    def coverage(self) -> list[tuple[datetime, datetime]]:
        """Merged, sorted half-open coverage ranges in the local timezone."""
        return [(start, end) for start, end in self._coverage]

    def add(
        self,
        road_user: str,
        flow_id: str,
        group: str,
        occurrence: datetime,
        speed_kmh: float | None,
    ) -> bool:
        """Count a road user; return False for duplicate, other day or unknown flow.

        Speeds are stored only if plausible (0 < speed <= max_speed_kmh).
        """
        when = _as_utc(occurrence)
        if flow_id not in self._flow_ids or not self._start <= when < self._end:
            return False
        if road_user in self.road_user_ids:
            return False
        self.road_user_ids.add(road_user)
        minutes = int((when - self._start).total_seconds() // 60)
        counts = self._counts.setdefault(flow_id, {})
        counts.setdefault(group, [0] * self._interval_count)[
            minutes // self._config.interval_minutes
        ] += 1
        if speed_kmh is not None and 0 < speed_kmh <= self._config.max_speed_kmh:
            slots = self._speeds.setdefault(flow_id, {}).setdefault(
                group, [[] for _ in range(self._slot_count)]
            )
            slots[minutes // self._config.speed_profile_interval_minutes].append(
                speed_kmh
            )
        return True

    def update_flows(self, flows: Sequence[FlowInfo]) -> None:
        """Reconcile the flows with the current ones, keeping all per-flow state.

        The result is the given flows (in the given order, with their current
        name and index) followed by previously known flows that are not part of
        them. Those keep their data so that totals stay intact.
        """
        current_ids = {flow.id for flow in flows}
        retired = [flow for flow in self.flows if flow.id not in current_ids]
        self.flows = [*flows, *retired]
        self._flow_ids = {flow.id for flow in self.flows}

    def mark_covered(self, start: datetime, end: datetime) -> None:
        """Mark the half-open range [start, end) as covered, clipped to the day."""
        clipped_start = max(_as_utc(start), self._start)
        clipped_end = min(_as_utc(end), self._end)
        if clipped_start >= clipped_end:
            return
        ranges = sorted(
            [*self._coverage_utc(), (clipped_start, clipped_end)], key=lambda r: r[0]
        )
        merged: list[tuple[datetime, datetime]] = []
        for range_start, range_end in ranges:
            if merged and range_start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], range_end))
            else:
                merged.append((range_start, range_end))
        self._coverage = [
            (s.astimezone(self._tz), e.astimezone(self._tz)) for s, e in merged
        ]

    def _coverage_utc(self) -> list[tuple[datetime, datetime]]:
        return [(_as_utc(s), _as_utc(e)) for s, e in self._coverage]

    def _covered_flags(self) -> list[bool]:
        """Flag per interval whether it overlaps any coverage range."""
        step = timedelta(minutes=self._config.interval_minutes)
        coverage = self._coverage_utc()
        flags = []
        for index in range(self._interval_count):
            interval_start = self._start + index * step
            interval_end = interval_start + step
            flags.append(
                any(s < interval_end and interval_start < e for s, e in coverage)
            )
        return flags

    def _flow_counts(self, flow_id: str) -> dict[str, list[int]]:
        if flow_id == TOTAL:
            totals: dict[str, list[int]] = {}
            for flow_counts in self._counts.values():
                for group, values in flow_counts.items():
                    current = totals.setdefault(group, [0] * self._interval_count)
                    for index, value in enumerate(values):
                        current[index] += value
            return totals
        return self._counts.get(flow_id, {})

    def counts(self, flow_id: str) -> dict[str, list[int | None]]:
        """Counts per group and interval; TOTAL sums all flows.

        An interval is None if it is not covered and has no count.
        """
        covered = self._covered_flags()
        result: dict[str, list[int | None]] = {
            group: [0 if flag else None for flag in covered]
            for group in self._config.class_groups
        }
        for group, values in self._flow_counts(flow_id).items():
            result[group] = [
                value if value > 0 or covered[index] else None
                for index, value in enumerate(values)
            ]
        return result

    def totals(self, flow_id: str) -> dict[str, int]:
        """Number of counted road users per group; TOTAL sums all flows."""
        return {
            group: sum(values) for group, values in self._flow_counts(flow_id).items()
        }

    def peak_hour(self, flow_id: str) -> dict[str, PeakHour]:
        """Strongest window per group; TOTAL sums all flows.

        Windows start every `peak_step_minutes` from the start of the day, are
        `peak_window_minutes` long and lie completely within the day. None
        counts are ignored, windows with only None are skipped and ties go to
        the earliest window. Groups without data are absent.
        """
        interval = self._config.interval_minutes
        window = max(1, self._config.peak_window_minutes // interval)
        step = max(1, self._config.peak_step_minutes // interval)
        day_minutes = minutes_in_day(self.day, self._tz)
        recorded = self._flow_counts(flow_id)
        result: dict[str, PeakHour] = {}
        for group, values in self.counts(flow_id).items():
            if group not in recorded:
                continue
            best: tuple[int, int] | None = None
            for first in range(0, len(values), step):
                if first * interval + window * interval > day_minutes:
                    break
                found = [v for v in values[first : first + window] if v is not None]
                if found and (best is None or sum(found) > best[0]):
                    best = (sum(found), first)
            if best is not None:
                count, first = best
                start = self._start + timedelta(minutes=first * interval)
                end = start + timedelta(minutes=window * interval)
                result[group] = PeakHour(
                    start=start.astimezone(self._tz),
                    end=end.astimezone(self._tz),
                    count=count,
                )
        return result

    def _flow_speeds(self, flow_id: str) -> dict[str, list[list[float]]]:
        if flow_id != TOTAL:
            return self._speeds.get(flow_id, {})
        merged: dict[str, list[list[float]]] = {}
        for groups in self._speeds.values():
            for group, slots in groups.items():
                current = merged.setdefault(
                    group, [[] for _ in range(self._slot_count)]
                )
                for index, speeds in enumerate(slots):
                    current[index].extend(speeds)
        return merged

    def speed(self, flow_id: str) -> dict[str, SpeedValues]:
        """Speed values per group over the whole day; TOTAL merges all flows.

        Groups without plausible speeds are absent.
        """
        result: dict[str, SpeedValues] = {}
        for group, slots in self._flow_speeds(flow_id).items():
            values = compute_speed_values([s for speeds in slots for s in speeds])
            if values is not None:
                result[group] = values
        return result

    def speed_profile(self, flow_id: str) -> dict[str, list[SpeedValues | None]]:
        """Speed values per group and speed profile slot; TOTAL merges flows.

        Contains every configured and counted group. Slots without plausible
        speeds are None.
        """
        result: dict[str, list[SpeedValues | None]] = {
            group: [None] * self._slot_count
            for group in [*self._config.class_groups, *self._flow_counts(flow_id)]
        }
        for group, slots in self._flow_speeds(flow_id).items():
            result[group] = [compute_speed_values(speeds) for speeds in slots]
        return result


@dataclass(frozen=True)
class AssignmentRecord:
    """The data of a road user assignment the traffic statistics need.

    Live assignments and restored road user assignment files are both converted
    to this record. The occurrences are the interpolated ones, as in counting.
    """

    road_user: str
    flow_id: str
    road_user_type: str
    start_occurrence: datetime
    end_occurrence: datetime
    avg_speed_mps: float | None

    @staticmethod
    def from_assignment(assignment: RoadUserAssignment) -> "AssignmentRecord":
        return AssignmentRecord(
            road_user=assignment.road_user,
            flow_id=assignment.assignment.id.id,
            road_user_type=assignment.road_user_type,
            start_occurrence=aggregation_time(assignment, CountingEvent.START),
            end_occurrence=aggregation_time(assignment, CountingEvent.END),
            avg_speed_mps=assignment.flow_metrics().avg_speed_mps,
        )


def record_to_entry(
    record: AssignmentRecord,
    counting_event: CountingEvent,
    resolver: ClassGroupResolver,
    tz: ZoneInfo,
) -> tuple[str, str, str, datetime, float | None] | None:
    """Convert a record to the arguments of `DayTrafficStatistics.add`.

    Returns (road_user, flow_id, group, local occurrence, speed in km/h) or None
    if the road user's classification belongs to no class group. Naive
    occurrences are treated as UTC.
    """
    group = resolver.group_of(record.road_user_type)
    if group is None:
        return None
    occurrence = (
        record.end_occurrence
        if counting_event == CountingEvent.END
        else record.start_occurrence
    )
    speed_mps = record.avg_speed_mps
    speed_kmh = None if speed_mps is None else speed_mps * 3.6
    return (
        record.road_user,
        record.flow_id,
        group,
        _as_utc(occurrence).astimezone(tz),
        speed_kmh,
    )
