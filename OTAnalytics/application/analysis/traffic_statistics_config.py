from dataclasses import dataclass, field
from typing import Mapping
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class TrafficStatisticsConfig:
    """Settings of the traffic statistics export.

    Attributes:
        enabled: whether the export runs. A disabled block is kept so that it
            survives a round trip through the otconfig.
        timezone: IANA timezone defining the day boundaries.
        interval_minutes: length of one statistics interval, divides 60.
        speed_profile_interval_minutes: interval of the speed profile, a
            multiple of interval_minutes.
        max_speed_kmh: speeds above this value are treated as implausible.
        class_groups: group name to the classifications it contains. Empty
            means every classification is its own group.
        peak_window_minutes: length of the sliding peak window.
        peak_step_minutes: step of the sliding peak window, a multiple of
            interval_minutes.
    """

    enabled: bool = True
    timezone: str = "UTC"
    interval_minutes: int = 1
    speed_profile_interval_minutes: int = 15
    max_speed_kmh: float = 200.0
    class_groups: Mapping[str, frozenset[str]] = field(default_factory=dict)
    peak_window_minutes: int = 60
    peak_step_minutes: int = 15

    def __post_init__(self) -> None:
        self._validate_timezone()
        self._validate_interval()
        self._validate_multiple_of_interval(
            "speed_profile_interval_minutes", self.speed_profile_interval_minutes
        )
        self._validate_multiple_of_interval("peak_step_minutes", self.peak_step_minutes)

    def _validate_timezone(self) -> None:
        try:
            ZoneInfo(self.timezone)
        except Exception as cause:
            raise ValueError(
                f"timezone '{self.timezone}' is not a valid IANA timezone."
            ) from cause

    def _validate_interval(self) -> None:
        if self.interval_minutes <= 0 or 60 % self.interval_minutes != 0:
            raise ValueError(
                f"interval_minutes must divide 60, got {self.interval_minutes}."
            )

    def _validate_multiple_of_interval(self, name: str, value: int) -> None:
        if value <= 0 or value % self.interval_minutes != 0:
            raise ValueError(
                f"{name} must be a multiple of interval_minutes "
                f"({self.interval_minutes}), got {value}."
            )
