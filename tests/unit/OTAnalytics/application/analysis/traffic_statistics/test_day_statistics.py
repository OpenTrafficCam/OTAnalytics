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

ROAD_USER_1 = "ru1"
ROAD_USER_2 = "ru2"
ROAD_USER_3 = "ru3"
ROAD_USER_4 = "ru4"

FLOW_ID_1 = "f1"
FLOW_ID_2 = "f2"
FLOW_ID_3 = "f3"
UNKNOWN_FLOW_ID = "unknown"
SECTION_ID_1 = "s1"
SECTION_ID_2 = "s2"
SECTION_ID_3 = "s3"

CAR = "car"
VAN = "van"
TRUCK = "truck"
BICYCLE = "bike"
LIGHT_VEHICLES = "LV"
HEAVY_VEHICLES = "SV"


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
        assert resolver.group_of(CAR) == CAR

    def test_maps_classification_to_group(self) -> None:
        config = TrafficStatisticsConfig(
            class_groups={
                LIGHT_VEHICLES: frozenset({CAR, VAN}),
                HEAVY_VEHICLES: frozenset({TRUCK}),
            }
        )
        resolver = ClassGroupResolver(config)
        assert resolver.group_of(VAN) == LIGHT_VEHICLES
        assert resolver.group_of(CAR) == LIGHT_VEHICLES
        assert resolver.group_of(TRUCK) == HEAVY_VEHICLES

    def test_unknown_classification_is_ignored_and_warned_once(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        config = TrafficStatisticsConfig(
            class_groups={LIGHT_VEHICLES: frozenset({CAR})}
        )
        resolver = ClassGroupResolver(config)
        with caplog.at_level(logging.WARNING):
            assert resolver.group_of(BICYCLE) is None
            assert resolver.group_of(BICYCLE) is None
        assert len([r for r in caplog.records if BICYCLE in r.getMessage()]) == 1


FLOW_1 = FlowInfo(
    FLOW_ID_1, "Flow 1", 0, SECTION_ID_1, "Section 1", SECTION_ID_2, "Section 2"
)
FLOW_2 = FlowInfo(
    FLOW_ID_2, "Flow 2", 1, SECTION_ID_1, "Section 1", SECTION_ID_3, "Section 3"
)


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
        assert stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15, 30)))
        counts = stats.counts(FLOW_ID_1)[LIGHT_VEHICLES]
        assert len(counts) == MINUTES_PER_DAY
        assert counts[interval_index(7, 15)] == 1
        assert counts[interval_index(7, 14)] == 0

    def test_uncovered_minute_without_counts_is_none(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(utc(7, 0), utc(8, 0))
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)))
        counts = stats.counts(FLOW_ID_1)[LIGHT_VEHICLES]
        assert counts[interval_index(7, 14)] == 0
        assert counts[interval_index(7, 15)] == 1
        assert counts[interval_index(0, 0)] is None
        assert counts[interval_index(8, 0)] is None

    def test_uncovered_minute_with_count_is_int(self) -> None:
        stats = create_statistics(covered=False)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)))
        assert stats.counts(FLOW_ID_1)[LIGHT_VEHICLES][interval_index(7, 15)] == 1

    def test_interval_overlapping_coverage_is_covered(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(interval_minutes=FIVE_MINUTES),
            covered=False,
        )
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(0, 0)))
        stats.mark_covered(utc(7, 3), utc(7, 4))
        counts = stats.counts(FLOW_ID_1)[LIGHT_VEHICLES]
        covered = interval_index(7, 3, interval_minutes=FIVE_MINUTES)
        assert counts[covered] == 0
        assert counts[covered + 1] is None

    def test_duplicate_road_user_is_counted_once(self) -> None:
        stats = create_statistics()
        assert stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)))
        assert not stats.add(record(ROAD_USER_1, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 16)))
        assert stats.totals(TOTAL) == {LIGHT_VEHICLES: 1}
        assert stats.road_user_ids == {ROAD_USER_1}

    def test_total_sums_flows(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)))
        stats.add(record(ROAD_USER_2, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 15)))
        assert stats.counts(TOTAL)[LIGHT_VEHICLES][interval_index(7, 15)] == 2
        assert stats.totals(FLOW_ID_1) == {LIGHT_VEHICLES: 1}

    def test_total_is_none_where_no_flow_has_coverage(self) -> None:
        stats = create_statistics(covered=False)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)))
        assert stats.counts(TOTAL)[LIGHT_VEHICLES][interval_index(0, 0)] is None

    def test_update_flows_replaces_flows_and_drops_removed_flow_data(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 15), SLOW_MPS))
        new_flow = FlowInfo(
            FLOW_ID_3, "new", 1, SECTION_ID_1, "Section 1", SECTION_ID_3, "Section 3"
        )
        renamed = replace(FLOW_1, name="renamed", index=2)

        stats.update_flows([new_flow, renamed])

        assert stats.flows == [new_flow, renamed]
        assert stats.add(record(ROAD_USER_2, FLOW_ID_3, LIGHT_VEHICLES, utc(7, 16)))
        assert stats.totals(TOTAL) == {LIGHT_VEHICLES: 1}
        assert stats.speed(TOTAL) == {}
        assert not stats.add(record(ROAD_USER_3, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 17)))

    def test_record_of_other_day_is_rejected(self) -> None:
        stats = create_statistics()
        assert not stats.add(
            record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15, day=NEXT_DAY))
        )
        assert stats.road_user_ids == set()

    def test_unknown_flow_is_rejected(self) -> None:
        stats = create_statistics()
        assert not stats.add(
            record(ROAD_USER_1, UNKNOWN_FLOW_ID, LIGHT_VEHICLES, utc(7, 15))
        )

    def test_naive_occurrence_is_treated_as_utc(self) -> None:
        stats = create_statistics()
        assert stats.add(
            record(
                ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, datetime(2026, 10, 27, 6, 15)
            )
        )
        assert stats.counts(FLOW_ID_1)[LIGHT_VEHICLES][interval_index(6, 15)] == 1

    def test_day_is_cut_at_utc_midnight(self) -> None:
        stats = create_statistics()
        assert not stats.add(
            record(
                ROAD_USER_1,
                FLOW_ID_1,
                LIGHT_VEHICLES,
                utc(23, 59, 59, day=PREVIOUS_DAY),
            )
        )
        assert stats.add(record(ROAD_USER_2, FLOW_ID_1, LIGHT_VEHICLES, utc(0, 0)))
        assert stats.counts(FLOW_ID_1)[LIGHT_VEHICLES][interval_index(0, 0)] == 1

    def test_occurrence_with_other_offset_is_rejected(self) -> None:
        stats = create_statistics()
        plus_two = timezone(timedelta(hours=2))
        occurrence = datetime(2026, 10, 27, 9, 0, tzinfo=plus_two)
        with pytest.raises(ValueError, match="UTC"):
            stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, occurrence))

    def test_five_minute_interval_has_288_bins(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(interval_minutes=FIVE_MINUTES)
        )
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 17)))
        counts = stats.counts(FLOW_ID_1)[LIGHT_VEHICLES]
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
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 20), SLOW_MPS))
        stats.add(
            record(ROAD_USER_2, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 21), too_fast_mps)
        )
        stats.add(record(ROAD_USER_3, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 22)))
        stats.add(
            record(ROAD_USER_4, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 23), STANDING_MPS)
        )
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert stats.speed_profile(FLOW_ID_1)[LIGHT_VEHICLES][slot] == SpeedValues(
            SLOW_KMH, SLOW_KMH, 1
        )
        assert stats.totals(FLOW_ID_1) == {LIGHT_VEHICLES: 4}

    def test_counting_event_defaults_to_start(self) -> None:
        assert create_statistics().counting_event == CountingEvent.START

    def test_end_counting_event_counts_at_end_occurrence(self) -> None:
        config = TrafficStatisticsConfig()
        stats = DayTrafficStatistics(DAY, config, [FLOW_1], CountingEvent.END)
        start_and_end = replace(
            record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)),
            end_occurrence=utc(7, 20),
        )
        assert stats.add(start_and_end)
        assert stats.counts(FLOW_ID_1)[LIGHT_VEHICLES][interval_index(7, 20)] == 1

    def test_classification_without_class_group_is_rejected(self) -> None:
        config = TrafficStatisticsConfig(
            class_groups={HEAVY_VEHICLES: frozenset({TRUCK})}
        )
        stats = create_statistics(config)
        assert not stats.add(record(ROAD_USER_1, FLOW_ID_1, CAR, utc(7, 15)))
        assert stats.road_user_ids == set()

    def test_classification_is_counted_in_its_class_group(self) -> None:
        config = TrafficStatisticsConfig(
            class_groups={LIGHT_VEHICLES: frozenset({CAR, VAN})}
        )
        stats = create_statistics(config)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, CAR, utc(7, 15)))
        stats.add(record(ROAD_USER_2, FLOW_ID_1, VAN, utc(7, 15)))
        assert stats.totals(FLOW_ID_1) == {LIGHT_VEHICLES: 2}


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
        road_users = [ROAD_USER_1, ROAD_USER_2, ROAD_USER_3, ROAD_USER_4]
        times = [utc(6, 0), utc(7, 20), utc(7, 50), utc(8, 10)]
        for road_user, occurrence in zip(road_users, times, strict=True):
            stats.add(record(road_user, FLOW_ID_1, LIGHT_VEHICLES, occurrence))
        assert stats.peak_hour(FLOW_ID_1) == {
            LIGHT_VEHICLES: PeakHour(start=utc(7, 15), end=utc(8, 15), count=3)
        }

    def test_peak_hour_tie_returns_earliest(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(6, 30)))
        stats.add(record(ROAD_USER_2, FLOW_ID_1, LIGHT_VEHICLES, utc(9, 30)))
        assert stats.peak_hour(FLOW_ID_1) == {
            LIGHT_VEHICLES: PeakHour(start=utc(5, 45), end=utc(6, 45), count=1)
        }

    def test_peak_hour_total_sums_flows(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 0)))
        stats.add(record(ROAD_USER_2, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 10)))
        assert stats.peak_hour(TOTAL)[LIGHT_VEHICLES].count == 2

    def test_peak_hour_ignores_uncovered_windows(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(utc(7, 0), utc(9, 0))
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 30)))
        assert stats.peak_hour(FLOW_ID_1)[LIGHT_VEHICLES].start == utc(6, 45)

    def test_peak_hour_without_data_is_absent(self) -> None:
        stats = create_statistics()
        assert stats.peak_hour(FLOW_ID_1) == {}

    def test_peak_hour_windows_lie_completely_in_the_day(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(23, 50)))
        assert stats.peak_hour(FLOW_ID_1)[LIGHT_VEHICLES] == PeakHour(
            start=utc(23, 0), end=utc(0, 0, day=NEXT_DAY), count=1
        )


