from unittest.mock import Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackStatisticKeys,
)
from OTAnalytics.application.use_cases.track_statistics import TrackStatistics
from OTAnalytics.plugin_ui.nicegui_gui.pages.track_statistics_form.container import (
    COLUMN_NAME,
    COLUMN_NUMBER,
    MARKER_TRACK_STATISTICS,
    TrackStatisticForm,
    map_to_ui,
)

LABEL_ALL = TrackStatisticKeys.LABEL_ALL_TRACKS
LABEL_ASSIGNED = TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS


def create_track_statistics() -> TrackStatistics:
    return TrackStatistics(
        track_count=101,
        track_count_outside=2,
        track_count_inside=99,
        track_count_inside_not_intersecting=13,
        track_count_inside_intersecting_but_unassigned=17,
        track_count_inside_assigned=69,
        percentage_inside_assigned=0.6969,
        percentage_inside_not_intersection=0.1313,
        percentage_inside_intersecting_but_unassigned=0.1717,
        number_of_tracks_to_be_validated=23,
        number_of_tracks_with_simultaneous_section_events=29,
    )


class TestMapToUi:
    def test_rows_show_label_and_value_in_order_of_desktop_gui(self) -> None:
        resource_manager = ResourceManager()

        actual = map_to_ui(resource_manager, create_track_statistics())

        expected = [
            (TrackStatisticKeys.LABEL_ALL_TRACKS, "101"),
            (TrackStatisticKeys.LABEL_INSIDE_CUTTING_SECTIONS, "99"),
            (TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS, "69 (69.7%)"),
            (TrackStatisticKeys.LABEL_TRACKS_NOT_INTERSECTING_SECTIONS, "13 (13.1%)"),
            (TrackStatisticKeys.LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED, "17 (17.2%)"),
            (TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED, "23"),
            (
                TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS,  # noqa
                "29",
            ),
        ]
        assert actual == [
            {COLUMN_NAME: resource_manager.get(key), COLUMN_NUMBER: value}
            for key, value in expected
        ]


ENDPOINT = "/test-track-statistics"


def value_of(user: User, label: str) -> str:
    """The text right of the given label in the status bar."""
    label_element = user.find(kind=ui.label, content=label).elements.pop()
    assert label_element.parent_slot is not None
    siblings = label_element.parent_slot.children
    value = siblings[siblings.index(label_element) + 1]
    assert isinstance(value, ui.label)
    return value.text


class TestTrackStatisticForm:
    async def test_shows_statistics_in_one_row(self, user: User) -> None:
        resource_manager = ResourceManager()
        target = TrackStatisticForm(resource_manager, Mock())

        @ui.page(ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT)

        status_bar = user.find(marker=MARKER_TRACK_STATISTICS).elements.pop()
        assert isinstance(status_bar, ui.row)
        assert "ota-stats" in status_bar.classes
        await user.should_not_see(kind=ui.table)
        assert value_of(user, resource_manager.get(LABEL_ALL)) == "0"

    async def test_update_changes_the_values(self, user: User) -> None:
        resource_manager = ResourceManager()
        target = TrackStatisticForm(resource_manager, Mock())

        @ui.page(ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT)
        target.update_track_statistics(create_track_statistics())

        assert value_of(user, resource_manager.get(LABEL_ALL)) == "101"
        assert value_of(user, resource_manager.get(LABEL_ASSIGNED)) == "69 (69.7%)"

    async def test_statistics_updated_before_build_are_shown(self, user: User) -> None:
        resource_manager = ResourceManager()
        target = TrackStatisticForm(resource_manager, Mock())
        target.update_track_statistics(create_track_statistics())

        @ui.page(ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT)

        assert value_of(user, resource_manager.get(LABEL_ALL)) == "101"

    async def test_starts_with_a_title(self, user: User) -> None:
        resource_manager = ResourceManager()
        target = TrackStatisticForm(resource_manager, Mock())

        @ui.page(ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT)

        status_bar = user.find(marker=MARKER_TRACK_STATISTICS).elements.pop()
        first = status_bar.default_slot.children[0]
        assert isinstance(first, ui.label)
        assert first.text == resource_manager.get(
            TrackStatisticKeys.LABEL_TRACK_STATISTIC_FORM_HEADER
        )
        assert "ota-stats-title" in first.classes
