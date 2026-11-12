import logging
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import pytest

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    KMH_PER_MPS,
    MINUTES_PER_DAY,
    MINUTES_PER_HOUR,
    TOTAL,
    AssignmentRecord,
    ClassGroupResolver,
    CoverageRange,
    DayTrafficStatistics,
    FlowInfo,
    PeakHour,
    as_utc,
    day_start,
    merge_ranges,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_values import SpeedValues
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)
from tests.utils.builders.road_user_assignment import create_assignment

DAY = date(2026, 10, 27)
PREVIOUS_DAY = DAY - timedelta(days=1)
NEXT_DAY = DAY + timedelta(days=1)
FIVE_MINUTES = 5
QUARTER_HOUR_MINUTES = 15
QUARTER_HOURS = MINUTES_PER_DAY // QUARTER_HOUR_MINUTES
QUARTER_HOUR_CONFIG = TrafficStatisticsConfig(interval_minutes=QUARTER_HOUR_MINUTES)

SLOW_MPS = 10.0
FAST_MPS = 15.0
SLOW_KMH = SLOW_MPS * KMH_PER_MPS
FAST_KMH = FAST_MPS * KMH_PER_MPS
AVG_SLOW_FAST_KMH = (SLOW_KMH + FAST_KMH) / 2
STANDING_MPS = 0.0
IMPLAUSIBLE_MPS = 100.0


class TestDayHelpers:
    def test_day_start_is_utc_midnight(self) -> None:
        assert day_start(DAY).isoformat() == "2026-10-27T00:00:00+00:00"

    def test_as_utc_takes_naive_time_as_utc_without_shifting(self) -> None:
        assert as_utc(datetime(2026, 10, 27, 7, 15)) == datetime(
            2026, 10, 27, 7, 15, tzinfo=timezone.utc
        )

    def test_as_utc_keeps_utc_time(self) -> None:
        value = datetime(2026, 10, 27, 7, 15, tzinfo=timezone.utc)
        assert as_utc(value) == value

    def test_as_utc_rejects_other_offset_instead_of_converting(self) -> None:
        plus_one = timezone(timedelta(hours=1))
        with pytest.raises(ValueError, match="UTC"):
            as_utc(datetime(2026, 10, 27, 8, 15, tzinfo=plus_one))


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


def utc(hour: int, minute: int, second: int = 0, day: date = DAY) -> datetime:
    return datetime(
        day.year, day.month, day.day, hour, minute, second, tzinfo=timezone.utc
    )


def interval_index(hour: int, minute: int, interval_minutes: int = 1) -> int:
    """Index of the interval containing the UTC time on DAY."""
    return (hour * MINUTES_PER_HOUR + minute) // interval_minutes


def record(
    road_user: str,
    flow_id: str,
    road_user_type: str,
    occurrence: datetime,
    speed_mps: float | None = None,
) -> AssignmentRecord:
    return AssignmentRecord(
        road_user=road_user,
        flow_id=flow_id,
        road_user_type=road_user_type,
        start_occurrence=occurrence,
        end_occurrence=occurrence,
        avg_speed_mps=speed_mps,
    )


def create_statistics(
    config: TrafficStatisticsConfig | None = None, covered: bool = True
) -> DayTrafficStatistics:
    config = config or TrafficStatisticsConfig()
    stats = DayTrafficStatistics(DAY, config, [FLOW_1, FLOW_2])
    if covered:
        stats.mark_covered(day_start(DAY), day_start(NEXT_DAY))
    return stats


