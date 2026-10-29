import logging
from dataclasses import replace
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    TOTAL,
    ClassGroupResolver,
    DayTrafficStatistics,
    FlowInfo,
    PeakHour,
    assignment_to_entry,
    day_start,
    minutes_in_day,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_values import SpeedValues
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from tests.utils.builders.road_user_assignment import create_assignment

TZ = ZoneInfo("Europe/Berlin")
DAY = date(2026, 10, 27)
MINUTES_PER_DAY = 24 * 60
SPEED_PROFILE_SLOTS = MINUTES_PER_DAY // 15


class TestDayHelpers:
    def test_day_start_is_local_midnight(self) -> None:
        assert day_start(DAY, TZ).isoformat() == "2026-10-27T00:00:00+01:00"

    def test_regular_day_has_1440_minutes(self) -> None:
        assert minutes_in_day(DAY, TZ) == MINUTES_PER_DAY

    def test_dst_spring_forward_day_has_1380_minutes(self) -> None:
        assert minutes_in_day(date(2026, 3, 29), TZ) == 1380

    def test_dst_fall_back_day_has_1500_minutes(self) -> None:
        assert minutes_in_day(date(2026, 10, 25), TZ) == 1500


class TestClassGroupResolver:
    def test_without_groups_classification_is_group(self) -> None:
        resolver = ClassGroupResolver(TrafficStatisticsConfig())
        assert resolver.group_of("car") == "car"

    def test_maps_classification_to_group(self) -> None:
        config = TrafficStatisticsConfig(
            class_groups={"LV": frozenset({"car", "van"}), "SV": frozenset({"truck"})}
        )
        resolver = ClassGroupResolver(config)
        assert resolver.group_of("van") == "LV"
        assert resolver.group_of("truck") == "SV"

    def test_unknown_classification_is_ignored_and_warned_once(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        config = TrafficStatisticsConfig(class_groups={"LV": frozenset({"car"})})
        resolver = ClassGroupResolver(config)
        with caplog.at_level(logging.WARNING):
            assert resolver.group_of("bike") is None
            assert resolver.group_of("bike") is None
        assert len([r for r in caplog.records if "bike" in r.getMessage()]) == 1


FLOW_1 = FlowInfo("f1", "Flow 1", 0, "s1", "Section 1", "s2", "Section 2")
FLOW_2 = FlowInfo("f2", "Flow 2", 1, "s1", "Section 1", "s3", "Section 3")


def local(hour: int, minute: int, second: int = 0, day: date = DAY) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=TZ)


def interval_index(hour: int, minute: int, interval_minutes: int = 1) -> int:
    """Index of the interval containing the local time on DAY (no DST change)."""
    return (hour * 60 + minute) // interval_minutes


def create_statistics(
    config: TrafficStatisticsConfig | None = None, covered: bool = True
) -> DayTrafficStatistics:
    config = config or TrafficStatisticsConfig(timezone="Europe/Berlin")
    stats = DayTrafficStatistics(DAY, config, [FLOW_1, FLOW_2])
    if covered:
        stats.mark_covered(day_start(DAY, TZ), day_start(date(2026, 10, 28), TZ))
    return stats


