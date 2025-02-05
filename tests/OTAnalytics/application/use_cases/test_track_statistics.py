from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
    TracksIntersectingAllNonCuttingSections,
)
from OTAnalytics.application.use_cases.inside_cutting_section import (
    TrackIdsInsideCuttingSections,
)
from OTAnalytics.application.use_cases.number_of_tracks_to_be_validated import (
    NumberOfTracksToBeValidated,
)
from OTAnalytics.application.use_cases.track_statistics import CalculateTrackStatistics
from OTAnalytics.domain.track import TrackId, TrackIdProvider

CUTTING_SECTION_NAME: str = "#clicut 0815"
NUMBER_OF_TRACKS_TO_BE_VALIDATED = 23


@pytest.fixture
def intersection_all_non_cutting_sections() -> Mock:
    return Mock(spec=TracksIntersectingAllNonCuttingSections)


@pytest.fixture
def assigned_to_all_flows() -> Mock:
    return Mock(spec=TracksAssignedToAllFlows)


@pytest.fixture
def all_track_ids() -> Mock:
    return Mock(spec=TrackIdProvider)


@pytest.fixture
def track_ids_inside_cutting_sections() -> Mock:
    return Mock(spec=TrackIdsInsideCuttingSections)


@pytest.fixture
def number_of_tracks_to_be_validated() -> Mock:
    return Mock(spec=NumberOfTracksToBeValidated)


@pytest.fixture
def given_number_of_tracks_to_be_validated() -> Mock:
    given = Mock()
    given.calculate.return_value = NUMBER_OF_TRACKS_TO_BE_VALIDATED
    return given


@pytest.fixture
def given_enter_section_events() -> Mock:
    given = Mock()
    given.get.return_value = []
    return given


def create_trackids_set_with_list_of_ids(ids: list[str]) -> set[TrackId]:
    return set([TrackId(id) for id in ids])


class TestCalculateTrackStatistics:
    def test_get_statistics(
        self,
        intersection_all_non_cutting_sections: Mock,
        assigned_to_all_flows: Mock,
        all_track_ids: Mock,
        track_ids_inside_cutting_sections: Mock,
        given_number_of_tracks_to_be_validated: Mock,
        given_enter_section_events: Mock,
    ) -> None:
        intersection_all_non_cutting_sections.get_ids.return_value = (
            create_trackids_set_with_list_of_ids(
                ["1", "2", "3", "4", "5", "6", "7", "8", "10"]
            )
        )
        assigned_to_all_flows.get_ids.return_value = (
            create_trackids_set_with_list_of_ids(["1", "2", "3", "4", "5"])
        )
        all_track_ids.get_ids.return_value = create_trackids_set_with_list_of_ids(
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        )
        track_ids_inside_cutting_sections.get_ids.return_value = (
            create_trackids_set_with_list_of_ids(
                ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            )
        )
        calculator = CalculateTrackStatistics(
            intersection_all_non_cutting_sections,
            assigned_to_all_flows,
            all_track_ids,
            track_ids_inside_cutting_sections,
            given_number_of_tracks_to_be_validated,
            given_enter_section_events,
        )

        trackStatistics = calculator.get_statistics()

        assert trackStatistics.track_count == 10
        assert (
            trackStatistics.track_count
            == trackStatistics.track_count_outside + trackStatistics.track_count_inside
        )
        assert trackStatistics.track_count_outside == 1
        assert trackStatistics.track_count_inside == 9
        assert trackStatistics.track_count_inside_not_intersecting == 1
        assert trackStatistics.track_count_inside_intersecting_but_unassigned == 3
        assert trackStatistics.track_count_inside_assigned == 5
        assert trackStatistics.percentage_inside_assigned == 5.0 / 9
        assert (
            trackStatistics.number_of_tracks_to_be_validated
            == NUMBER_OF_TRACKS_TO_BE_VALIDATED
        )
        given_number_of_tracks_to_be_validated.calculate.assert_called_once()
        assert trackStatistics.number_of_tracks_with_simultaneous_section_events == 0

    def test_get_number_of_tracks_with_simultaneous_events_while_simultaneous_events(
        self,
        intersection_all_non_cutting_sections: Mock,
        assigned_to_all_flows: Mock,
        all_track_ids: Mock,
        track_ids_inside_cutting_sections: Mock,
        number_of_tracks_to_be_validated: Mock,
    ) -> None:
        event1 = Mock()
        event1.road_user_id = "1"
        event1.occurrence = datetime(2024, 12, 18, 9, 0, 17, 4)
        event2 = Mock()
        event2.road_user_id = "2"
        event2.occurrence = datetime(2024, 12, 18, 9, 0, 23, 4)
        event3 = Mock()
        event3.road_user_id = "2"
        event3.occurrence = datetime(2024, 12, 18, 9, 0, 23, 4)
        event4 = Mock()
        event4.road_user_id = "2"
        event4.occurrence = datetime(2024, 12, 18, 10, 0, 21, 0)
        event5 = Mock()
        event5.road_user_id = "3"
        event5.occurrence = datetime(2024, 12, 18, 10, 0, 21, 0)

        get_all_enter_section_events = Mock()
        get_all_enter_section_events.get.return_value = [
            event1,
            event2,
            event3,
            event4,
            event5,
        ]

        calculator = CalculateTrackStatistics(
            intersection_all_non_cutting_sections,
            assigned_to_all_flows,
            all_track_ids,
            track_ids_inside_cutting_sections,
            number_of_tracks_to_be_validated,
            get_all_enter_section_events,
        )

        simultaneous_event_count = (
            calculator.get_number_of_tracks_with_simultaneous_events()
        )

        assert simultaneous_event_count == 1
