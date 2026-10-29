import json
import os
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    TOTAL,
    DayTrafficStatistics,
    FlowInfo,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from OTAnalytics.plugin_parser.traffic_statistics_json import (
    AS_OF_KEY,
    BINS_KEY,
    CLASS_GROUPS_KEY,
    COUNT_KEY,
    COUNTS_KEY,
    COVERAGE_KEY,
    DAY_KEY,
    FLOWS_KEY,
    FORMAT,
    FORMAT_KEY,
    INTERVAL_MINUTES_KEY,
    PEAK_HOUR_KEY,
    ROAD_USER_IDS_KEY,
    SPEED_HISTOGRAMS_KEY,
    SPEED_KEY,
    SPEED_PROFILE_INTERVAL_MINUTES_KEY,
    STATE_KEY,
    STATISTICS_KEY,
    TIMEZONE_KEY,
    TOTAL_KEY,
    TOTAL_SPEED_KEY,
    TOTALS_KEY,
    VERSION,
    VERSION_KEY,
    TrafficStatisticsFormatError,
    from_dict,
    read,
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


def create_statistics() -> DayTrafficStatistics:
    stats = DayTrafficStatistics(DAY, CONFIG, [FLOW_1, FLOW_2], CountingEvent.END)
    stats.mark_covered(local(0, 0), local(14, 32))
    stats.add("ru1", "f1", "LV", local(7, 20), 41.5)
    stats.add("ru2", "f1", "LV", local(7, 21), 50.0)
    stats.add("ru3", "f2", "LV", local(8, 0), None)
    stats.add("ru4", "f2", "SV", local(9, 5), 30.2)
    stats.as_of = local(14, 32)
    return stats


class TestRoundTrip:
    def test_round_trip_preserves_derived_and_state(self, tmp_path: Path) -> None:
        stats = create_statistics()
        path = tmp_path / "day.json"

        write(stats, path)
        restored = read(path, CONFIG)

        assert restored.day == stats.day
        assert restored.counting_event == CountingEvent.END
        assert restored.as_of == stats.as_of
        assert restored.flows == stats.flows
        assert restored.coverage == stats.coverage
        assert restored.road_user_ids == stats.road_user_ids
        for flow_id in ("f1", "f2", TOTAL):
            assert restored.counts(flow_id) == stats.counts(flow_id)
            assert restored.totals(flow_id) == stats.totals(flow_id)
            assert restored.peak_hour(flow_id) == stats.peak_hour(flow_id)
            assert restored.speed(flow_id) == stats.speed(flow_id)
            assert restored.speed_profile(flow_id) == stats.speed_profile(flow_id)
        assert restored.raw_counts() == stats.raw_counts()

    def test_restored_statistics_keeps_counting(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        write(create_statistics(), path)
        restored = read(path, CONFIG)

        assert not restored.add("ru1", "f1", "LV", local(10, 0), 40.0)
        assert restored.add("ru9", "f1", "LV", local(10, 0), 40.0)

    def test_none_as_of_and_no_coverage(self) -> None:
        stats = DayTrafficStatistics(DAY, CONFIG, [FLOW_1])
        data = to_dict(stats)

        assert data[AS_OF_KEY] is None
        assert data[COVERAGE_KEY] == []
        restored = from_dict(json.loads(json.dumps(data)), CONFIG)
        assert restored.as_of is None
        assert restored.coverage == []


class TestFormat:
    def test_written_file_matches_documented_keys(self, tmp_path: Path) -> None:
        # Literal keys on purpose: this test pins the file format for consumers,
        # so changing the value of a key constant must fail here.
        path = tmp_path / "day.json"
        write(create_statistics(), path)

        data = json.loads(path.read_text(encoding="utf-8"))

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
            "state",
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
        assert "Nord → Süd" in path.read_text(encoding="utf-8")

    def test_statistics_and_state_blocks(self) -> None:
        data = to_dict(create_statistics())

        total = data[STATISTICS_KEY][TOTAL_KEY]
        assert total[TOTALS_KEY] == {"LV": 3, "SV": 1}
        assert total[COUNTS_KEY]["LV"][440] == 1
        assert total[PEAK_HOUR_KEY]["LV"][COUNT_KEY] == 3
        assert total[SPEED_KEY]["LV"][COUNT_KEY] == 2
        assert set(data[STATISTICS_KEY][FLOWS_KEY]) == {"f1", "f2"}
        assert data[STATE_KEY][ROAD_USER_IDS_KEY] == ["ru1", "ru2", "ru3", "ru4"]
        histograms = data[STATE_KEY][SPEED_HISTOGRAMS_KEY]
        slots = histograms["f1"]["LV"]
        assert slots[29] == {BINS_KEY: {"41": 1, "50": 1}, TOTAL_SPEED_KEY: 91.5}
        assert slots[0] is None
        assert "LV" not in histograms["f2"]

    def test_uncovered_counts_are_null(self) -> None:
        data = to_dict(create_statistics())

        counts = data[STATISTICS_KEY][TOTAL_KEY][COUNTS_KEY]["LV"]
        assert len(counts) == 1440
        assert counts[0] == 0
        assert counts[-1] is None


class TestErrors:
    @staticmethod
    def valid() -> dict[str, Any]:
        return json.loads(json.dumps(to_dict(create_statistics())))

    def test_interval_mismatch_raises_format_error(self) -> None:
        other = TrafficStatisticsConfig(
            timezone="Europe/Berlin",
            interval_minutes=5,
            class_groups=CONFIG.class_groups,
        )

        with pytest.raises(TrafficStatisticsFormatError):
            from_dict(self.valid(), other)

    @pytest.mark.parametrize(
        "key,value",
        [
            (FORMAT_KEY, "other"),
            (VERSION_KEY, 2),
            (TIMEZONE_KEY, "UTC"),
            (SPEED_PROFILE_INTERVAL_MINUTES_KEY, 30),
            (INTERVAL_MINUTES_KEY, 5),
        ],
    )
    def test_mismatching_header_raises(self, key: str, value: Any) -> None:
        data = self.valid()
        data[key] = value

        with pytest.raises(TrafficStatisticsFormatError):
            from_dict(data, CONFIG)

    @pytest.mark.parametrize(
        "class_groups",
        [
            {"LV": frozenset({"car"}), "SV": frozenset({"truck"})},
            {"LV": frozenset({"car", "van"}), "HV": frozenset({"truck"})},
            {"LV": frozenset({"car", "van"})},
            {},
        ],
    )
    def test_changed_class_groups_raise_format_error(
        self, class_groups: dict[str, frozenset[str]]
    ) -> None:
        other = TrafficStatisticsConfig(
            timezone="Europe/Berlin", class_groups=class_groups
        )

        with pytest.raises(TrafficStatisticsFormatError, match=CLASS_GROUPS_KEY):
            from_dict(self.valid(), other)

    def test_class_groups_are_compared_ignoring_order(self) -> None:
        data = self.valid()
        data[CLASS_GROUPS_KEY] = {"SV": ["truck"], "LV": ["van", "car"]}

        restored = from_dict(data, CONFIG)

        assert restored.config.class_groups == CONFIG.class_groups

    def test_changed_peak_settings_are_accepted(self) -> None:
        other = TrafficStatisticsConfig(
            timezone="Europe/Berlin",
            class_groups=CONFIG.class_groups,
            peak_window_minutes=30,
            peak_step_minutes=5,
        )

        restored = from_dict(self.valid(), other)

        assert restored.config == other

    @pytest.mark.parametrize(
        "key", [DAY_KEY, FLOWS_KEY, STATISTICS_KEY, STATE_KEY, COVERAGE_KEY]
    )
    def test_missing_key_raises(self, key: str) -> None:
        data = self.valid()
        del data[key]

        with pytest.raises(TrafficStatisticsFormatError):
            from_dict(data, CONFIG)

    def test_wrong_counts_length_raises(self) -> None:
        data = self.valid()
        data[STATISTICS_KEY][FLOWS_KEY]["f1"][COUNTS_KEY]["LV"].pop()

        with pytest.raises(TrafficStatisticsFormatError):
            from_dict(data, CONFIG)

    def test_wrong_histogram_length_raises(self) -> None:
        data = self.valid()
        data[STATE_KEY][SPEED_HISTOGRAMS_KEY]["f1"]["LV"].pop()

        with pytest.raises(TrafficStatisticsFormatError):
            from_dict(data, CONFIG)

    def test_restore_accepts_full_empty_histogram_slots(self) -> None:
        data = self.valid()
        slots = data[STATE_KEY][SPEED_HISTOGRAMS_KEY]["f1"]["LV"]
        slots[0] = {BINS_KEY: {}, TOTAL_SPEED_KEY: 0.0}
        expected = from_dict(deepcopy(self.valid()), CONFIG)

        restored = from_dict(data, CONFIG)

        assert restored.histograms()["f1"]["LV"][0].count == 0
        assert restored.speed("f1") == expected.speed("f1")

    def test_corrupt_json_raises_format_error(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        path.write_text("{not json", encoding="utf-8")

        with pytest.raises(TrafficStatisticsFormatError):
            read(path, CONFIG)

    def test_non_object_json_raises_format_error(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        path.write_text("[1, 2]", encoding="utf-8")

        with pytest.raises(TrafficStatisticsFormatError):
            read(path, CONFIG)


class TestWrite:
    def test_write_is_atomic_and_leaves_no_temp_files(self, tmp_path: Path) -> None:
        path = tmp_path / "day.json"
        path.write_text("old", encoding="utf-8")

        write(create_statistics(), path)

        assert [p.name for p in tmp_path.iterdir()] == ["day.json"]
        assert json.loads(path.read_text(encoding="utf-8"))[FORMAT_KEY] == FORMAT

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
