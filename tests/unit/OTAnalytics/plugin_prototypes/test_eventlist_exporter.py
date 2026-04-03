from dataclasses import dataclass

import pytest

from OTAnalytics.application.export_formats import event_list
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    EventListDataFrameBuilder,
)
from tests.utils.builders.event_builder import EventBuilder


@dataclass
class EventListGiven:
    """Holds event lists for export geo coordinate tests."""

    events_with_geo: list
    events_without_geo: list
    events_empty: list


def create_event_list_given() -> EventListGiven:
    """Create test fixtures for event list export geo coordinate tests."""
    builder_with = EventBuilder(geo_x=449210.0, geo_y=5699310.0)
    builder_with.append_section_event()
    builder_without = EventBuilder()
    builder_without.append_section_event()
    return EventListGiven(
        events_with_geo=builder_with.build_events(),
        events_without_geo=builder_without.build_events(),
        events_empty=[],
    )


def setup_default(given: EventListGiven) -> EventListGiven:
    """Return given unchanged (no default setup needed)."""
    return given


def create_target_with_geo(given: EventListGiven) -> EventListDataFrameBuilder:
    """Create builder from events that carry geo coordinates."""
    return EventListDataFrameBuilder(given.events_with_geo, [])


def create_target_without_geo(given: EventListGiven) -> EventListDataFrameBuilder:
    """Create builder from events without geo coordinates."""
    return EventListDataFrameBuilder(given.events_without_geo, [])


def create_target_empty(given: EventListGiven) -> EventListDataFrameBuilder:
    """Create builder from empty event list."""
    return EventListDataFrameBuilder(given.events_empty, [])


class TestEventListDataFrameBuilder:
    def test_build_no_events(self) -> None:
        """
        Supporting test case for bug OP#9023
        """
        builder = EventListDataFrameBuilder([], [])

        actual = builder.build()

        assert actual.empty


class TestEventListDataFrameBuilderGeoCoordinates:
    """Tests for geo coordinate columns in EventListDataFrameBuilder.build()."""

    def test_build_no_events(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_empty(given)
        assert target.build().empty

    def test_geo_columns_present_when_events_have_geo(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_with_geo(given)
        df = target.build()
        assert event_list.GEO_X in df.columns
        assert event_list.GEO_Y in df.columns

    def test_geo_x_value_correct(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_with_geo(given)
        df = target.build()
        assert df[event_list.GEO_X].iloc[0] == pytest.approx(449210.0, abs=0.001)

    def test_geo_y_value_correct(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_with_geo(given)
        df = target.build()
        assert df[event_list.GEO_Y].iloc[0] == pytest.approx(5699310.0, abs=0.001)

    def test_geo_columns_absent_when_events_have_no_geo(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_without_geo(given)
        df = target.build()
        assert event_list.GEO_X not in df.columns
        assert event_list.GEO_Y not in df.columns
