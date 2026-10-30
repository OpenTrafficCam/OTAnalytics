import os
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    AssignmentRecord,
    DayTrafficStatistics,
    FlowInfo,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from OTAnalytics.plugin_parser.json_parser import parse_json, write_json
from OTAnalytics.plugin_parser.traffic_statistics_json import (
    COUNT_KEY,
    COUNTS_KEY,
    COVERAGE_KEY,
    FLOWS_KEY,
    FORMAT,
    FORMAT_KEY,
    PEAK_HOUR_KEY,
    SPEED_KEY,
    STATISTICS_KEY,
    TOTAL_KEY,
    TOTALS_KEY,
    VERSION,
    VERSION_KEY,
    DayProgress,
    TrafficStatisticsFormatError,
    read_progress,
    to_dict,
    write,
)

TZ = ZoneInfo("Europe/Berlin")
DAY = date(2026, 10, 27)
CONFIG = TrafficStatisticsConfig(
    timezone="Europe/Berlin",
    class_groups={"LV": frozenset({"car", "van"}), "SV": frozenset({"truck"})},
)
FLOW_1 = FlowInfo("f1", "Nord → Süd", 1, "s1", "Nord", "s2", "Süd")
FLOW_2 = FlowInfo("f2", "Süd → Nord", 2, "s2", "Süd", "s1", "Nord")


def local(hour: int, minute: int) -> datetime:
    return datetime(2026, 10, 27, hour, minute, tzinfo=TZ)


def record(
    road_user: str,
    flow_id: str,
    road_user_type: str,
    occurrence: datetime,
    speed_mps: float | None,
) -> AssignmentRecord:
    return AssignmentRecord(
        road_user, flow_id, road_user_type, occurrence, occurrence, speed_mps
    )


def create_statistics() -> DayTrafficStatistics:
    stats = DayTrafficStatistics(DAY, CONFIG, [FLOW_1, FLOW_2], CountingEvent.END)
    stats.mark_covered(local(0, 0), local(14, 32))
    stats.add(record("ru1", "f1", "car", local(7, 20), 11.5))
    stats.add(record("ru2", "f1", "van", local(7, 21), 14.0))
    stats.add(record("ru3", "f2", "car", local(8, 0), None))
    stats.add(record("ru4", "f2", "truck", local(9, 5), 8.4))
    stats.as_of = local(14, 32)
    return stats


class TestReadProgress:
    def test_returns_coverage_and_as_of(self, tmp_path: Path) -> None:
        stats = create_statistics()
        path = tmp_path / "day.json"
        write(stats, path)

        assert read_progress(path) == DayProgress(stats.coverage, stats.as_of)

    def test_no_as_of_and_no_coverage(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        write(DayTrafficStatistics(DAY, CONFIG, [FLOW_1]), path)

        assert read_progress(path) == DayProgress([], None)

    @pytest.mark.parametrize("content", ["{not json", "[1, 2]"])
    def test_corrupt_file_raises_format_error(
        self, tmp_path: Path, content: str
    ) -> None:
        path = tmp_path / "day.json"
        path.write_text(content, encoding="utf-8")

        with pytest.raises(TrafficStatisticsFormatError):
            read_progress(path)

    @pytest.mark.parametrize(
        "key, value",
        [(FORMAT_KEY, "other"), (VERSION_KEY, VERSION + 1), (COVERAGE_KEY, None)],
    )
    def test_invalid_header_raises_format_error(
        self, tmp_path: Path, key: str, value: Any
    ) -> None:
        path = tmp_path / "day.json"
        write(create_statistics(), path)
        data = parse_json(path)
        if value is None:
            del data[key]
        else:
            data[key] = value
        write_json(data, path)

        with pytest.raises(TrafficStatisticsFormatError):
            read_progress(path)


class TestFormat:
    def test_written_file_matches_documented_keys(self, tmp_path: Path) -> None:
        # Literal keys on purpose: this test pins the file format for consumers,
        # so changing the value of a key constant must fail here.
        path = tmp_path / "day.json"
        write(create_statistics(), path)

        data = parse_json(path)

        assert set(data) == {
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
        }
        assert data["format"] == FORMAT
        assert data["version"] == VERSION
        assert data["day"] == "2026-10-27"
        assert data["counting_event"] == "end"
        assert data["class_groups"] == {"LV": ["car", "van"], "SV": ["truck"]}
        assert data["as_of"] == "2026-10-27T14:32:00+01:00"
        assert data["coverage"] == [
            ["2026-10-27T00:00:00+01:00", "2026-10-27T14:32:00+01:00"]
        ]
        assert data["flows"][0] == {
            "id": "f1",
            "name": "Nord → Süd",
            "index": 1,
            "start_section": {"id": "s1", "name": "Nord"},
            "end_section": {"id": "s2", "name": "Süd"},
        }

    def test_statistics_block(self) -> None:
        data = to_dict(create_statistics())

        total = data[STATISTICS_KEY][TOTAL_KEY]
        assert total[TOTALS_KEY] == {"LV": 3, "SV": 1}
        assert total[COUNTS_KEY]["LV"][440] == 1
        assert total[PEAK_HOUR_KEY]["LV"][COUNT_KEY] == 3
        assert total[SPEED_KEY]["LV"][COUNT_KEY] == 2
        assert set(data[STATISTICS_KEY][FLOWS_KEY]) == {"f1", "f2"}

    def test_uncovered_counts_are_null(self) -> None:
        data = to_dict(create_statistics())

        counts = data[STATISTICS_KEY][TOTAL_KEY][COUNTS_KEY]["LV"]
        assert len(counts) == 1440
        assert counts[0] == 0
        assert counts[-1] is None


class TestWrite:
    def test_write_is_atomic_and_leaves_no_temp_files(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        path.write_text("old", encoding="utf-8")

        write(create_statistics(), path)

        assert [p.name for p in tmp_path.iterdir()] == ["day.json"]
        assert parse_json(path)[FORMAT_KEY] == FORMAT

    def test_written_file_gets_default_permissions(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        old_umask = os.umask(0o022)
        try:
            write(create_statistics(), path)
        finally:
            os.umask(old_umask)

        assert path.stat().st_mode & 0o777 == 0o644

    def test_write_syncs_temp_file_before_replace(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = tmp_path / "day.json"
        calls: list[str] = []
        original_fsync = os.fsync
        original_replace = os.replace

        def fsync(fd: int) -> None:
            calls.append("fsync")
            original_fsync(fd)

        def replace(src: Any, dst: Any) -> None:
            calls.append("replace")
            original_replace(src, dst)

        monkeypatch.setattr("os.fsync", fsync)
        monkeypatch.setattr("os.replace", replace)

        write(create_statistics(), path)

        assert calls == ["fsync", "replace"]

    def test_failed_write_keeps_old_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = tmp_path / "day.json"
        path.write_text("old", encoding="utf-8")

        def fail(*args: Any, **kwargs: Any) -> None:
            raise OSError("boom")

        monkeypatch.setattr("os.replace", fail)

        with pytest.raises(OSError):
            write(create_statistics(), path)

        assert path.read_text(encoding="utf-8") == "old"
        assert [p.name for p in tmp_path.iterdir()] == ["day.json"]
