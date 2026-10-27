"""Histogram of road user speeds used for traffic statistics."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SpeedValues:
    """Summary of the speeds in a histogram.

    Attributes:
        avg: mean speed in km/h, rounded to one decimal.
        v85: 85th percentile speed in km/h (nearest rank on 1 km/h bins),
            rounded to one decimal.
        count: number of speeds in the histogram.
    """

    avg: float
    v85: float
    count: int


class SpeedHistogram:
    """Histogram of speeds in km/h with 1 km/h bins.

    A speed is stored in the bin `math.floor(speed_kmh)`. The sum of all speeds
    is kept to compute the average exactly.
    """

    def __init__(
        self, bins: dict[int, int] | None = None, total_speed: float = 0.0
    ) -> None:
        """Create a histogram, optionally restoring stored bins and total speed.

        Args:
            bins: bin key (floor of the speed in km/h) to number of speeds.
            total_speed: sum of all speeds in km/h.
        """
        self._bins: dict[int, int] = dict(bins) if bins else {}
        self._total_speed = total_speed

    @property
    def bins(self) -> dict[int, int]:
        """Copy of the bin counts keyed by floor of the speed in km/h."""
        return dict(self._bins)

    @property
    def total_speed(self) -> float:
        """Sum of all speeds in km/h."""
        return self._total_speed

    @property
    def count(self) -> int:
        """Number of speeds in the histogram."""
        return sum(self._bins.values())

    def add(self, speed_kmh: float) -> None:
        """Add one speed in km/h to the histogram."""
        key = math.floor(speed_kmh)
        self._bins[key] = self._bins.get(key, 0) + 1
        self._total_speed += speed_kmh

    def merge(self, other: "SpeedHistogram") -> "SpeedHistogram":
        """Return a new histogram combining this and the other histogram.

        Neither histogram is modified.
        """
        merged_bins = dict(self._bins)
        for key, value in other._bins.items():
            merged_bins[key] = merged_bins.get(key, 0) + value
        return SpeedHistogram(
            bins=merged_bins,
            total_speed=self._total_speed + other._total_speed,
        )

    def values(self) -> SpeedValues | None:
        """Return average and v85 of the speeds, or None if the histogram is empty."""
        count = self.count
        if count == 0:
            return None
        avg = round(self._total_speed / count, 1)
        v85 = self._v85(count)
        return SpeedValues(avg=avg, v85=v85, count=count)

    def _v85(self, count: int) -> float:
        """Return the v85 speed for the given number of speeds (count > 0)."""
        # rank = ceil(0.85 * count), computed in integers to avoid float error
        rank = -(-85 * count // 100)
        cumulative = 0
        for key in sorted(self._bins):
            cumulative += self._bins[key]
            if cumulative >= rank:
                return round(key + 0.5, 1)
        raise AssertionError("cumulative count never reaches rank")
