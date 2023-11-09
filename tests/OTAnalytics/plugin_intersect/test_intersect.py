from unittest.mock import Mock

import pytest

from OTAnalytics.application.geometry import (
    SectionGeometryBuilder,
    TrackGeometryBuilder,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.event import EventType
from OTAnalytics.domain.geometry import Line, RelativeOffsetCoordinate
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)
from tests.conftest import TrackBuilder


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    classification = "car"
    track_id = "1"

    track_builder.add_track_class(classification)
    track_builder.add_detection_class(classification)
    track_builder.add_track_id(track_id)
    track_builder.add_wh_bbox(15.3, 30.5)

    track_builder.add_frame(1)
    track_builder.add_second(0)
    track_builder.add_xy_bbox(0.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(2)
    track_builder.add_second(1)
    track_builder.add_xy_bbox(10.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(3)
    track_builder.add_second(2)
    track_builder.add_xy_bbox(15.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(3)
    track_builder.add_xy_bbox(20.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(4)
    track_builder.add_xy_bbox(25.0, 5.0)
    track_builder.append_detection()
    return track_builder.build_track()


class TestSimpleTracksIntersectingSections:
    def test_tracks_intersecting_sections(self, track: Track) -> None:
        get_all_tracks = Mock(spec=GetAllTracks)
        get_all_tracks.return_value = [track]

        section = Mock(spec=Section)
        offset = RelativeOffsetCoordinate(0, 0)
        section.get_offset.return_value = offset
        section.name = "south"

        intersect_implementation = Mock(spec=IntersectImplementation)
        intersect_implementation.line_intersects_line.return_value = True

        section_geom = Mock(spec=Line)
        track_geom = Mock(spec=Line)

        track_geometry_builder = Mock(spec=TrackGeometryBuilder)
        track_geometry_builder.build.return_value = track_geom
        section_geometry_builder = Mock(spec=SectionGeometryBuilder)
        section_geometry_builder.build_as_line.return_value = section_geom

        tracks_intersecting_sections = SimpleTracksIntersectingSections(
            get_all_tracks,
            intersect_implementation,
            track_geometry_builder,
            section_geometry_builder,
        )
        intersecting = tracks_intersecting_sections([section])

        assert intersecting == {track.id}
        get_all_tracks.assert_called_once()
        section.get_offset.assert_called_once_with(EventType.SECTION_ENTER)
        track_geometry_builder.build.assert_called_once_with(track, offset)
        section_geometry_builder.build_as_line.assert_called_once_with(section)
        intersect_implementation.line_intersects_line.assert_called_once_with(
            track_geom, section_geom
        )
