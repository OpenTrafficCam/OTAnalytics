from unittest.mock import Mock

from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import Filter, FilterBuilder, FilterElement


class TestFilterElement:
    def test_init(self) -> None:
        date_range = Mock(spec=DateRange)

        filter_element = FilterElement(date_range, [])

        assert filter_element.date_range == date_range
        assert filter_element.classifications == []

    def test_build_filter(self) -> None:
        start_date = Mock()
        end_date = Mock()
        date_range = DateRange(start_date, end_date)
        classifications = ["car", "truck"]

        expected_filter = Mock(spec=Filter)

        filter_builder = Mock(spec=FilterBuilder)
        filter_builder.get_result.return_value = expected_filter

        filter_element = FilterElement(date_range, classifications)
        result = filter_element.build_filter(filter_builder)

        filter_builder.build.assert_called_once()
        filter_builder.get_result.assert_called_once()
        filter_builder.add_has_classifications_predicate.assert_called_once_with(
            classifications
        )
        filter_builder.add_starts_at_or_after_date_predicate.assert_called_once_with(
            start_date
        )
        filter_builder.add_ends_before_or_at_date_predicate.assert_called_once_with(
            end_date
        )
        assert expected_filter == result
