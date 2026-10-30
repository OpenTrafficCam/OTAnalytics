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
        max_speed_kmh: speeds above this value are treated as implausible,
            must be > 0.
        class_groups: group name to the classifications it contains. Empty
            means every classification is its own group. A classification may
            belong to at most one group.
        peak_window_minutes: length of the sliding peak window, a multiple of
            interval_minutes.
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
        self._validate_int_fields()
        self._validate_timezone()
        self._validate_interval()
        self._validate_multiple_of_interval(
            "speed_profile_interval_minutes", self.speed_profile_interval_minutes
        )
        self._validate_multiple_of_interval(
            "peak_window_minutes", self.peak_window_minutes
        )
        self._validate_multiple_of_interval("peak_step_minutes", self.peak_step_minutes)
        self._validate_max_speed()
        self._validate_class_groups()

    def _validate_int_fields(self) -> None:
        for name in (
            "interval_minutes",
            "speed_profile_interval_minutes",
            "peak_window_minutes",
            "peak_step_minutes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer, got {value!r}.")

    def _validate_max_speed(self) -> None:
        value = self.max_speed_kmh
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not value > 0
        ):
            raise ValueError(f"max_speed_kmh must be a number > 0, got {value!r}.")

    def _validate_class_groups(self) -> None:
        group_by_classification: dict[str, str] = {}
        for group, classifications in self.class_groups.items():
            for classification in classifications:
                other = group_by_classification.setdefault(classification, group)
                if other != group:
                    raise ValueError(
                        f"class_groups assigns classification '{classification}' "
                        f"to more than one group ('{other}', '{group}')."
                    )

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
