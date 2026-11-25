"""Summary values of road user speeds used for traffic statistics."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SpeedValues:
    """Summary of measured speeds.

    Attributes:
        avg: mean speed in km/h, rounded to one decimal.
        v85: 85th percentile speed in km/h (nearest rank), rounded to one
            decimal.
        count: number of speeds.
    """

    avg: float
    v85: float
    count: int


def compute_speed_values(speeds: Sequence[float]) -> SpeedValues | None:
    """Return average and v85 of the speeds in km/h, or None if there are none."""
    count = len(speeds)
    if count == 0:
        return None
    # rank = ceil(0.85 * count), computed in integers to avoid float error
    rank = -(-85 * count // 100)
    v85 = sorted(speeds)[rank - 1]
    return SpeedValues(
        avg=round(sum(speeds) / count, 1), v85=round(v85, 1), count=count
    )