class TestDayTrafficStatistics:
    def test_record_counts_into_its_minute_bin(self) -> None:
        stats = create_statistics()
        assert stats.add(record("ru1", "f1", "LV", utc(7, 15, 30)))
        counts = stats.counts("f1")["LV"]
        assert len(counts) == MINUTES_PER_DAY
        assert counts[interval_index(7, 15)] == 1
        assert counts[interval_index(7, 14)] == 0

    def test_uncovered_minute_without_counts_is_none(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(utc(7, 0), utc(8, 0))
        stats.add(record("ru1", "f1", "LV", utc(7, 15)))
        counts = stats.counts("f1")["LV"]
        assert counts[interval_index(7, 14)] == 0
        assert counts[interval_index(7, 15)] == 1
        assert counts[interval_index(0, 0)] is None
        assert counts[interval_index(8, 0)] is None

    def test_uncovered_minute_with_count_is_int(self) -> None:
        stats = create_statistics(covered=False)
        stats.add(record("ru1", "f1", "LV", utc(7, 15)))
        assert stats.counts("f1")["LV"][interval_index(7, 15)] == 1

    def test_interval_overlapping_coverage_is_covered(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(interval_minutes=FIVE_MINUTES),
            covered=False,
        )
        stats.add(record("ru0", "f1", "LV", utc(0, 0)))
        stats.mark_covered(utc(7, 3), utc(7, 4))
        counts = stats.counts("f1")["LV"]
        covered = interval_index(7, 3, interval_minutes=FIVE_MINUTES)
        assert counts[covered] == 0
        assert counts[covered + 1] is None

    def test_duplicate_road_user_is_counted_once(self) -> None:
        stats = create_statistics()
        assert stats.add(record("ru1", "f1", "LV", utc(7, 15)))
        assert not stats.add(record("ru1", "f2", "LV", utc(7, 16)))
        assert stats.totals(TOTAL) == {"LV": 1}
        assert stats.road_user_ids == {"ru1"}

    def test_total_sums_flows(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(7, 15)))
        stats.add(record("ru2", "f2", "LV", utc(7, 15)))
        assert stats.counts(TOTAL)["LV"][interval_index(7, 15)] == 2
        assert stats.totals("f1") == {"LV": 1}

    def test_total_is_none_where_no_flow_has_coverage(self) -> None:
        stats = create_statistics(covered=False)
        stats.add(record("ru1", "f1", "LV", utc(7, 15)))
        assert stats.counts(TOTAL)["LV"][interval_index(0, 0)] is None

    def test_record_of_other_day_is_rejected(self) -> None:
        stats = create_statistics()
        assert not stats.add(record("ru1", "f1", "LV", utc(7, 15, day=NEXT_DAY)))
        assert stats.road_user_ids == set()

    def test_unknown_flow_is_rejected(self) -> None:
        stats = create_statistics()
        assert not stats.add(record("ru1", "unknown", "LV", utc(7, 15)))

    def test_naive_occurrence_is_treated_as_utc(self) -> None:
        stats = create_statistics()
        assert stats.add(record("ru1", "f1", "LV", datetime(2026, 10, 27, 6, 15)))
        assert stats.counts("f1")["LV"][interval_index(6, 15)] == 1

    def test_day_is_cut_at_utc_midnight(self) -> None:
        stats = create_statistics()
        assert not stats.add(
            record("ru1", "f1", "LV", utc(23, 59, 59, day=PREVIOUS_DAY))
        )
        assert stats.add(record("ru2", "f1", "LV", utc(0, 0)))
        assert stats.counts("f1")["LV"][interval_index(0, 0)] == 1

    def test_occurrence_with_other_offset_is_rejected(self) -> None:
        stats = create_statistics()
        plus_two = timezone(timedelta(hours=2))
        occurrence = datetime(2026, 10, 27, 9, 0, tzinfo=plus_two)
        with pytest.raises(ValueError, match="UTC"):
            stats.add(record("ru1", "f1", "LV", occurrence))

    def test_five_minute_interval_has_288_bins(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(interval_minutes=FIVE_MINUTES)
        )
        stats.add(record("ru1", "f1", "LV", utc(7, 17)))
        counts = stats.counts("f1")["LV"]
        assert len(counts) == MINUTES_PER_DAY // FIVE_MINUTES
        assert counts[interval_index(7, 17, interval_minutes=FIVE_MINUTES)] == 1

    def test_mark_covered_merges_and_clips(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(utc(7, 0), utc(8, 0))
        stats.mark_covered(utc(7, 30), utc(9, 0))
        stats.mark_covered(utc(9, 0), utc(9, 30))
        stats.mark_covered(utc(23, 0, day=PREVIOUS_DAY), utc(0, 30))
        assert stats.coverage == [
            (utc(0, 0), utc(0, 30)),
            (utc(7, 0), utc(9, 30)),
        ]

    def test_only_plausible_speeds_enter_speed_profile(self) -> None:
        max_speed_kmh = 100
        too_fast_mps = max_speed_kmh / KMH_PER_MPS + 1
        config = replace(QUARTER_HOUR_CONFIG, max_speed_kmh=max_speed_kmh)
        stats = create_statistics(config)
        stats.add(record("ru1", "f1", "LV", utc(7, 20), SLOW_MPS))
        stats.add(record("ru2", "f1", "LV", utc(7, 21), too_fast_mps))
        stats.add(record("ru3", "f1", "LV", utc(7, 22)))
        stats.add(record("ru4", "f1", "LV", utc(7, 23), STANDING_MPS))
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert stats.speed_profile("f1")["LV"][slot] == SpeedValues(
            SLOW_KMH, SLOW_KMH, 1
        )
        assert stats.totals("f1") == {"LV": 4}

    def test_counting_event_defaults_to_start(self) -> None:
        assert create_statistics().counting_event == CountingEvent.START

    def test_end_counting_event_counts_at_end_occurrence(self) -> None:
        config = TrafficStatisticsConfig()
        stats = DayTrafficStatistics(DAY, config, [FLOW_1], CountingEvent.END)
        start_and_end = replace(
            record("ru1", "f1", "LV", utc(7, 15)), end_occurrence=utc(7, 20)
        )
        assert stats.add(start_and_end)
        assert stats.counts("f1")["LV"][interval_index(7, 20)] == 1

    def test_classification_without_class_group_is_rejected(self) -> None:
        config = TrafficStatisticsConfig(class_groups={"SV": frozenset({"truck"})})
        stats = create_statistics(config)
        assert not stats.add(record("ru1", "f1", "car", utc(7, 15)))
        assert stats.road_user_ids == set()

    def test_classification_is_counted_in_its_class_group(self) -> None:
        config = TrafficStatisticsConfig(class_groups={"LV": frozenset({"car", "van"})})
        stats = create_statistics(config)
        stats.add(record("ru1", "f1", "car", utc(7, 15)))
        stats.add(record("ru2", "f1", "van", utc(7, 15)))
        assert stats.totals("f1") == {"LV": 2}


class TestMergeRanges:
    def test_merges_overlapping_and_touching_ranges_in_order(self) -> None:
        ranges = [
            CoverageRange(utc(9, 0), utc(9, 30)),
            CoverageRange(utc(7, 30), utc(9, 0)),
            CoverageRange(utc(0, 0), utc(0, 30)),
            CoverageRange(utc(7, 0), utc(8, 0)),
        ]
        assert merge_ranges(ranges) == [
            CoverageRange(utc(0, 0), utc(0, 30)),
            CoverageRange(utc(7, 0), utc(9, 30)),
        ]

    def test_keeps_enclosing_range(self) -> None:
        ranges = [
            CoverageRange(utc(7, 0), utc(9, 0)),
            CoverageRange(utc(7, 30), utc(8, 0)),
        ]
        assert merge_ranges(ranges) == [CoverageRange(utc(7, 0), utc(9, 0))]

    def test_without_ranges_is_empty(self) -> None:
        assert merge_ranges([]) == []


class TestPeakHour:
    def test_peak_hour_finds_strongest_quarter_aligned_window(self) -> None:
        stats = create_statistics()
        for index, (hour, minute) in enumerate([(6, 0), (7, 20), (7, 50), (8, 10)]):
            stats.add(record(f"ru{index}", "f1", "LV", utc(hour, minute)))
        assert stats.peak_hour("f1") == {
            "LV": PeakHour(start=utc(7, 15), end=utc(8, 15), count=3)
        }

    def test_peak_hour_tie_returns_earliest(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(6, 30)))
        stats.add(record("ru2", "f1", "LV", utc(9, 30)))
        assert stats.peak_hour("f1") == {
            "LV": PeakHour(start=utc(5, 45), end=utc(6, 45), count=1)
        }

    def test_peak_hour_total_sums_flows(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(7, 0)))
        stats.add(record("ru2", "f2", "LV", utc(7, 10)))
        assert stats.peak_hour(TOTAL)["LV"].count == 2

    def test_peak_hour_ignores_uncovered_windows(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(utc(7, 0), utc(9, 0))
        stats.add(record("ru1", "f1", "LV", utc(7, 30)))
        assert stats.peak_hour("f1")["LV"].start == utc(6, 45)

    def test_peak_hour_without_data_is_absent(self) -> None:
        stats = create_statistics()
        assert stats.peak_hour("f1") == {}

    def test_peak_hour_windows_lie_completely_in_the_day(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(23, 50)))
        assert stats.peak_hour("f1")["LV"] == PeakHour(
            start=utc(23, 0), end=utc(0, 0, day=NEXT_DAY), count=1
        )


