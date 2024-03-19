from datetime import datetime, timedelta

import pytest

from OTAnalytics.domain.date import (
    DateRange,
    validate_date,
    validate_hour,
    validate_minute,
    validate_second,
)

DATE_FORMAT: str = r"%Y-%m-%d"


class TestDateValidation:
    @pytest.mark.parametrize(
        "hour,expected_result",
        [
            (0, True),
            (23, True),
            (24, False),
            (-1, False),
        ],
    )
    def test_validate_hour(self, hour: int, expected_result: bool) -> None:
        assert validate_hour(hour) is expected_result

    @pytest.mark.parametrize(
        "value,expected_result",
        [
            (0, True),
            (59, True),
            (60, False),
            (-1, False),
        ],
    )
    def test_validate_minute_and_seconds(
        self, value: int, expected_result: bool
    ) -> None:
        assert validate_minute(value) is expected_result
        assert validate_second(value) is expected_result

    @pytest.mark.parametrize(
        "value,expected_result",
        [
            ("2000-01-01", True),
            ("2000-02-29", True),
            ("2001-02-30", False),
        ],
    )
    def test_validate_date(self, value: str, expected_result: bool) -> None:
        assert validate_date(value, DATE_FORMAT) is expected_result


DURATION = timedelta(seconds=1)
START_DATE = datetime(2020, 1, 1)
END_DATE = START_DATE + DURATION


class TestDateRange:
    @pytest.mark.parametrize(
        "start,end,duration",
        [
            (START_DATE, END_DATE, DURATION),
            (None, END_DATE, None),
            (START_DATE, None, None),
            (None, None, None),
        ],
    )
    def test_duration(
        self, start: datetime, end: datetime, duration: timedelta
    ) -> None:
        range = DateRange(start_date=start, end_date=end)

        actual = range.duration()

        assert actual == duration