class TestSpeed:
    def test_total_speed_merges_flows(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 0), SLOW_MPS))
        stats.add(record(ROAD_USER_2, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 5), FAST_MPS))
        assert stats.speed(TOTAL) == {
            LIGHT_VEHICLES: SpeedValues(AVG_SLOW_FAST_KMH, FAST_KMH, 2)
        }
        assert stats.speed(FLOW_ID_1) == {
            LIGHT_VEHICLES: SpeedValues(SLOW_KMH, SLOW_KMH, 1)
        }

    def test_implausible_speed_is_counted_but_not_in_speed(self) -> None:
        stats = create_statistics()
        stats.add(
            record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 0), IMPLAUSIBLE_MPS)
        )
        assert stats.totals(FLOW_ID_1) == {LIGHT_VEHICLES: 1}
        assert stats.speed(FLOW_ID_1) == {}

    def test_speed_merges_all_slots(self) -> None:
        stats = create_statistics()
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 0), SLOW_MPS))
        stats.add(record(ROAD_USER_2, FLOW_ID_1, LIGHT_VEHICLES, utc(18, 0), FAST_MPS))
        assert stats.speed(FLOW_ID_1)[LIGHT_VEHICLES].count == 2

    def test_speed_profile_uses_count_intervals(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(interval_minutes=FIVE_MINUTES)
        )
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 22), SLOW_MPS))
        profile = stats.speed_profile(FLOW_ID_1)[LIGHT_VEHICLES]
        assert len(profile) == MINUTES_PER_DAY // FIVE_MINUTES
        assert profile[
            interval_index(7, 22, interval_minutes=FIVE_MINUTES)
        ] == SpeedValues(SLOW_KMH, SLOW_KMH, 1)

    def test_speed_profile_has_value_only_in_occupied_slot(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 20), SLOW_MPS))
        profile = stats.speed_profile(FLOW_ID_1)[LIGHT_VEHICLES]
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert len(profile) == QUARTER_HOURS
        assert profile[slot] == SpeedValues(SLOW_KMH, SLOW_KMH, 1)
        assert [v for i, v in enumerate(profile) if i != slot and v is not None] == []

    def test_speed_profile_contains_counted_group_without_speed(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 20)))
        assert stats.speed_profile(FLOW_ID_1) == {
            LIGHT_VEHICLES: [None] * QUARTER_HOURS
        }

    def test_speed_profile_contains_configured_groups_without_data(self) -> None:
        config = TrafficStatisticsConfig(
            interval_minutes=QUARTER_HOUR_MINUTES,
            class_groups={
                LIGHT_VEHICLES: frozenset({CAR}),
                HEAVY_VEHICLES: frozenset({TRUCK}),
            },
        )
        stats = create_statistics(config)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, CAR, utc(7, 20), SLOW_MPS))
        profile = stats.speed_profile(FLOW_ID_1)
        assert set(profile) == {LIGHT_VEHICLES, HEAVY_VEHICLES}
        assert profile[HEAVY_VEHICLES] == [None] * QUARTER_HOURS
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert profile[LIGHT_VEHICLES][slot] == SpeedValues(SLOW_KMH, SLOW_KMH, 1)

    def test_speed_profile_of_total_merges_flows_per_slot(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 20), SLOW_MPS))
        stats.add(record(ROAD_USER_2, FLOW_ID_2, LIGHT_VEHICLES, utc(7, 25), FAST_MPS))
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert stats.speed_profile(TOTAL)[LIGHT_VEHICLES][slot] == SpeedValues(
            AVG_SLOW_FAST_KMH, FAST_KMH, 2
        )

    def test_total_speed_profile_merges_flows_and_groups_per_slot(self) -> None:
        stats = create_statistics(QUARTER_HOUR_CONFIG)
        stats.add(record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 20), SLOW_MPS))
        stats.add(record(ROAD_USER_2, FLOW_ID_2, HEAVY_VEHICLES, utc(7, 25), FAST_MPS))
        stats.add(record(ROAD_USER_3, FLOW_ID_2, HEAVY_VEHICLES, utc(9, 0)))
        profile = stats.total_speed_profile()
        slot = interval_index(7, 20, interval_minutes=QUARTER_HOUR_MINUTES)
        assert len(profile) == QUARTER_HOURS
        assert profile[slot] == SpeedValues(AVG_SLOW_FAST_KMH, FAST_KMH, 2)
        assert [v for i, v in enumerate(profile) if i != slot and v is not None] == []


