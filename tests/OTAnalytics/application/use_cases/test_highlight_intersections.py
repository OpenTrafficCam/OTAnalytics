from datetime import datetime
from unittest.mock import Mock, PropertyMock, call, patch

import pytest

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting import (
    EventPair,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.state import (
    FlowState,
    ObservableProperty,
    SectionState,
    TrackViewState,
)
from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
    TracksAssignedToSelectedFlows,
    TracksIntersectingGivenSections,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
    TracksOverlapOccurrenceWindow,
)
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackId,
    TrackIdProvider,
    TrackRepository,
)


class TestTracksIntersectingSelectedSections:
    def test_get_ids(self) -> None:
        track_id = TrackId("2")
        section_id = Mock(spec=SectionId)
        section = Mock(spec=Section)
        section.id = section_id

        section_state = Mock(spec=SectionState)
        selected_sections = Mock(spec=ObservableProperty)
        selected_sections.get.return_value = [section_id]
        section_state.selected_sections = selected_sections

        get_section_by_id = Mock(spec=GetSectionsById)
        get_section_by_id.return_value = [section]
        tracks_intersecting_sections = Mock(spec=TracksIntersectingSections)
        tracks_intersecting_sections.return_value = [track_id]

        tracks_intersecting_selected_sections = TracksIntersectingSelectedSections(
            section_state, tracks_intersecting_sections, get_section_by_id
        )
        track_ids = list(tracks_intersecting_selected_sections.get_ids())

        assert track_ids == [track_id]
        section_state.selected_sections.get.assert_called_once()
        get_section_by_id.assert_called_once_with([section_id])
        tracks_intersecting_sections.assert_called_once_with([section])


class TestTracksIntersectingGivenSections:
    def test_get_ids(self) -> None:
        section_id_1 = SectionId("section-1")
        section_ids = [section_id_1]
        section_1 = Mock(spec=Section)
        section_1.id = section_id_1
        sections = [section_1]
        section_1_tracks = {TrackId("track-1")}
        original_track_ids = {section_id_1: section_1_tracks}
        tracks_intersecting_sections = Mock(spec=TracksIntersectingSections)
        get_section_by_id = Mock(spec=GetSectionsById)
        intersection_repository = Mock(spec=IntersectionRepository)
        intersection_repository.get.return_value = {}
        get_section_by_id.return_value = sections
        tracks_intersecting_sections.return_value = original_track_ids
        provider = TracksIntersectingGivenSections(
            section_ids,
            tracks_intersecting_sections,
            get_section_by_id,
            intersection_repository,
        )

        track_ids = provider.get_ids()

        assert track_ids == section_1_tracks
        get_section_by_id.assert_called_once_with(section_ids)
        tracks_intersecting_sections.assert_called_once_with(sections)
        intersection_repository.store.assert_called_once_with(original_track_ids)


class TestTracksNotIntersectingSelection:
    def test_get_ids(self) -> None:
        first_track_id = TrackId("1")
        second_track_id = TrackId("2")
        first_track = Mock(spec=Track)
        first_track.id = first_track_id
        second_track = Mock(spec=Track)
        second_track.id = second_track_id
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_all.return_value = [first_track, second_track]

        tracks_intersecting_sections = Mock(spec=TrackIdProvider)
        tracks_intersecting_sections.get_ids.return_value = {first_track_id}

        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_sections, track_repository
        )
        track_ids = list(tracks_not_intersecting_sections.get_ids())

        assert track_ids == [second_track_id]
        track_repository.get_all.assert_called_once()
        tracks_intersecting_sections.get_ids.assert_called_once()

    def test_no_selection_returns_all_tracks(self) -> None:
        first_track_id = TrackId("1")
        second_track_id = TrackId("2")
        first_track = Mock(spec=Track)
        first_track.id = first_track_id
        second_track = Mock(spec=Track)
        second_track.id = second_track_id
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_all.return_value = [first_track, second_track]

        tracks_intersecting_sections = Mock(spec=TrackIdProvider)
        tracks_intersecting_sections.get_ids.return_value = {}

        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_sections, track_repository
        )
        track_ids = tracks_not_intersecting_sections.get_ids()

        assert set(track_ids) == {first_track_id, second_track_id}
        track_repository.get_all.assert_called_once()
        tracks_intersecting_sections.get_ids.assert_called_once()


