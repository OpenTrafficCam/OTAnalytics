from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackStatisticKeys,
)
from OTAnalytics.application.use_cases.track_statistics import TrackStatistics
from OTAnalytics.plugin_ui.nicegui_gui.pages.track_statistics_form.container import (
    COLUMN_NAME,
    COLUMN_NUMBER,
    map_to_ui,
)


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
