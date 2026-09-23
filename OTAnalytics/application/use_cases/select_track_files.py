import math
from collections.abc import Iterable
from pathlib import Path


class SelectEquallySpacedTrackFiles:
    def __init__(self, fraction: float) -> None:
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("Fraction must be between 0.0 and 1.0")
        self._fraction = fraction

    def select(self, track_files: Iterable[Path]) -> list[Path]:
        ordered = sorted(list(track_files))

        total_count = len(ordered)
        if total_count == 0:
            return ordered

        if self._fraction == 1.0:
            return ordered

        selected_count = min(total_count, math.ceil(self._fraction * total_count))

        if selected_count == 0:
            return []

        if selected_count == 1:
            return [ordered[0]]

        return [
            ordered[round(index * (total_count - 1) / (selected_count - 1))]
            for index in range(selected_count)
        ]
