"""Per UTC day statistics of road users per flow and class group."""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, NamedTuple, Sequence

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
HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = HOURS_PER_DAY * MINUTES_PER_HOUR
SECONDS_PER_MINUTE = 60
KMH_PER_MPS = 3.6


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
    """Strongest sliding window of a group: UTC start, end and count."""

    start: datetime
    end: datetime
    count: int


class CoverageRange(NamedTuple):
    """Half-open UTC range [start, end) covered by input data."""

    start: datetime
    end: datetime


def merge_ranges(ranges: Iterable[CoverageRange]) -> list[CoverageRange]:
    """Merge overlapping or touching ranges into sorted, disjoint ranges."""
    merged: list[CoverageRange] = []
    current: CoverageRange | None = None
    for candidate in sorted(ranges):
        if current is not None and candidate.start <= current.end:
            current = CoverageRange(current.start, max(current.end, candidate.end))
            continue
        if current is not None:
            merged.append(current)
        current = candidate
    if current is not None:
        merged.append(current)
    return merged


def day_start(day: date) -> datetime:
    """Return the start of the given UTC day."""
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc)


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


def as_utc(value: datetime) -> datetime:
    """Return the datetime as UTC without converting it.

    Times of the input files are the camera's UTC times and the truth, so they
    are never converted. Naive values are taken as UTC.

    Raises:
        ValueError: if the value has an offset other than UTC.
    """
    if value.tzinfo is not None and value.utcoffset() != timedelta(0):
        raise ValueError(f"Expected a UTC time, got {value.isoformat()}.")
    return value.replace(tzinfo=timezone.utc)


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


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

    def occurrence(self, counting_event: CountingEvent) -> datetime:
        """Return the occurrence of the counting event in UTC.

        Naive occurrences are treated as UTC.
        """
        if counting_event == CountingEvent.END:
            return as_utc(self.end_occurrence)
        return as_utc(self.start_occurrence)

    @property
    def speed_kmh(self) -> float | None:
        """Average speed in km/h or None if unknown."""
        if self.avg_speed_mps is None:
            return None
        return self.avg_speed_mps * KMH_PER_MPS


