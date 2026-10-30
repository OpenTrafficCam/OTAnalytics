import logging
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence
from zoneinfo import ZoneInfo

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    AssignmentRecord,
    ClassGroupResolver,
    DayTrafficStatistics,
    FlowInfo,
    day_start,
)
from OTAnalytics.application.use_cases.assignment_repository import (
    GetRoadUserAssignments,
)
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.application.use_cases.section_repository import GetAllSections
from OTAnalytics.application.use_cases.traffic_statistics_export import (
    ExportTrafficStatistics,
    TrafficStatisticsExportSpecification,
)
from OTAnalytics.plugin_parser.road_user_assignment_csv_reader import (
    read_assignment_records,
)
from OTAnalytics.plugin_parser.traffic_statistics_json import (
    TrafficStatisticsFormatError,
    read_progress,
    write,
)

LOGGER = logging.getLogger(__name__)


def _as_utc(value: datetime) -> datetime:
    """Return the datetime in UTC, treating naive values as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class JsonTrafficStatisticsExporter(ExportTrafficStatistics):
    """Writes traffic statistics as JSON, one file per local day.

    The exporter is stateful across calls: days are kept in memory (the
    `max_open_days` most recent ones) and rewritten completely after every call.
    Assignments of days that were already evicted are dropped with a warning.

    When a day is opened, it is rebuilt from the road user assignment files in
    `restore_files` with the current settings; coverage and as_of are taken
    from an existing day file. Flows are rebuilt from the repositories on every
    call; data of flows that no longer exist is dropped.
    """

    def __init__(
        self,
        get_assignments: GetRoadUserAssignments,
        get_all_flows: GetAllFlows,
        get_all_sections: GetAllSections,
        restore_files: Sequence[Path] = (),
        max_open_days: int = 2,
    ) -> None:
        self._get_assignments = get_assignments
        self._get_all_flows = get_all_flows
        self._get_all_sections = get_all_sections
        self._max_open_days = max_open_days
        self._days: dict[date, DayTrafficStatistics] = {}
        self._evicted: set[date] = set()
        self._resolver: ClassGroupResolver | None = None
        self._restore_files = list(restore_files)
        self._restore_records: dict[date, list[AssignmentRecord]] | None = None

    def export(self, specification: TrafficStatisticsExportSpecification) -> list[Path]:
        config = specification.config
        tz = ZoneInfo(config.timezone)
        if self._resolver is None:
            self._resolver = ClassGroupResolver(config)
        if self._restore_records is None:
            self._restore_records = self._read_restore_records(
                specification.counting_event, tz
            )
        flows = self._build_flows()
        touched: set[date] = set()
        counted: dict[date, datetime] = {}
        dropped = 0

        for assignment in self._get_assignments.get_as_list():
            record = AssignmentRecord.from_assignment(assignment)
            occurrence = record.occurrence(specification.counting_event)
            day = occurrence.astimezone(tz).date()
            if day in self._evicted:
                dropped += 1
                continue
            stats = self._get_day(day, specification, flows)
            touched.add(day)
            if stats.add(record):
                if day not in counted or occurrence > counted[day]:
                    counted[day] = occurrence

        if dropped:
            LOGGER.warning(
                "Dropped %s assignment(s) belonging to days that are no longer "
                "kept open.",
                dropped,
            )

        covered_ranges = [
            (_as_utc(start), _as_utc(end))
            for start, end in specification.covered_ranges
        ]
        for covered_start, covered_end in covered_ranges:
            for day in self._coverage_days(covered_start, covered_end, tz):
                if day in self._evicted:
                    continue
                self._get_day(day, specification, flows)
                touched.add(day)

        paths = []
        for day in sorted(touched):
            stats = self._days[day]
            for covered_start, covered_end in covered_ranges:
                stats.mark_covered(covered_start, covered_end)
            self._update_as_of(stats, counted.get(day), covered_ranges, tz)
            path = self._path(specification, day)
            write(stats, path)
            paths.append(path)
        self._evict()
        return paths

    def _coverage_days(
        self, start: datetime, end: datetime, tz: ZoneInfo
    ) -> list[date]:
        """Local days overlapped by the half-open range [start, end)."""
        if start >= end:
            return []
        first = start.astimezone(tz).date()
        last = (end - timedelta(microseconds=1)).astimezone(tz).date()
        return [first + timedelta(days=i) for i in range((last - first).days + 1)]

    def _update_as_of(
        self,
        stats: DayTrafficStatistics,
        counted: datetime | None,
        covered_ranges: list[tuple[datetime, datetime]],
        tz: ZoneInfo,
    ) -> None:
        """Set as_of to the latest processed timestamp of the day.

        It is the maximum of the previous as_of, the latest occurrence counted
        in this call and the ends of the covered ranges clipped to the day
        (only of ranges overlapping the day).
        """
        day_begin = _as_utc(day_start(stats.day, tz))
        day_end = _as_utc(day_start(stats.day + timedelta(days=1), tz))
        candidates = []
        for covered_start, covered_end in covered_ranges:
            if covered_start < day_end and covered_end > day_begin:
                candidates.append(min(covered_end, day_end))
        if stats.as_of is not None:
            candidates.append(_as_utc(stats.as_of))
        if counted is not None:
            candidates.append(_as_utc(counted))
        if candidates:
            stats.as_of = max(candidates).astimezone(tz)

    def _get_day(
        self,
        day: date,
        specification: TrafficStatisticsExportSpecification,
        flows: list[FlowInfo],
    ) -> DayTrafficStatistics:
        stats = self._days.get(day)
        if stats is not None:
            stats.update_flows(flows)
            return stats
        stats = DayTrafficStatistics(
            day,
            specification.config,
            flows,
            specification.counting_event,
            self._resolver,
        )
        path = self._path(specification, day)
        if path.exists():
            try:
                progress = read_progress(path)
            except TrafficStatisticsFormatError as cause:
                LOGGER.warning(
                    "Ignoring coverage of unreadable day file %s: %s", path, cause
                )
            else:
                for covered_start, covered_end in progress.coverage:
                    stats.mark_covered(covered_start, covered_end)
                stats.as_of = progress.as_of
        for record in (self._restore_records or {}).get(day, []):
            stats.add(record)
        self._days[day] = stats
        return stats

    def _read_restore_records(
        self, counting_event: CountingEvent, tz: ZoneInfo
    ) -> dict[date, list[AssignmentRecord]]:
        """Read the restore files and group their records by local day."""
        records: dict[date, list[AssignmentRecord]] = defaultdict(list)
        for path in self._restore_files:
            for record in read_assignment_records(path):
                day = record.occurrence(counting_event).astimezone(tz).date()
                records[day].append(record)
        return records

    def _evict(self) -> None:
        for day in sorted(self._days, reverse=True)[self._max_open_days :]:
            del self._days[day]
            self._evicted.add(day)

    def _build_flows(self) -> list[FlowInfo]:
        sections = {s.id.id: s.name for s in self._get_all_sections()}
        return [
            FlowInfo(
                id=flow.id.id,
                name=flow.name,
                index=index,
                start_section_id=flow.start.id,
                start_section_name=sections.get(flow.start.id, flow.start.id),
                end_section_id=flow.end.id,
                end_section_name=sections.get(flow.end.id, flow.end.id),
            )
            for index, flow in enumerate(self._get_all_flows.get(), start=1)
        ]

    @staticmethod
    def _path(specification: TrafficStatisticsExportSpecification, day: date) -> Path:
        return specification.export_directory / (
            f"{specification.export_filename_stem}.traffic_statistics_"
            f"{day.isoformat()}.json"
        )