class TestSpeed:
    def test_total_speed_merges_flows(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(7, 0), SLOW_MPS))
        stats.add(record("ru2", "f2", "LV", utc(7, 5), FAST_MPS))
        assert stats.speed(TOTAL) == {"LV": SpeedValues(AVG_SLOW_FAST_KMH, FAST_KMH, 2)}
        assert stats.speed("f1") == {"LV": SpeedValues(SLOW_KMH, SLOW_KMH, 1)}

    def test_implausible_speed_is_counted_but_not_in_speed(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(7, 0), IMPLAUSIBLE_MPS))
        assert stats.totals("f1") == {"LV": 1}
        assert stats.speed("f1") == {}

    def test_speed_merges_all_slots(self) -> None:
        stats = create_statistics()
        stats.add(record("ru1", "f1", "LV", utc(7, 0), SLOW_MPS))
        stats.add(record("ru2", "f1", "LV", utc(18, 0), FAST_MPS))
        assert stats.speed("f1")["LV"].count == 2

    def test_speed_profile_uses_count_intervals(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(interval_minutes=FIVE_MINUTES)
        )
        stats.add(record("ru1", "f1", "LV", utc(7, 22), SLOW_MPS))
        profile = stats.speed_profile("f1")["LV"]
        assert len(profile) == MINUTES_PER_DAY // FIVE_MINUTES
        assert profile[
            interval_index(7, 22, interval_minutes=FIVE_MINUTES)
        ] == SpeedValues(SLOW_KMH, SLOW_KMH, 1)

    def test_speed_profile_has_value_only_in_occupied_slot(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record("ru1", "f1", "LV", utc(7, 20), SLOW_MPS))
        profile = stats.speed_profile("f1")["LV"]
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert len(profile) == QUARTER_HOURS
        assert profile[slot] == SpeedValues(SLOW_KMH, SLOW_KMH, 1)
        assert [v for i, v in enumerate(profile) if i != slot and v is not None] == []

    def test_speed_profile_contains_counted_group_without_speed(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record("ru1", "f1", "LV", utc(7, 20)))
        assert stats.speed_profile("f1") == {"LV": [None] * QUARTER_HOURS}

    def test_speed_profile_contains_configured_groups_without_data(self) -> None:
        config = TrafficStatisticsConfig(
            interval_minutes=QUARTER_HOUR_MINUTES,
            class_groups={"LV": frozenset({"car"}), "HV": frozenset({"truck"})},
        )
        stats = create_statistics(config)
        stats.add(record("ru1", "f1", "car", utc(7, 20), SLOW_MPS))
        profile = stats.speed_profile("f1")
        assert set(profile) == {"LV", "HV"}
        assert profile["HV"] == [None] * QUARTER_HOURS
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert profile["LV"][slot] == SpeedValues(SLOW_KMH, SLOW_KMH, 1)

    def test_speed_profile_of_total_merges_flows_per_slot(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record("ru1", "f1", "LV", utc(7, 20), SLOW_MPS))
        stats.add(record("ru2", "f2", "LV", utc(7, 25), FAST_MPS))
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert stats.speed_profile(TOTAL)["LV"][slot] == SpeedValues(
            AVG_SLOW_FAST_KMH, FAST_KMH, 2
        )

    def test_total_speed_profile_merges_flows_and_groups_per_slot(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record("ru1", "f1", "LV", utc(7, 20), SLOW_MPS))
        stats.add(record("ru2", "f2", "SV", utc(7, 25), FAST_MPS))
        stats.add(record("ru3", "f2", "SV", utc(9, 0)))
        profile = stats.total_speed_profile()
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert len(profile) == QUARTER_HOURS
        assert profile[slot] == SpeedValues(AVG_SLOW_FAST_KMH, FAST_KMH, 2)
        assert [v for i, v in enumerate(profile) if i != slot and v is not None] == []


