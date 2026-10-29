import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    RoadUserAssignment,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    DayTrafficStatistics,
    FlowInfo,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from OTAnalytics.application.export_formats.export_mode import MERGE
from OTAnalytics.application.use_cases.traffic_statistics_export import (
    TrafficStatisticsExportSpecification,
)
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import SectionId
from OTAnalytics.plugin_parser.json_parser import parse_json
from OTAnalytics.plugin_parser.traffic_statistics_export import (
    JsonTrafficStatisticsExporter,
)
from OTAnalytics.plugin_parser.traffic_statistics_json import (
    COUNTS_KEY,
    FLOWS_KEY,
    ID_KEY,
    INDEX_KEY,
    NAME_KEY,
    START_SECTION_KEY,
    STATISTICS_KEY,
    TOTAL_KEY,
    TOTALS_KEY,
    TrafficStatisticsFormatError,
    read,
    write,
)
from tests.utils.builders.event_builder import EventBuilder

TZ = ZoneInfo("Europe/Berlin")
CONFIG = TrafficStatisticsConfig(
    timezone="Europe/Berlin", class_groups={"LV": frozenset({"car"})}
)


def local(day: int, hour: int, minute: int) -> datetime:
    return datetime(2026, 10, day, hour, minute, tzinfo=TZ)


def assignment(road_user: str, when: datetime) -> RoadUserAssignment:
    start = EventBuilder(
        road_user_id=road_user, section_id="s1", interpolated_occurrence=when
    ).build_section_event()
    end = EventBuilder(
        road_user_id=road_user,
        section_id="s2",
        interpolated_occurrence=when + timedelta(seconds=10),
    ).build_section_event()
    flow = Flow(FlowId("f1"), "flow", SectionId("s1"), SectionId("s2"), 100.0)
    return RoadUserAssignment(road_user, "car", flow, EventPair(start, end))


def create_exporter(
    assignments: list[RoadUserAssignment],
    max_open_days: int = 2,
    flows: list[Flow] | None = None,
) -> JsonTrafficStatisticsExporter:
    get_assignments = MagicMock()
    get_assignments.get_as_list.side_effect = lambda: list(assignments)
    flow = Flow(FlowId("f1"), "flow", SectionId("s1"), SectionId("s2"), 100.0)
    get_flows = MagicMock()
    get_flows.get.return_value = flows if flows is not None else [flow]
    sections = []
    for section_id, name in (("s1", "Nord"), ("s2", "Süd")):
        section = MagicMock()
        section.id = SectionId(section_id)
        section.name = name
        sections.append(section)
    return JsonTrafficStatisticsExporter(
        get_assignments, get_flows, MagicMock(return_value=sections), max_open_days
    )


def spec(
    tmp_path: Path, start: datetime, end: datetime
) -> TrafficStatisticsExportSpecification:
    return spec_with_ranges(tmp_path, [(start, end)])


def spec_with_ranges(
    tmp_path: Path, covered_ranges: list[tuple[datetime, datetime]]
) -> TrafficStatisticsExportSpecification:
    return TrafficStatisticsExportSpecification(
        export_directory=tmp_path,
        export_filename_stem="out",
        config=CONFIG,
        counting_event=CountingEvent.START,
        covered_ranges=covered_ranges,
        export_mode=MERGE,
    )


def day_file(tmp_path: Path, day: int) -> Path:
    return tmp_path / f"out.traffic_statistics_2026-10-{day:02d}.json"


def lv_total(path: Path) -> int:
    data = parse_json(path)
    return data[STATISTICS_KEY][TOTAL_KEY][TOTALS_KEY]["LV"]


def test_export_writes_one_file_per_touched_day(tmp_path: Path) -> None:
    exporter = create_exporter(
        [assignment("r1", local(26, 23, 58)), assignment("r2", local(27, 0, 1))]
    )

    paths = exporter.export(spec(tmp_path, local(26, 23, 58), local(27, 0, 2)))

    assert paths == [day_file(tmp_path, 26), day_file(tmp_path, 27)]
    assert lv_total(paths[0]) == 1
    assert lv_total(paths[1]) == 1
    flows = parse_json(paths[0])[FLOWS_KEY]
    assert flows[0][INDEX_KEY] == 1
    assert flows[0][START_SECTION_KEY] == {ID_KEY: "s1", NAME_KEY: "Nord"}


