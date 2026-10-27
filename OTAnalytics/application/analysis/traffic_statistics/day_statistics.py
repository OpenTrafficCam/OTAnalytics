"""Per local day statistics of road users per flow and class group."""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from OTAnalytics.application.analysis.traffic_statistics_config import (
    TrafficStatisticsConfig,
)

LOGGER = logging.getLogger(__name__)

TOTAL = "total"


@dataclass(frozen=True)
class FlowInfo:
    """Descriptive data of a flow in the statistics."""

    id: str
    name: str
    index: int
    start_section_id: str
    start_section_name: str
    end_section_id: str
    end_section_name: str


def day_start(day: date, tz: ZoneInfo) -> datetime:
    """Return the timezone aware start of the given local day."""
    return datetime(day.year, day.month, day.day, tzinfo=tz)


def minutes_in_day(day: date, tz: ZoneInfo) -> int:
    """Return the real number of minutes of the local day (DST aware)."""
    start = day_start(day, tz).astimezone(timezone.utc)
    end = day_start(day + timedelta(days=1), tz).astimezone(timezone.utc)
    return int((end - start).total_seconds() // 60)


class ClassGroupResolver:
    """Maps classifications to class groups defined in the config.

    Without configured class groups every classification is its own group.
    Unknown classifications resolve to None and are warned about once.
    """

    def __init__(self, config: TrafficStatisticsConfig) -> None:
        self._lookup: dict[str, str] = {
            classification: group
            for group, classifications in config.class_groups.items()
            for classification in classifications
        }
        self._use_identity = not config.class_groups
        self._warned: set[str] = set()

    def group_of(self, classification: str) -> str | None:
        """Return the group of the classification or None if it is unknown."""
        if self._use_identity:
            return classification
        group = self._lookup.get(classification)
        if group is None and classification not in self._warned:
            self._warned.add(classification)
            LOGGER.warning(
                "Classification '%s' is not part of any class group. "
                "Road users of this classification are ignored.",
                classification,
            )
        return group
