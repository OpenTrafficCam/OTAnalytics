import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    ClassGroupResolver,
    DayTrafficStatistics,
    FlowInfo,
    assignment_to_entry,
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
from OTAnalytics.plugin_parser.traffic_statistics_json import (
    TrafficStatisticsFormatError,
    read,
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
    `max_open_days` most recent ones), resumed from an existing day file at
    first contact and rewritten completely after every call. Assignments of
    days that were already evicted are dropped with a warning.

    Flows are rebuilt from the repositories on every call. A resumed day file
    is read with its stored flows; a stored flow id unknown to the file itself
    is rejected by the codec with a TrafficStatisticsFormatError.
    """

    def __init__(
        self,
        get_assignments: GetRoadUserAssignments,
        get_all_flows: GetAllFlows,
        get_all_sections: GetAllSections,
        max_open_days: int = 2,
    ) -> None:
        self._get_assignments = get_assignments
        self._get_all_flows = get_all_flows
        self._get_all_sections = get_all_sections
        self._max_open_days = max_open_days
        self._days: dict[date, DayTrafficStatistics] = {}
        self._evicted: set[date] = set()
        self._resolver: ClassGroupResolver | None = None

    def export(self, specification: TrafficStatisticsExportSpecification) -> list[Path]:
        config = specification.config
        tz = ZoneInfo(config.timezone)
        if self._resolver is None:
            self._resolver = ClassGroupResolver(config)
        flows = self._build_flows()
        touched: dict[date, int] = {}
        counted: dict[date, datetime] = {}
        dropped = 0

        for assignment in self._get_assignments.get_as_list():
            entry = assignment_to_entry(
                assignment, specification.counting_event, self._resolver, tz
            )
            if entry is None:
                continue
            road_user, flow_id, group, occurrence, speed = entry
            day = occurrence.date()
            if day in self._evicted:
                dropped += 1
                continue
            stats = self._get_day(day, specification, flows)
            touched[day] = 0
            if stats.add(road_user, flow_id, group, occurrence, speed):
                if day not in counted or occurrence > counted[day]:
                    counted[day] = occurrence

        if dropped:
            LOGGER.warning(
                "Dropped %s assignment(s) belonging to days that are no longer "
                "kept open.",
                dropped,
            )

        covered_start = _as_utc(specification.covered_start)
        covered_end = _as_utc(specification.covered_end)
        for day in self._coverage_days(covered_start, covered_end, tz):
            if day in self._evicted:
                continue
            self._get_day(day, specification, flows)
            touched[day] = 0

        paths = []
        for day in sorted(touched):
            stats = self._days[day]
            stats.mark_covered(covered_start, covered_end)
            self._update_as_of(stats, counted.get(day), covered_end, tz)
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
        covered_end: datetime,
        tz: ZoneInfo,
    ) -> None:
        """Set as_of to the latest processed timestamp of the day.

        It is the maximum of the previous as_of, the latest occurrence counted
        in this call and the end of the coverage clipped to the day.
        """
        day_end = _as_utc(day_start(stats.day + timedelta(days=1), tz))
        candidates = [min(covered_end, day_end)]
        if stats.as_of is not None:
            candidates.append(_as_utc(stats.as_of))
        if counted is not None:
            candidates.append(_as_utc(counted))
        stats.as_of = max(candidates).astimezone(tz)

    def _get_day(
        self,
        day: date,
        specification: TrafficStatisticsExportSpecification,
        flows: list[FlowInfo],
    ) -> DayTrafficStatistics:
        stats = self._days.get(day)
        if stats is not None:
            return stats
        path = self._path(specification, day)
        if path.exists():
            stats = read(path, specification.config)
            if stats.counting_event != specification.counting_event:
                raise TrafficStatisticsFormatError(
                    f"counting_event of {path} ({stats.counting_event}) differs "
                    f"from the export ({specification.counting_event})."
                )
        else:
            stats = DayTrafficStatistics(
                day, specification.config, flows, specification.counting_event
            )
        self._days[day] = stats
        return stats

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