class TestDayTrafficStatistics:
    def test_record_counts_into_its_minute_bin(self) -> None:
        stats = create_statistics()
        assert stats.add("ru1", "f1", "LV", local(7, 15, 30), None)
        counts = stats.counts("f1")["LV"]
        assert len(counts) == MINUTES_PER_DAY
        assert counts[interval_index(7, 15)] == 1
        assert counts[interval_index(7, 14)] == 0

    def test_uncovered_minute_without_counts_is_none(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(local(7, 0), local(8, 0))
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        counts = stats.counts("f1")["LV"]
        assert counts[interval_index(7, 14)] == 0
        assert counts[interval_index(7, 15)] == 1
        assert counts[interval_index(0, 0)] is None
        assert counts[interval_index(8, 0)] is None

    def test_uncovered_minute_with_count_is_int(self) -> None:
        stats = create_statistics(covered=False)
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        assert stats.counts("f1")["LV"][interval_index(7, 15)] == 1

    def test_interval_overlapping_coverage_is_covered(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(timezone="Europe/Berlin", interval_minutes=5),
            covered=False,
        )
        stats.add("ru0", "f1", "LV", local(0, 0), None)
        stats.mark_covered(local(7, 3), local(7, 4))
        counts = stats.counts("f1")["LV"]
        covered = interval_index(7, 3, interval_minutes=5)
        assert counts[covered] == 0
        assert counts[covered + 1] is None

    def test_duplicate_road_user_is_counted_once(self) -> None:
        stats = create_statistics()
        assert stats.add("ru1", "f1", "LV", local(7, 15), None)
        assert not stats.add("ru1", "f2", "LV", local(7, 16), None)
        assert stats.totals(TOTAL) == {"LV": 1}
        assert stats.road_user_ids == {"ru1"}

    def test_total_sums_flows(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        stats.add("ru2", "f2", "LV", local(7, 15), None)
        assert stats.counts(TOTAL)["LV"][interval_index(7, 15)] == 2
        assert stats.totals("f1") == {"LV": 1}

    def test_total_is_none_where_no_flow_has_coverage(self) -> None:
        stats = create_statistics(covered=False)
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        assert stats.counts(TOTAL)["LV"][interval_index(0, 0)] is None

    def test_record_of_other_day_is_rejected(self) -> None:
        stats = create_statistics()
        assert not stats.add(
            "ru1", "f1", "LV", local(7, 15, day=date(2026, 10, 28)), None
        )
        assert stats.road_user_ids == set()

    def test_unknown_flow_is_rejected(self) -> None:
        stats = create_statistics()
        assert not stats.add("ru1", "unknown", "LV", local(7, 15), None)

    def test_naive_occurrence_is_treated_as_utc(self) -> None:
        stats = create_statistics()
        # 06:15 UTC is 07:15 local time
        assert stats.add("ru1", "f1", "LV", datetime(2026, 10, 27, 6, 15), None)
        assert stats.counts("f1")["LV"][interval_index(7, 15)] == 1

    def test_dst_spring_forward_day_has_1380_bins(self) -> None:
        day = date(2026, 3, 29)
        stats = DayTrafficStatistics(
            day, TrafficStatisticsConfig(timezone="Europe/Berlin"), [FLOW_1]
        )
        stats.mark_covered(day_start(day, TZ), day_start(date(2026, 3, 30), TZ))
        # 04:00 local is 180 real minutes after midnight, the hour 02:00 is skipped
        assert stats.add("ru1", "f1", "LV", local(4, 0, day=day), None)
        counts = stats.counts("f1")["LV"]
        assert len(counts) == 1380
        assert counts[180] == 1

    def test_dst_fall_back_day_has_1500_bins(self) -> None:
        day = date(2026, 10, 25)
        stats = DayTrafficStatistics(
            day, TrafficStatisticsConfig(timezone="Europe/Berlin"), [FLOW_1]
        )
        # midnight local is 22:00Z, so 01:30Z is 210 real minutes into the day
        occurrence = datetime(2026, 10, 25, 1, 30, tzinfo=timezone.utc)
        assert stats.add("ru1", "f1", "LV", occurrence, None)
        counts = stats.counts("f1")["LV"]
        assert len(counts) == 1500
        assert counts[210] == 1

    def test_five_minute_interval_has_288_bins(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(timezone="Europe/Berlin", interval_minutes=5)
        )
        stats.add("ru1", "f1", "LV", local(7, 17), None)
        counts = stats.counts("f1")["LV"]
        assert len(counts) == MINUTES_PER_DAY // 5
        assert counts[interval_index(7, 17, interval_minutes=5)] == 1

    def test_mark_covered_merges_and_clips(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(local(7, 0), local(8, 0))
        stats.mark_covered(local(7, 30), local(9, 0))
        stats.mark_covered(local(9, 0), local(9, 30))
        stats.mark_covered(local(23, 0, day=date(2026, 10, 26)), local(0, 30))
        assert stats.coverage == [
            (local(0, 0), local(0, 30)),
            (local(7, 0), local(9, 30)),
        ]

    def test_only_plausible_speeds_enter_speed_profile(self) -> None:
        config = TrafficStatisticsConfig(
            timezone="Europe/Berlin",
            speed_profile_interval_minutes=15,
            max_speed_kmh=100,
        )
        stats = create_statistics(config)
        stats.add("ru1", "f1", "LV", local(7, 20), 50.5)
        stats.add("ru2", "f1", "LV", local(7, 21), 150.0)
        stats.add("ru3", "f1", "LV", local(7, 22), None)
        stats.add("ru4", "f1", "LV", local(7, 23), 0.0)
        slot = interval_index(7, 20, interval_minutes=15)
        assert stats.speed_profile("f1")["LV"][slot] == SpeedValues(50.5, 50.5, 1)
        assert stats.totals("f1") == {"LV": 4}

    def test_counting_event_defaults_to_start(self) -> None:
        assert create_statistics().counting_event == CountingEvent.START


class TestPeakHour:
    def test_peak_hour_finds_strongest_quarter_aligned_window(self) -> None:
        stats = create_statistics()
        for index, (hour, minute) in enumerate([(6, 0), (7, 20), (7, 50), (8, 10)]):
            stats.add(f"ru{index}", "f1", "LV", local(hour, minute), None)
        assert stats.peak_hour("f1") == {
            "LV": PeakHour(start=local(7, 15), end=local(8, 15), count=3)
        }

    def test_peak_hour_tie_returns_earliest(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(6, 30), None)
        stats.add("ru2", "f1", "LV", local(9, 30), None)
        assert stats.peak_hour("f1") == {
            "LV": PeakHour(start=local(5, 45), end=local(6, 45), count=1)
        }

    def test_peak_hour_total_sums_flows(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 0), None)
        stats.add("ru2", "f2", "LV", local(7, 10), None)
        assert stats.peak_hour(TOTAL)["LV"].count == 2

    def test_peak_hour_ignores_uncovered_windows(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(local(7, 0), local(9, 0))
        stats.add("ru1", "f1", "LV", local(7, 30), None)
        assert stats.peak_hour("f1")["LV"].start == local(6, 45)

    def test_peak_hour_without_data_is_absent(self) -> None:
        stats = create_statistics()
        assert stats.peak_hour("f1") == {}

    def test_peak_hour_windows_lie_completely_in_the_day(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(23, 50), None)
        assert stats.peak_hour("f1")["LV"] == PeakHour(
            start=local(23, 0), end=datetime(2026, 10, 28, 0, 0, tzinfo=TZ), count=1
        )

    def test_peak_hour_on_dst_day_uses_elapsed_time(self) -> None:
        day = date(2026, 10, 25)
        stats = DayTrafficStatistics(
            day, TrafficStatisticsConfig(timezone="Europe/Berlin"), [FLOW_1]
        )
        stats.mark_covered(day_start(day, TZ), day_start(date(2026, 10, 26), TZ))
        stats.add("ru1", "f1", "LV", datetime(2026, 10, 25, 4, 0, tzinfo=TZ), None)
        peak = stats.peak_hour("f1")["LV"]
        # window starts at elapsed minute 255 (03:15 CET)
        assert peak.start.isoformat() == "2026-10-25T03:15:00+01:00"
        assert peak.end.isoformat() == "2026-10-25T04:15:00+01:00"


class TestSpeed:
    def test_total_speed_merges_flows(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 0), 30.0)
        stats.add("ru2", "f2", "LV", local(7, 5), 50.0)
        assert stats.speed(TOTAL) == {"LV": SpeedValues(40.0, 50.0, 2)}
        assert stats.speed("f1") == {"LV": SpeedValues(30.0, 30.0, 1)}

    def test_implausible_speed_is_counted_but_not_in_speed(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 0), 250.0)
        assert stats.totals("f1") == {"LV": 1}
        assert stats.speed("f1") == {}

    def test_speed_merges_all_slots(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 0), 30.0)
        stats.add("ru2", "f1", "LV", local(18, 0), 50.0)
        assert stats.speed("f1")["LV"].count == 2

    def test_speed_profile_has_value_only_in_occupied_slot(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 20), 36.0)
        profile = stats.speed_profile("f1")["LV"]
        slot = interval_index(7, 20, interval_minutes=15)
        assert len(profile) == SPEED_PROFILE_SLOTS
        assert profile[slot] == SpeedValues(36.0, 36.0, 1)
        assert [v for i, v in enumerate(profile) if i != slot and v is not None] == []

    def test_speed_profile_contains_counted_group_without_speed(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 20), None)
        assert stats.speed_profile("f1") == {"LV": [None] * SPEED_PROFILE_SLOTS}

    def test_speed_profile_contains_configured_groups_without_data(self) -> None:
        config = TrafficStatisticsConfig(
            timezone="Europe/Berlin",
            class_groups={"LV": frozenset({"car"}), "HV": frozenset({"truck"})},
        )
        stats = create_statistics(config)
        stats.add("ru1", "f1", "LV", local(7, 20), 36.0)
        profile = stats.speed_profile("f1")
        assert set(profile) == {"LV", "HV"}
        assert profile["HV"] == [None] * SPEED_PROFILE_SLOTS
        slot = interval_index(7, 20, interval_minutes=15)
        assert profile["LV"][slot] == SpeedValues(36.0, 36.0, 1)

    def test_total_speed_profile_merges_per_slot(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 20), 30.0)
        stats.add("ru2", "f2", "LV", local(7, 25), 50.0)
        slot = interval_index(7, 20, interval_minutes=15)
        assert stats.speed_profile(TOTAL)["LV"][slot] == SpeedValues(40.0, 50.0, 2)


