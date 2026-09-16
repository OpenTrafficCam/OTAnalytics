"""The time range a user selects to decide which tracks and videos to load.

Deliberately separate from `DateRange`, which filters tracks that are already
loaded. A Load Window decides what gets fetched in the first place, and is
bounded by a configured maximum duration because continuous recording produces
far more data than can be held at once.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta


@dataclass(frozen=True)
class LoadWindow:
    """The start and end time selected for a load.

    Attributes:
        start (datetime): the first timestamp to load, inclusive.
        end (datetime): the last timestamp to load, inclusive.
        was_clamped (bool): whether `end` was shortened to respect a maximum
            duration, so the user can be told what was adjusted.
    """

    start: datetime
    end: datetime
    was_clamped: bool = False

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError(
                f"A load window cannot end ({self.end}) before it starts"
                f" ({self.start})."
            )

    @property
    def duration(self) -> timedelta:
        """How long the selected window is."""
        return self.end - self.start

    def clamp(self, maximum: timedelta) -> "LoadWindow":
        """Shorten the window to at most `maximum`, keeping its start.

        A window already within the maximum is returned unchanged, so an
        exactly-at-cap selection is never reported as adjusted.

        Args:
            maximum (timedelta): the longest window that may be loaded at once.

        Returns:
            LoadWindow: the window to actually load.
        """
        if self.duration <= maximum:
            return self
        return replace(self, end=self.start + maximum, was_clamped=True)

    def contains(self, moment: datetime) -> bool:
        """Whether a timestamp falls within the window, both ends inclusive.

        Args:
            moment (datetime): the timestamp to test.

        Returns:
            bool: True if the timestamp is within the window.
        """
        return self.start <= moment <= self.end
