from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
    TracksIntersectingAllNonCuttingSections,
)
from OTAnalytics.application.use_cases.inside_cutting_section import (
    TrackIdsInsideCuttingSections,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTrackIds
from OTAnalytics.application.use_cases.track_statistics import CalculateTrackStatistics
from OTAnalytics.domain.track import TrackId

CUTTING_SECTION_NAME: str = "#clicut 0815"
NUMBER_OF_TRACKS_TO_BE_VALIDATED = 23


@pytest.fixture
def intersection_all_non_cutting_sections() -> Mock:
    return Mock(spec=TracksIntersectingAllNonCuttingSections)


@pytest.fixture
def assigned_to_all_flows() -> Mock:
    return Mock(spec=TracksAssignedToAllFlows)


@pytest.fixture
def get_all_track_ids() -> Mock:
    return Mock(spec=GetAllTrackIds)


@pytest.fixture
def track_ids_inside_cutting_sections() -> Mock:
    return Mock(spec=TrackIdsInsideCuttingSections)


@pytest.fixture
def given_number_of_tracks_to_be_validated() -> Mock:
    given = Mock()
    given.calculate.return_value = NUMBER_OF_TRACKS_TO_BE_VALIDATED
    return given


def create_trackids_set_with_list_of_ids(ids: list[str]) -> set[TrackId]:
    return set([TrackId(id) for id in ids])


class TestCalculateTrackStatistics:
    def test_get_statistics(
        self,
        intersection_all_non_cutting_sections: Mock,
        assigned_to_all_flows: Mock,
        get_all_track_ids: Mock,
        track_ids_inside_cutting_sections: Mock,
        given_number_of_tracks_to_be_validated: Mock,
    ) -> None:
        intersection_all_non_cutting_sections.get_ids.return_value = (
            create_trackids_set_with_list_of_ids(
                ["1", "2", "3", "4", "5", "6", "7", "8", "10"]
            )
        )
        assigned_to_all_flows.get_ids.return_value = (
            create_trackids_set_with_list_of_ids(["1", "2", "3", "4", "5"])
        )
        get_all_track_ids.return_value = create_trackids_set_with_list_of_ids(
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        )
        track_ids_inside_cutting_sections.return_value = (
            create_trackids_set_with_list_of_ids(
                ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            )
        )
        calculator = CalculateTrackStatistics(
            intersection_all_non_cutting_sections,
            assigned_to_all_flows,
            get_all_track_ids,
            track_ids_inside_cutting_sections,
            given_number_of_tracks_to_be_validated,
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