class TestAssignmentRecord:
    def test_from_assignment_takes_interpolated_times_and_speed(self) -> None:
        assignment = create_assignment(
            distance=100,
            start_s=0,
            end_s=10,
            road_user=ROAD_USER_1,
            road_user_type=CAR,
        )
        assert AssignmentRecord.from_assignment(assignment) == AssignmentRecord(
            road_user=ROAD_USER_1,
            flow_id="flow",
            road_user_type=CAR,
            start_occurrence=datetime(2020, 1, 1, tzinfo=timezone.utc),
            end_occurrence=datetime(2020, 1, 1, 0, 0, 10, tzinfo=timezone.utc),
            avg_speed_mps=10.0,
        )

    def test_missing_distance_gives_no_speed(self) -> None:
        assignment = create_assignment(distance=None, start_s=0, end_s=10)
        assert AssignmentRecord.from_assignment(assignment).speed_kmh is None

    def test_speed_is_converted_to_kmh(self) -> None:
        assert (
            record(
                ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 0), SLOW_MPS
            ).speed_kmh
            == SLOW_KMH
        )

    def test_occurrence_of_counting_event(self) -> None:
        start_and_end = replace(
            record(ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, utc(7, 15)),
            end_occurrence=utc(7, 20),
        )
        assert start_and_end.occurrence(CountingEvent.START) == utc(7, 15)
        assert start_and_end.occurrence(CountingEvent.END) == utc(7, 20)

    def test_naive_occurrence_is_treated_as_utc(self) -> None:
        naive = record(
            ROAD_USER_1, FLOW_ID_1, LIGHT_VEHICLES, datetime(2020, 1, 1, 12, 0)
        )
        assert naive.occurrence(CountingEvent.START) == datetime(
            2020, 1, 1, 12, tzinfo=timezone.utc
        )
