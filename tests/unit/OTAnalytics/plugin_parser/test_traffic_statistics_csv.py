import csv
from datetime import date, datetime, timezone
from pathlib import Path

from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    AssignmentRecord,
    DayTrafficStatistics,
    FlowInfo,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from OTAnalytics.plugin_parser.traffic_statistics_csv import write_speeds

DAY = date(2026, 10, 27)
CONFIG = TrafficStatisticsConfig(
    interval_minutes=15,
    class_groups={"LV": frozenset({"car"}), "SV": frozenset({"truck"})},
)
FLOW_1 = FlowInfo("f1", "Nord --> Süd", 1, "s1", "Nord", "s2", "Süd")
FLOW_2 = FlowInfo("f2", "Süd --> Nord", 2, "s2", "Süd", "s1", "Nord")
TIME_COLUMNS = [
    "start time",
    "start occurrence date",
    "start occurrence time",
    "end time",
    "end occurrence date",
    "end occurrence time",
]
SPEED_COLUMNS = ["speed count", "avg speed", "v85"]


def utc(hour: int, minute: int) -> datetime:
    return datetime(2026, 10, 27, hour, minute, tzinfo=timezone.utc)


def record(
    road_user: str, flow_id: str, classification: str, when: datetime, mps: float
) -> AssignmentRecord:
    return AssignmentRecord(road_user, flow_id, classification, when, when, mps)


def create_statistics() -> DayTrafficStatistics:
    """Day covered from 07:00 to 07:30 with speeds in 07:00 to 07:15 only."""
    stats = DayTrafficStatistics(DAY, CONFIG, [FLOW_1, FLOW_2])
    stats.mark_covered(utc(7, 0), utc(7, 30))
    stats.add(record("ru1", "f1", "car", utc(7, 1), 10.0))
    stats.add(record("ru2", "f2", "car", utc(7, 2), 15.0))
    stats.add(record("ru3", "f2", "truck", utc(7, 3), 5.0))
    return stats


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader.fieldnames or []), list(reader)


def speed_file(tmp_path: Path, name: str) -> Path:
    return tmp_path / f"out.traffic_statistics_2026-10-27.{name}_15min.csv"


def first_interval(row: dict[str, str]) -> bool:
    return row["start time"] == "2026-10-27 07:00:00"


class TestWriteSpeeds:
    def test_writes_three_files(self, tmp_path: Path) -> None:
        paths = write_speeds(create_statistics(), tmp_path, "out")

        assert paths == [
            speed_file(tmp_path, "speeds"),
            speed_file(tmp_path, "speeds_all_flows"),
            speed_file(tmp_path, "speeds_total"),
        ]

    def test_speeds_per_flow_have_counts_columns(self, tmp_path: Path) -> None:
        write_speeds(create_statistics(), tmp_path, "out")

        columns, rows = read_rows(speed_file(tmp_path, "speeds"))

        assert columns == [
            *TIME_COLUMNS,
            "classification",
            "flow",
            "from section",
            "to section",
            *SPEED_COLUMNS,
        ]
        assert {
            "classification": "LV",
            "flow": "Süd --> Nord",
            "from section": "Süd",
            "to section": "Nord",
            "start time": "2026-10-27 07:00:00",
            "start occurrence date": "2026-10-27",
            "start occurrence time": "07:00:00",
            "end time": "2026-10-27 07:15:00",
            "end occurrence date": "2026-10-27",
            "end occurrence time": "07:15:00",
            "speed count": "1",
            "avg speed": "54.0",
            "v85": "54.0",
        } in rows
        # 2 flows x 2 groups x 2 covered intervals
        assert len(rows) == 8

    def test_covered_interval_without_speeds_has_empty_values(
        self, tmp_path: Path
    ) -> None:
        write_speeds(create_statistics(), tmp_path, "out")

        _, rows = read_rows(speed_file(tmp_path, "speeds"))

        later = [row for row in rows if row["start time"] == "2026-10-27 07:15:00"]
        assert {(r["speed count"], r["avg speed"], r["v85"]) for r in later} == {
            ("0", "", "")
        }

    def test_uncovered_interval_without_speeds_has_no_rows(
        self, tmp_path: Path
    ) -> None:
        write_speeds(create_statistics(), tmp_path, "out")

        for name in ("speeds", "speeds_all_flows", "speeds_total"):
            _, rows = read_rows(speed_file(tmp_path, name))
            assert {row["start time"] for row in rows} == {
                "2026-10-27 07:00:00",
                "2026-10-27 07:15:00",
            }

    def test_speeds_all_flows_merge_flows_per_group(self, tmp_path: Path) -> None:
        write_speeds(create_statistics(), tmp_path, "out")

        columns, rows = read_rows(speed_file(tmp_path, "speeds_all_flows"))

        assert columns == [*TIME_COLUMNS, "classification", *SPEED_COLUMNS]
        values = {
            row["classification"]: (row["speed count"], row["avg speed"], row["v85"])
            for row in rows
            if first_interval(row)
        }
        assert values == {"LV": ("2", "45.0", "54.0"), "SV": ("1", "18.0", "18.0")}

    def test_speeds_total_merge_flows_and_groups(self, tmp_path: Path) -> None:
        write_speeds(create_statistics(), tmp_path, "out")

        columns, rows = read_rows(speed_file(tmp_path, "speeds_total"))

        assert columns == [*TIME_COLUMNS, "classification", *SPEED_COLUMNS]
        first = [row for row in rows if first_interval(row)]
        assert [
            (r["classification"], r["speed count"], r["avg speed"], r["v85"])
            for r in first
        ] == [("total", "3", "36.0", "54.0")]

    def test_nothing_is_written_without_coverage_and_speeds(
        self, tmp_path: Path
    ) -> None:
        stats = DayTrafficStatistics(DAY, CONFIG, [FLOW_1])

        assert write_speeds(stats, tmp_path, "out") == []
        assert list(tmp_path.iterdir()) == []
