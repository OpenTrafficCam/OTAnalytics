from unittest.mock import Mock

import pytest

from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)
from tests.utils.builders.track_builder import TrackBuilder


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
        track_dataset = Mock()
        track_dataset.intersecting_tracks.return_value = {track.id}
        get_all_tracks = Mock()
        get_all_tracks.as_dataset.return_value = track_dataset

        section = Mock(spec=Section)
        section.id = SectionId("section-1")
        section.name = "south"

        tracks_intersecting_sections = SimpleTracksIntersectingSections(
            get_all_tracks,
        )
        intersecting = tracks_intersecting_sections([section])

        assert intersecting == {section.id: {track.id}}
        get_all_tracks.as_dataset.assert_called_once()
