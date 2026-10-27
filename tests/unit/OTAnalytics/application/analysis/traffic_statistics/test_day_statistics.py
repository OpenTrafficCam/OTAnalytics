import logging
from datetime import date
from zoneinfo import ZoneInfo

import pytest

from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    ClassGroupResolver,
    day_start,
    minutes_in_day,
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