def test_second_chunk_accumulates_into_same_day_file(tmp_path: Path) -> None:
    assignments = [assignment("r1", local(27, 10, 0))]
    exporter = create_exporter(assignments)
    exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))
    assignments.append(assignment("r2", local(27, 10, 6)))

    paths = exporter.export(spec(tmp_path, local(27, 10, 5), local(27, 10, 10)))

    assert paths == [day_file(tmp_path, 27)]
    assert lv_total(paths[0]) == 2
    stats = read(paths[0], CONFIG)
    assert stats.as_of == local(27, 10, 10)
    assert stats.coverage == [(local(27, 10, 0), local(27, 10, 10))]


def test_existing_day_file_is_resumed_without_double_counting(
    tmp_path: Path,
) -> None:
    flow = FlowInfo("f1", "flow", 1, "s1", "Nord", "s2", "Süd")
    existing = DayTrafficStatistics(
        local(27, 0, 0).date(), CONFIG, [flow], CountingEvent.START
    )
    existing.add("r1", "f1", "LV", local(27, 10, 0), None)
    write(existing, day_file(tmp_path, 27))
    exporter = create_exporter(
        [assignment("r1", local(27, 10, 0)), assignment("r2", local(27, 10, 1))]
    )

    paths = exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))

    assert lv_total(paths[0]) == 2


def test_corrupt_existing_file_raises_and_is_not_overwritten(tmp_path: Path) -> None:
    path = day_file(tmp_path, 27)
    path.write_text("{not json", encoding="utf-8")
    os.utime(path, (1_000_000, 1_000_000))
    exporter = create_exporter([assignment("r1", local(27, 10, 0))])

    with pytest.raises(TrafficStatisticsFormatError):
        exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))

    assert path.read_text(encoding="utf-8") == "{not json"
    assert path.stat().st_mtime == 1_000_000


def test_resumed_file_with_other_counting_event_raises(tmp_path: Path) -> None:
    flow = FlowInfo("f1", "flow", 1, "s1", "Nord", "s2", "Süd")
    existing = DayTrafficStatistics(
        local(27, 0, 0).date(), CONFIG, [flow], CountingEvent.END
    )
    write(existing, day_file(tmp_path, 27))
    before = day_file(tmp_path, 27).read_text(encoding="utf-8")
    exporter = create_exporter([assignment("r1", local(27, 10, 0))])

    with pytest.raises(TrafficStatisticsFormatError):
        exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))

    assert day_file(tmp_path, 27).read_text(encoding="utf-8") == before


def test_only_two_days_are_kept_open(tmp_path: Path) -> None:
    exporter = create_exporter([])
    for day in (25, 26, 27):
        exporter.export(spec(tmp_path, local(day, 10, 0), local(day, 10, 5)))

    assert sorted(d.day for d in exporter._days) == [26, 27]


def test_assignments_of_evicted_days_are_dropped_with_one_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    assignments: list[RoadUserAssignment] = []
    exporter = create_exporter(assignments)
    for day in (25, 26, 27):
        exporter.export(spec(tmp_path, local(day, 10, 0), local(day, 10, 5)))
    assignments.extend(
        [
            assignment("r1", local(25, 11, 0)),
            assignment("r2", local(25, 12, 0)),
            assignment("r3", local(27, 11, 0)),
        ]
    )

    with caplog.at_level(logging.WARNING):
        paths = exporter.export(spec(tmp_path, local(27, 11, 0), local(27, 11, 5)))

    assert paths == [day_file(tmp_path, 27)]
    assert lv_total(paths[0]) == 1
    warnings = [r for r in caplog.records if "Dropped" in r.getMessage()]
    assert len(warnings) == 1
    assert "2" in warnings[0].getMessage()


def other_flow_assignment(road_user: str, when: datetime) -> RoadUserAssignment:
    base = assignment(road_user, when)
    flow = Flow(FlowId("f2"), "flow2", SectionId("s2"), SectionId("s1"), 100.0)
    return RoadUserAssignment(road_user, "car", flow, base.events)


def flow_ids(path: Path) -> list[str]:
    data = parse_json(path)
    return [flow[ID_KEY] for flow in data[FLOWS_KEY]]


