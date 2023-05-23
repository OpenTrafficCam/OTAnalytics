from datetime import datetime
from unittest.mock import Mock

from OTAnalytics.application.analysis import RunSceneEventDetection, RunTrafficCounting
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.types import EventType


class TestRunSceneEventDetection:
    def test_init(self) -> None:
        scene_action_detector = Mock(spec=SceneActionDetector)
        run_scene_event_detection = RunSceneEventDetection(scene_action_detector)

        assert run_scene_event_detection._scene_action_detector == scene_action_detector

    def test_run(self) -> None:
        track = Mock(spec=Track)
        scene_action_detector = Mock(spec=SceneActionDetector)
        mock_event = Mock(spec=Event)
        scene_action_detector.detect.return_value = [mock_event]

        run_scene_event_detection = RunSceneEventDetection(scene_action_detector)
        events = run_scene_event_detection.run([track])

        scene_action_detector.detect.assert_called_once()
        assert events == [mock_event]


def create_event(
    track_id: TrackId,
    section: SectionId,
) -> Event:
    return Event(
        road_user_id=track_id.id,
        road_user_type="car",
        hostname="my_hostname",
        occurrence=datetime(2020, 1, 1, 0, 0, 0),
        frame_number=1,
        section_id=section,
        event_coordinate=ImageCoordinate(0, 0),
        event_type=EventType.SECTION_ENTER,
        direction_vector=DirectionVector2D(x1=1, x2=1),
        video_name="my_video_name.mp4",
    )


class TestRunTrafficCounting:
    def test_run(self) -> None:
        first_track = TrackId(1)
        second_track = TrackId(2)
        third_track = TrackId(3)
        forth_track = TrackId(4)
        fifth_track = TrackId(5)
        sixth_track = TrackId(6)
        south_section_id = SectionId("south")
        north_section_id = SectionId("north")
        west_section_id = SectionId("west")
        south_section = Mock(spec=Section)
        north_section = Mock(spec=Section)
        west_section = Mock(spec=Section)
        south_section.id = south_section_id
        north_section.id = north_section_id
        west_section.id = west_section_id
        south_to_north_id = FlowId("south to north")
        south_to_north = Flow(
            south_to_north_id,
            start=south_section,
            end=north_section,
            distance=10,
        )
        south_to_west_id = FlowId("south to west")
        south_to_west = Flow(
            south_to_west_id,
            start=south_section,
            end=west_section,
            distance=11,
        )
        north_to_south_id = FlowId("north to south")
        north_to_south = Flow(
            north_to_south_id,
            start=north_section,
            end=south_section,
            distance=10,
        )
        events: list[Event] = [
            create_event(first_track, south_section_id),
            create_event(second_track, south_section_id),
            create_event(third_track, south_section_id),
            create_event(forth_track, south_section_id),
            create_event(fifth_track, north_section_id),
            create_event(sixth_track, north_section_id),
            create_event(first_track, north_section_id),
            create_event(first_track, west_section_id),
            create_event(second_track, west_section_id),
            create_event(third_track, west_section_id),
            create_event(forth_track, west_section_id),
            create_event(fifth_track, south_section_id),
            create_event(sixth_track, south_section_id),
        ]
        flows: list[Flow] = [south_to_north, south_to_west, north_to_south]

        expected_result = {
            south_to_north_id: 0,
            north_to_south_id: 2,
            south_to_west_id: 4,
        }

        analysis = RunTrafficCounting()
        result = analysis.run(events, flows)

        assert result == expected_result
