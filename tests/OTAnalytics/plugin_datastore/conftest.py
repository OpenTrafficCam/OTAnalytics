import pytest

from OTAnalytics.domain.track import Track
from tests.conftest import TrackBuilder


@pytest.fixture
def first_track() -> Track:
    track_builder = TrackBuilder()
    _class = "car"

    track_builder.add_track_id("1")
    track_builder.add_track_class(_class)
    track_builder.add_second(1)
    track_builder.add_frame(1)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(2)
    track_builder.add_frame(2)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def first_track_continuing() -> Track:
    track_builder = TrackBuilder()
    _class = "truck"
    track_builder.add_track_id("1")
    track_builder.add_track_class(_class)
    track_builder.add_second(3)
    track_builder.add_frame(3)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(4)
    track_builder.add_frame(4)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(5)
    track_builder.add_frame(5)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def second_track() -> Track:
    track_builder = TrackBuilder()
    _class = "pedestrian"
    track_builder.add_track_id("2")
    track_builder.add_track_class(_class)
    track_builder.add_second(1)
    track_builder.add_frame(1)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(2)
    track_builder.add_frame(2)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(3)
    track_builder.add_frame(3)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    return track_builder.build_track()
