import pytest

from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)


class TestTrafficStatisticsConfig:
    def test_defaults(self) -> None:
        config = TrafficStatisticsConfig()

        assert config.enabled is True
        assert config.timezone == "UTC"
        assert config.interval_minutes == 1
        assert config.speed_profile_interval_minutes == 15
        assert config.max_speed_kmh == 200.0
        assert config.class_groups == {}
        assert config.peak_window_minutes == 60
        assert config.peak_step_minutes == 15

    @pytest.mark.parametrize("interval", [1, 5, 15, 60])
    def test_valid_intervals(self, interval: int) -> None:
        TrafficStatisticsConfig(
            interval_minutes=interval,
            speed_profile_interval_minutes=60,
            peak_step_minutes=60,
        )

    @pytest.mark.parametrize("interval", [0, -5, 7, 45, 120])
    def test_invalid_interval_raises_with_field_name(self, interval: int) -> None:
        with pytest.raises(ValueError, match="interval_minutes"):
            TrafficStatisticsConfig(interval_minutes=interval)

    def test_speed_profile_interval_must_be_multiple_of_interval(self) -> None:
        with pytest.raises(ValueError, match="speed_profile_interval_minutes"):
            TrafficStatisticsConfig(
                interval_minutes=10, speed_profile_interval_minutes=15
            )

    def test_peak_step_must_be_multiple_of_interval(self) -> None:
        with pytest.raises(ValueError, match="peak_step_minutes"):
            TrafficStatisticsConfig(
                interval_minutes=10,
                speed_profile_interval_minutes=20,
                peak_step_minutes=15,
            )

    def test_unknown_timezone_raises_with_field_name(self) -> None:
        with pytest.raises(ValueError, match="timezone"):
            TrafficStatisticsConfig(timezone="Mars/Olympus")
