from datetime import datetime
from unittest.mock import Mock

from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import (
    Filter,
    FilterBuilder,
    FilterElement,
    FilterElementSettingRestorer,
)


class TestFilterElement:
    def test_init(self) -> None:
        date_range = Mock(spec=DateRange)

        filter_element = FilterElement(date_range, set())

        assert filter_element.date_range == date_range
        assert filter_element.classifications == set()

    def test_build_filter(self) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = None
        date_range = DateRange(start_date, end_date)
        classifications = {"car", "truck"}

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
        filter_builder.add_ends_before_or_at_date_predicate.assert_not_called()
        assert expected_filter == result

    def test_derive_methods(self) -> None:
        date_range = Mock(spec=DateRange)
        classifications = {"car"}
        new_date_range = Mock(spec=DateRange)
        new_classifications = {"car", "truck"}

        filter_element = FilterElement(date_range, classifications)

        updated_filter_element = filter_element.derive_date(new_date_range)
        assert updated_filter_element.date_range == new_date_range
        assert updated_filter_element.classifications == classifications

        updated_filter_element = updated_filter_element.derive_classifications(
            new_classifications
        )
        assert updated_filter_element.date_range == new_date_range
        assert updated_filter_element.classifications == new_classifications


class TestFilterElementSettingRestorer:
    def test_save_by_date_filter_setting(self) -> None:
        filter_element = FilterElement(DateRange(None, None), {"car"})
        restorer = FilterElementSettingRestorer()
        restorer.save_by_date_filter_setting(filter_element)

        assert restorer._by_class_filter_setting is None
        assert restorer._by_date_filter_setting == filter_element.date_range

    def test_by_classification_filter_setting(self) -> None:
        filter_element = FilterElement(DateRange(None, None), {"car"})
        restorer = FilterElementSettingRestorer()
        restorer.save_by_class_filter_setting(filter_element)

        assert restorer._by_class_filter_setting == {"car"}
        assert restorer._by_date_filter_setting is None

    def test_restore_by_date_filter_setting(self) -> None:
        date_range = DateRange(datetime(2000, 1, 1), datetime(2000, 1, 2))
        filter_element = FilterElement(date_range, set())

        restorer = FilterElementSettingRestorer()
        restorer.save_by_date_filter_setting(filter_element)

        restored_filter_element = restorer.restore_by_date_filter_setting(
            FilterElement(DateRange(None, None), {"car"})
        )
        assert restored_filter_element.classifications == {"car"}
        assert restored_filter_element.date_range == date_range

    def test_restore_by_classification_filter_setting(self) -> None:
        date_range = DateRange(datetime(2000, 1, 1), datetime(2000, 1, 2))
        classifications = {"car"}
        filter_element = FilterElement(date_range, classifications)
        restorer = FilterElementSettingRestorer()
        restorer.save_by_class_filter_setting(filter_element)

        restored_filter_element = restorer.restore_by_class_filter_setting(
            FilterElement(DateRange(None, None), set())
        )
        assert restored_filter_element.classifications == classifications
        assert restored_filter_element.date_range == DateRange(None, None)