class DayTrafficStatistics:
    """Counts and speeds of one UTC day per flow and class group.

    Counts and speeds are kept per interval of `config.interval_minutes`. An
    interval is reported as covered if it overlaps any range marked with
    `mark_covered`. Uncovered intervals without counts are reported as None. A
    road user is counted at most once per day, regardless of flow and class
    group.
    """

    def __init__(
        self,
        day: date,
        config: TrafficStatisticsConfig,
        flows: Sequence[FlowInfo],
        counting_event: CountingEvent = CountingEvent.START,
        resolver: ClassGroupResolver | None = None,
    ) -> None:
        self.day = day
        self.flows = list(flows)
        self.counting_event = counting_event
        self.as_of: datetime | None = None
        self.road_user_ids: set[str] = set()
        self._config = config
        self._resolver = resolver or ClassGroupResolver(config)
        self._start = day_start(day)
        self._end = day_start(day + timedelta(days=1))
        self._interval_count = _ceil_div(MINUTES_PER_DAY, config.interval_minutes)
        self._flow_ids = {flow.id for flow in self.flows}
        self._counts: dict[str, dict[str, list[int]]] = {}
        # flow -> group -> interval -> plausible speeds in km/h
        self._speeds: dict[str, dict[str, list[list[float]]]] = {}
        self._coverage: list[CoverageRange] = []

    @property
    def config(self) -> TrafficStatisticsConfig:
        """The configuration this statistics was created with."""
        return self._config

    @property
    def coverage(self) -> list[tuple[datetime, datetime]]:
        """Merged, sorted half-open coverage ranges in UTC."""
        return [(start, end) for start, end in self._coverage]

    def add(self, record: AssignmentRecord) -> bool:
        """Count a road user.

        Return False for a duplicate, another day, an unknown flow or a
        classification in no class group. Speeds are stored only if plausible
        (0 < speed <= max_speed_kmh).
        """
        group = self._resolver.group_of(record.road_user_type)
        when = record.occurrence(self.counting_event)
        if (
            group is None
            or record.flow_id not in self._flow_ids
            or not self._start <= when < self._end
        ):
            return False
        if record.road_user in self.road_user_ids:
            return False
        self.road_user_ids.add(record.road_user)
        minutes = int((when - self._start).total_seconds() // SECONDS_PER_MINUTE)
        index = minutes // self._config.interval_minutes
        counts = self._counts.setdefault(record.flow_id, {})
        counts.setdefault(group, [0] * self._interval_count)[index] += 1
        speed_kmh = record.speed_kmh
        if speed_kmh is not None and 0 < speed_kmh <= self._config.max_speed_kmh:
            intervals = self._speeds.setdefault(record.flow_id, {}).setdefault(
                group, [[] for _ in range(self._interval_count)]
            )
            intervals[index].append(speed_kmh)
        return True

    def mark_covered(self, start: datetime, end: datetime) -> None:
        """Mark the half-open range [start, end) as covered, clipped to the day."""
        clipped_start = max(as_utc(start), self._start)
        clipped_end = min(as_utc(end), self._end)
        if clipped_start >= clipped_end:
            return
        self._coverage = merge_ranges(
            [*self._coverage, CoverageRange(clipped_start, clipped_end)]
        )

    def covered_intervals(self) -> list[bool]:
        """Flag per interval whether it overlaps any coverage range."""
        step = timedelta(minutes=self._config.interval_minutes)
        coverage = self._coverage
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

    def interval_start(self, index: int) -> datetime:
        """Return the UTC start of the interval with the given index."""
        return self._start + timedelta(minutes=index * self._config.interval_minutes)

    def counts(self, flow_id: str) -> dict[str, list[int | None]]:
        """Counts per group and interval; TOTAL sums all flows.

        An interval is None if it is not covered and has no count.
        """
        covered = self.covered_intervals()
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
        recorded = self._flow_counts(flow_id)
        result: dict[str, PeakHour] = {}
        for group, values in self.counts(flow_id).items():
            if group not in recorded:
                continue
            best: tuple[int, int] | None = None
            for first in range(0, len(values), step):
                if first * interval + window * interval > MINUTES_PER_DAY:
                    break
                found = [v for v in values[first : first + window] if v is not None]
                if found and (best is None or sum(found) > best[0]):
                    best = (sum(found), first)
            if best is not None:
                count, first = best
                start = self.interval_start(first)
                end = start + timedelta(minutes=window * interval)
                result[group] = PeakHour(start=start, end=end, count=count)
        return result

    def _flow_speeds(self, flow_id: str) -> dict[str, list[list[float]]]:
        if flow_id != TOTAL:
            return self._speeds.get(flow_id, {})
        merged: dict[str, list[list[float]]] = {}
        for groups in self._speeds.values():
            for group, intervals in groups.items():
                current = merged.setdefault(
                    group, [[] for _ in range(self._interval_count)]
                )
                for index, speeds in enumerate(intervals):
                    current[index].extend(speeds)
        return merged

    def speed(self, flow_id: str) -> dict[str, SpeedValues]:
        """Speed values per group over the whole day; TOTAL merges all flows.

        Groups without plausible speeds are absent.
        """
        result: dict[str, SpeedValues] = {}
        for group, intervals in self._flow_speeds(flow_id).items():
            values = compute_speed_values([s for speeds in intervals for s in speeds])
            if values is not None:
                result[group] = values
        return result

    def speed_profile(self, flow_id: str) -> dict[str, list[SpeedValues | None]]:
        """Speed values per group and interval; TOTAL merges flows.

        Contains every configured and counted group. Intervals without
        plausible speeds are None.
        """
        result: dict[str, list[SpeedValues | None]] = {
            group: [None] * self._interval_count
            for group in [*self._config.class_groups, *self._flow_counts(flow_id)]
        }
        for group, intervals in self._flow_speeds(flow_id).items():
            result[group] = [compute_speed_values(speeds) for speeds in intervals]
        return result

    def total_speed_profile(self) -> list[SpeedValues | None]:
        """Speed values per interval over all flows and groups.

        Intervals without plausible speeds are None.
        """
        merged: list[list[float]] = [[] for _ in range(self._interval_count)]
        for intervals in self._flow_speeds(TOTAL).values():
            for index, speeds in enumerate(intervals):
                merged[index].extend(speeds)
        return [compute_speed_values(speeds) for speeds in merged]