class TestTracksAssignedToSelectedFlows:
    def test_get_ids(self) -> None:
        first_flow_id = FlowId("North-South")
        first_flow = Mock(spec=Flow)
        first_flow.id = first_flow_id

        second_flow_id = FlowId("North-West")
        second_flow = Mock(spec=Flow)
        second_flow.id = second_flow_id

        selected_flows = Mock(spec=ObservableProperty)
        selected_flows.get.return_value = [first_flow_id]
        flow_state = Mock(spec=FlowState)
        flow_state.selected_flows = selected_flows

        first_assignment = RoadUserAssignment("1", first_flow, Mock(spec=EventPair))
        second_assignment = RoadUserAssignment("2", second_flow, Mock(spec=EventPair))
        assignments = Mock(spec=RoadUserAssignments)
        assignments.as_list.return_value = [first_assignment, second_assignment]
        assigner = Mock(spec=RoadUserAssigner)
        assigner.assign.return_value = assignments

        event = Mock(spec=Event)
        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = [event]

        flow_repository = Mock(spec=FlowRepository)
        flow_repository.get_all.return_value = [first_flow, second_flow]

        tracks_assigned_to_flow = TracksAssignedToSelectedFlows(
            assigner, event_repository, flow_repository, flow_state
        )
        track_ids = list(tracks_assigned_to_flow.get_ids())

        assert track_ids == [TrackId("1")]
        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        assert selected_flows.get.call_count == 2
        assigner.assign.assert_called_once_with([event], [first_flow, second_flow])
        assignments.as_list.assert_called_once()