class TestAssignmentRecord:
    def test_from_assignment_takes_interpolated_times_and_speed(self) -> None:
        assignment = create_assignment(distance=100, start_s=0, end_s=10)
        assert AssignmentRecord.from_assignment(assignment) == AssignmentRecord(
            road_user="1",
            flow_id="flow",
            road_user_type="car",
            start_occurrence=datetime(2020, 1, 1, tzinfo=timezone.utc),
            end_occurrence=datetime(2020, 1, 1, 0, 0, 10, tzinfo=timezone.utc),
            avg_speed_mps=10.0,
        )

    def test_missing_distance_gives_no_speed(self) -> None:
        assignment = create_assignment(distance=None, start_s=0, end_s=10)
        assert AssignmentRecord.from_assignment(assignment).speed_kmh is None

    def test_speed_is_converted_to_kmh(self) -> None:
        assert record("ru1", "f1", "LV", utc(7, 0), SLOW_MPS).speed_kmh == SLOW_KMH

    def test_occurrence_of_counting_event(self) -> None:
        start_and_end = replace(
            record("ru1", "f1", "LV", utc(7, 15)), end_occurrence=utc(7, 20)
        )
        assert start_and_end.occurrence(CountingEvent.START) == utc(7, 15)
        assert start_and_end.occurrence(CountingEvent.END) == utc(7, 20)

    def test_naive_occurrence_is_treated_as_utc(self) -> None:
        naive = record("ru1", "f1", "LV", datetime(2020, 1, 1, 12, 0))
        assert naive.occurrence(CountingEvent.START) == datetime(
            2020, 1, 1, 12, tzinfo=timezone.utc
        )
