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

    def test_classification_in_two_class_groups_raises(self) -> None:
        with pytest.raises(ValueError, match="class_groups.*car"):
            TrafficStatisticsConfig(
                class_groups={
                    "light": frozenset({"car", "bicycle"}),
                    "motor": frozenset({"car", "truck"}),
                }
            )

    @pytest.mark.parametrize("window", [0, -60, 50])
    def test_invalid_peak_window_raises_with_field_name(self, window: int) -> None:
        with pytest.raises(ValueError, match="peak_window_minutes"):
            TrafficStatisticsConfig(
                interval_minutes=15,
                speed_profile_interval_minutes=15,
                peak_window_minutes=window,
            )

    @pytest.mark.parametrize("max_speed", [0.0, -10.0])
    def test_non_positive_max_speed_raises_with_field_name(
        self, max_speed: float
    ) -> None:
        with pytest.raises(ValueError, match="max_speed_kmh"):
            TrafficStatisticsConfig(max_speed_kmh=max_speed)

    @pytest.mark.parametrize(
        "name",
        [
            "interval_minutes",
            "speed_profile_interval_minutes",
            "peak_window_minutes",
            "peak_step_minutes",
        ],
    )
    @pytest.mark.parametrize("value", [True, 15.0, "15"])
    def test_non_int_minutes_raise_with_field_name(
        self, name: str, value: object
    ) -> None:
        with pytest.raises(ValueError, match=name):
            TrafficStatisticsConfig(**{name: value})  # type: ignore[arg-type]