class TestAssignmentToEntry:
    def test_start_event_entry_in_local_time(self) -> None:
        assignment = create_assignment(distance=100, start_s=0, end_s=10)
        resolver = ClassGroupResolver(TrafficStatisticsConfig())
        entry = assignment_to_entry(assignment, CountingEvent.START, resolver, TZ)
        assert entry is not None
        road_user, flow_id, group, occurrence, speed = entry
        assert (road_user, flow_id, group) == ("1", "flow", "car")
        assert occurrence == datetime(2020, 1, 1, tzinfo=timezone.utc)
        assert occurrence.utcoffset() == TZ.utcoffset(occurrence)
        assert occurrence.hour == 1
        assert speed == pytest.approx(36.0)

    def test_end_counting_event_uses_end_occurrence(self) -> None:
        assignment = create_assignment(distance=100, start_s=0, end_s=10)
        resolver = ClassGroupResolver(TrafficStatisticsConfig())
        entry = assignment_to_entry(assignment, CountingEvent.END, resolver, TZ)
        assert entry is not None
        assert entry[3] == datetime(2020, 1, 1, 0, 0, 10, tzinfo=timezone.utc)

    def test_missing_distance_gives_no_speed(self) -> None:
        assignment = create_assignment(distance=None, start_s=0, end_s=10)
        resolver = ClassGroupResolver(TrafficStatisticsConfig())
        entry = assignment_to_entry(assignment, CountingEvent.START, resolver, TZ)
        assert entry is not None
        assert entry[4] is None

    def test_unknown_group_gives_none(self) -> None:
        assignment = create_assignment(distance=100, start_s=0, end_s=10)
        config = TrafficStatisticsConfig(class_groups={"SV": frozenset({"truck"})})
        entry = assignment_to_entry(
            assignment, CountingEvent.START, ClassGroupResolver(config), TZ
        )
        assert entry is None

    def test_naive_occurrence_is_treated_as_utc(self) -> None:
        assignment = create_assignment(distance=100, start_s=0, end_s=10)
        naive_start = replace(
            assignment.events.start,
            interpolated_occurrence=datetime(2020, 1, 1, 12, 0),
        )
        naive_end = replace(
            assignment.events.end,
            interpolated_occurrence=datetime(2020, 1, 1, 12, 0, 10),
        )
        naive = replace(
            assignment,
            events=replace(assignment.events, start=naive_start, end=naive_end),
        )
        resolver = ClassGroupResolver(TrafficStatisticsConfig())
        entry = assignment_to_entry(naive, CountingEvent.START, resolver, TZ)
        assert entry is not None
        assert entry[3].hour == 13
        assert entry[3] == datetime(2020, 1, 1, 12, tzinfo=timezone.utc)
