from unittest.mock import Mock

from OTAnalytics.domain.filter import Filter, FilterBuilder, FilterElement


class TestFilterElement:
    def test_init(self) -> None:
        start_date = Mock()
        end_date = Mock()

        filter_element = FilterElement(start_date, end_date, [])

        assert filter_element.start_date == start_date
        assert filter_element.end_date == end_date
        assert filter_element.classifications == []

    def test_build_filter(self) -> None:
        start_date = Mock()
        end_date = Mock()
        classifications = ["car", "truck"]

        expected_filter = Mock(spec=Filter)

        filter_builder = Mock(spec=FilterBuilder)
        filter_builder.build.return_value = expected_filter

        filter_element = FilterElement(start_date, end_date, classifications)
        result = filter_element.build_filter(filter_builder)

        filter_builder.build.assert_called_once()
        filter_builder.add_has_classifications_predicate.assert_called_once_with(
            classifications
        )
        filter_builder.add_starts_at_or_after_date_predicate.assert_called_once_with(
            start_date
        )
        assert expected_filter == result
