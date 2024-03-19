from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional


@dataclass(frozen=True)
class DateRange:
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    def duration(self) -> Optional[timedelta]:
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None


def validate_date(date: str, date_format: str) -> bool:
    """Validates a date string against a date format.

    Args:
        date (str): the date string
        date_format (str): the date formate

    Returns:
        bool: `True` if date string matches date format. Otherwise `False`.
    """
    try:
        datetime.strptime(date, date_format)
        return True
    except ValueError:
        return False


def validate_hour(hour: int) -> bool:
    """Validates if hour is in the correct time format.

    The hour is a natural number in range [0,23]

    Args:
        hour (int): the hour

    Returns:
        bool: `True` if hour is valid
    """
    try:
        time(hour=hour)
        return True
    except ValueError:
        return False


def validate_minute(minute: int) -> bool:
    """Validates if minute is in the correct time format.

    Minute must be a natural number in range[0,59]

    Args:
        minute (int): the hour value to validate

    Returns:
        bool: `True` if second value is valid. Otherwise `False`
    """
    try:
        time(minute=minute)
        return True
    except ValueError:
        return False


def validate_second(second: int) -> bool:
    """Validates if second is in the correct time format.

    Second must be a natural number in range[0,59]

    Args:
        second(int): the hour value to validate

    Returns:
        bool: `True` if second value is valid. Otherwise `False`
    """
    try:
        time(second=second)
        return True
    except ValueError:
        return False