def test_flow_added_between_chunks_is_counted(tmp_path: Path) -> None:
    assignments = [assignment("r1", local(27, 10, 0))]
    flows = [Flow(FlowId("f1"), "flow", SectionId("s1"), SectionId("s2"), 100.0)]
    exporter = create_exporter(assignments, flows=flows)
    exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))
    flows.append(Flow(FlowId("f2"), "flow2", SectionId("s2"), SectionId("s1"), 1.0))
    assignments.append(other_flow_assignment("r2", local(27, 10, 6)))

    paths = exporter.export(spec(tmp_path, local(27, 10, 5), local(27, 10, 10)))

    assert flow_ids(paths[0]) == ["f1", "f2"]
    assert lv_total(paths[0]) == 2


def test_resumed_file_is_reconciled_with_current_flows(tmp_path: Path) -> None:
    old = FlowInfo("f1", "old", 1, "s1", "Nord", "s2", "Süd")
    gone = FlowInfo("f0", "gone", 2, "s1", "Nord", "s2", "Süd")
    existing = DayTrafficStatistics(
        local(27, 0, 0).date(), CONFIG, [old, gone], CountingEvent.START
    )
    existing.add("r0", "f0", "LV", local(27, 9, 0), None)
    write(existing, day_file(tmp_path, 27))
    flows = [
        Flow(FlowId("f2"), "flow2", SectionId("s2"), SectionId("s1"), 1.0),
        Flow(FlowId("f1"), "flow", SectionId("s1"), SectionId("s2"), 100.0),
    ]
    exporter = create_exporter(
        [other_flow_assignment("r2", local(27, 10, 0))], flows=flows
    )

    paths = exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))

    assert flow_ids(paths[0]) == ["f2", "f1", "f0"]
    assert lv_total(paths[0]) == 2
    assert read(paths[0], CONFIG).flows[1].name == "flow"


def test_as_of_is_not_pushed_beyond_the_day(tmp_path: Path) -> None:
    exporter = create_exporter([assignment("r1", local(26, 23, 58))])

    paths = exporter.export(spec(tmp_path, local(26, 23, 58), local(27, 0, 2)))

    assert read(paths[0], CONFIG).as_of == local(27, 0, 0)
    assert read(paths[1], CONFIG).as_of == local(27, 0, 2)


def lv_counts(path: Path) -> list[int | None]:
    data = parse_json(path)
    return data[STATISTICS_KEY][TOTAL_KEY][COUNTS_KEY]["LV"]


def test_gap_between_covered_ranges_stays_uncovered(tmp_path: Path) -> None:
    exporter = create_exporter([assignment("r1", local(27, 10, 2))])

    paths = exporter.export(
        spec_with_ranges(
            tmp_path,
            [
                (local(27, 10, 0), local(27, 10, 5)),
                (local(27, 10, 10), local(27, 10, 15)),
            ],
        )
    )

    counts = lv_counts(paths[0])
    minute = 10 * 60
    assert counts[minute + 2] == 1
    assert counts[minute + 4] == 0
    assert counts[minute + 5 : minute + 10] == [None] * 5
    assert counts[minute + 10] == 0
    assert read(paths[0], CONFIG).coverage == [
        (local(27, 10, 0), local(27, 10, 5)),
        (local(27, 10, 10), local(27, 10, 15)),
    ]
    assert read(paths[0], CONFIG).as_of == local(27, 10, 15)


def test_gap_between_chunks_stays_uncovered(tmp_path: Path) -> None:
    exporter = create_exporter([])
    exporter.export(spec(tmp_path, local(27, 10, 0), local(27, 10, 5)))

    paths = exporter.export(spec(tmp_path, local(27, 10, 10), local(27, 10, 15)))

    counts = lv_counts(paths[0])
    assert counts[10 * 60 + 4] == 0
    assert counts[10 * 60 + 7] is None
    assert counts[10 * 60 + 12] == 0
    assert read(paths[0], CONFIG).coverage == [
        (local(27, 10, 0), local(27, 10, 5)),
        (local(27, 10, 10), local(27, 10, 15)),
    ]


def test_range_on_other_day_does_not_cover_untouched_day(tmp_path: Path) -> None:
    exporter = create_exporter([])

    paths = exporter.export(
        spec_with_ranges(
            tmp_path,
            [
                (local(26, 23, 0), local(26, 23, 30)),
                (local(27, 1, 0), local(27, 1, 30)),
            ],
        )
    )

    assert paths == [day_file(tmp_path, 26), day_file(tmp_path, 27)]
    assert read(paths[0], CONFIG).coverage == [(local(26, 23, 0), local(26, 23, 30))]
    assert read(paths[1], CONFIG).coverage == [(local(27, 1, 0), local(27, 1, 30))]