class TestTracksOverlapOccurrenceWindow:
    @pytest.mark.parametrize(
        "start_1,end_1,start_2,end_2,expected",
        [
            (
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
                datetime(2020, 1, 1, 14, 30),
                datetime(2020, 1, 1, 15),
                False,
            ),
            (
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 13, 30),
                True,
            ),
            (
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
                datetime(2020, 1, 1, 13, 30),
                datetime(2020, 1, 1, 14),
                True,
            ),
            (
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
                datetime(2020, 1, 1, 13, 30),
                datetime(2020, 1, 1, 14, 30),
                True,
            ),
            (
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
                datetime(2020, 1, 1, 14, 00),
                datetime(2020, 1, 1, 14, 30),
                True,
            ),
        ],
    )
    def test_has_overlap(
        self,
        start_1: datetime,
        end_1: datetime,
        start_2: datetime,
        end_2: datetime,
        expected: bool,
    ) -> None:
        assert (
            TracksOverlapOccurrenceWindow._has_overlap(start_1, end_1, start_2, end_2)
            == expected
        )
        assert (
            TracksOverlapOccurrenceWindow._has_overlap(start_2, end_2, start_1, end_1)
            == expected
        )

    def test_has_overlap_wrong_order_of_arguments(self) -> None:
        start_1 = datetime(2022, 1, 2)
        start_2 = datetime(2022, 1, 1)
        end_1 = datetime(2022, 1, 3)
        end_2 = datetime(2022, 1, 4)
        with pytest.raises(
            ValueError, match="start_1 needs to be lesser equal than end_1."
        ):
            TracksOverlapOccurrenceWindow._has_overlap(
                start_1,
                start_2,
                end_1,
                end_2,
            )
        with pytest.raises(
            ValueError, match="start_2 needs to be lesser equal than end_2."
        ):
            TracksOverlapOccurrenceWindow._has_overlap(
                start_2,
                start_1,
                end_2,
                end_1,
            )

    def test_get_ids(self) -> None:
        track_repository = Mock(spec=TrackRepository)
        track_view_state = Mock(spec=TrackViewState)
        track_ids = [Mock(spec=TrackId), Mock(spec=TrackId)]
        tracks = [Mock(spec=Track), None]
        track_repository.get_all.return_value = tracks

        with patch.object(
            TracksOverlapOccurrenceWindow, "_filter", return_value=[track_ids[0]]
        ):
            id_provider = TracksOverlapOccurrenceWindow(
                track_repository, track_view_state
            )
            result_ids = id_provider.get_ids()

            assert result_ids == [track_ids[0]]
            track_repository.get_all.assert_called_once()

    def test_get_ids_as_decorator(self) -> None:
        track_repository = Mock(spec=TrackRepository)
        track_view_state = Mock(spec=TrackViewState)
        track_ids = [Mock(spec=TrackId), Mock(spec=TrackId)]
        tracks = [Mock(spec=Track), None]
        track_repository.get_for.side_effect = tracks

        with patch.object(
            TracksOverlapOccurrenceWindow, "_filter", return_value=[track_ids[0]]
        ):
            id_provider = TracksOverlapOccurrenceWindow(
                track_repository, track_view_state
            )
            result_ids = id_provider.get_ids()

            assert result_ids == [track_ids[0]]
            track_repository.get_for.call_args_list == [call(id) for id in track_ids]

    @pytest.mark.parametrize(
        (
            "filter_start,filter_end,"
            "expected_has_overlap_filter_start,expected_has_overlap_filter_end,"
        ),
        [
            (datetime(2020, 1, 1, 13), None, datetime(2020, 1, 1, 13), datetime.max),
            (None, datetime(2020, 1, 1, 14), datetime.min, datetime(2020, 1, 1, 14)),
            (
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
                datetime(2020, 1, 1, 13),
                datetime(2020, 1, 1, 14),
            ),
            (None, None, datetime.min, datetime.max),
        ],
    )
    def test_filter(
        self,
        filter_start: datetime | None,
        filter_end: datetime | None,
        expected_has_overlap_filter_start: datetime,
        expected_has_overlap_filter_end: datetime,
    ) -> None:
        track_repository = Mock(spec=TrackRepository)

        filter_element = Mock(spec=FilterElement)
        filter_element.date_range = DateRange(filter_start, filter_end)

        track_view_state = Mock(spec=TrackViewState)
        observable_property = Mock(spec=ObservableProperty)
        observable_property.get.return_value = filter_element
        track_view_state.filter_element = observable_property

        start_detection = Mock(spec=Detection)
        start_time = datetime(2020, 1, 1, 13)
        start_detection.occurrence = start_time

        end_detection = Mock(spec=Detection)
        end_time = datetime(2020, 1, 1, 13, 30)
        end_detection.occurrence = end_time

        with patch.object(
            TracksOverlapOccurrenceWindow, "_has_overlap", return_value=True
        ) as mock_has_overlap, patch(
            "OTAnalytics.application.use_cases.highlight_intersections.Track.start",
            new_callable=PropertyMock,
            return_value=start_time,
        ) as mock_start, patch(
            "OTAnalytics.application.use_cases.highlight_intersections.Track.end",
            new_callable=PropertyMock,
            return_value=end_time,
        ) as mock_end:
            track_id = TrackId("1")
            track = Mock(spec=Track)
            track.id = track_id
            track.start.return_value = start_detection
            track.end.return_value = end_detection

            id_provider = TracksOverlapOccurrenceWindow(
                track_repository, track_view_state
            )
            result_ids = id_provider._filter([track])

            assert result_ids == [track_id]
            mock_start.assert_called_once()
            mock_end.assert_called_once()
            if filter_start or filter_end:
                mock_has_overlap.assert_called_once_with(
                    expected_has_overlap_filter_start,
                    expected_has_overlap_filter_end,
                    track.start,
                    track.end,
                )
            else:
                mock_has_overlap.assert_not_called()
