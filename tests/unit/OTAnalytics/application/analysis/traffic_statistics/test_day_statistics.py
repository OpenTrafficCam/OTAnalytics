import logging
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
    day_start,
    minutes_in_day,
)
from OTAnalytics.application.analysis.traffic_statistics.speed_histogram import (
    SpeedHistogram,
)
from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)

TZ = ZoneInfo("Europe/Berlin")
DAY = date(2026, 10, 27)


class TestDayHelpers:
    def test_day_start_is_local_midnight(self) -> None:
        assert day_start(DAY, TZ).isoformat() == "2026-10-27T00:00:00+01:00"

    def test_regular_day_has_1440_minutes(self) -> None:
        assert minutes_in_day(DAY, TZ) == 1440

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
        assert len(counts) == 1440
        assert counts[435] == 1
        assert counts[434] == 0

    def test_uncovered_minute_without_counts_is_none(self) -> None:
        stats = create_statistics(covered=False)
        stats.mark_covered(local(7, 0), local(8, 0))
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        counts = stats.counts("f1")["LV"]
        assert counts[434] == 0
        assert counts[435] == 1
        assert counts[0] is None
        assert counts[480] is None

    def test_uncovered_minute_with_count_is_int(self) -> None:
        stats = create_statistics(covered=False)
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        assert stats.counts("f1")["LV"][435] == 1

    def test_interval_overlapping_coverage_is_covered(self) -> None:
        stats = create_statistics(
            TrafficStatisticsConfig(timezone="Europe/Berlin", interval_minutes=5),
            covered=False,
        )
        stats.add("ru0", "f1", "LV", local(0, 0), None)
        stats.mark_covered(local(7, 3), local(7, 4))
        counts = stats.counts("f1")["LV"]
        assert counts[7 * 12] == 0
        assert counts[7 * 12 + 1] is None

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
        assert stats.counts(TOTAL)["LV"][435] == 2
        assert stats.totals("f1") == {"LV": 1}

    def test_total_is_none_where_no_flow_has_coverage(self) -> None:
        stats = create_statistics(covered=False)
        stats.add("ru1", "f1", "LV", local(7, 15), None)
        assert stats.counts(TOTAL)["LV"][0] is None

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
        assert stats.add("ru1", "f1", "LV", datetime(2026, 10, 27, 6, 15), None)
        assert stats.counts("f1")["LV"][435] == 1

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
        assert len(counts) == 288
        assert counts[87] == 1

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

    def test_speeds_are_stored_in_speed_profile_histograms(self) -> None:
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
        histograms = stats.histograms()["f1"]["LV"]
        assert len(histograms) == 96
        assert histograms[29].bins == {50: 1}
        assert sum(h.count for h in histograms) == 1

    def test_restore_reproduces_state(self) -> None:
        stats = create_statistics()
        stats.add("ru1", "f1", "LV", local(7, 15), 40.0)
        as_of = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
        restored = DayTrafficStatistics.restore(
            DAY,
            stats.config,
            [FLOW_1, FLOW_2],
            stats.raw_counts(),
            stats.histograms(),
            stats.coverage,
            stats.road_user_ids,
            as_of,
            counting_event=CountingEvent.END,
        )
        assert restored.counts("f1") == stats.counts("f1")
        assert restored.coverage == stats.coverage
        assert restored.road_user_ids == {"ru1"}
        assert restored.as_of == as_of
        assert restored.counting_event == CountingEvent.END
        assert not restored.add("ru1", "f1", "LV", local(7, 16), None)
        assert restored.histograms()["f1"]["LV"][29].bins == {40: 1}
        assert isinstance(restored.histograms()["f1"]["LV"][29], SpeedHistogram)

    def test_counting_event_defaults_to_start(self) -> None:
        assert create_statistics().counting_event == CountingEvent.START
