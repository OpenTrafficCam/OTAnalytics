from datetime import datetime
from typing import Any, Optional
from unittest.mock import Mock

from OTAnalytics.application.state import ObservableProperty, TrackViewState
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement


def observable(value: Any) -> Mock:
    observable_property = Mock(spec=ObservableProperty)
    observable_property.get.return_value = value
    return observable_property


def create_filter_element(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Mock:
    filter_element = Mock(spec=FilterElement)
    filter_element.date_range = DateRange(start_date=start_date, end_date=end_date)
    return filter_element


def create_track_view_state(
    filter_element: FilterElement, filter_date_active: bool
) -> Mock:
    state = Mock(spec=TrackViewState)
    state.filter_element = observable(filter_element)
    state.filter_date_active = observable(filter_date_active)
    return state
