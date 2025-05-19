import shutil
from pathlib import Path
from typing import Any, Generator, Sequence, TypeVar
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    EventPair,
    RoadUserAssignment,
)
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.section import LineSection, Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasByMaxConfidence
from OTAnalytics.plugin_parser.otconfig_parser import OtConfigFormatFixer
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    OtFlowParser,
    OttrkParser,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from tests.utils.builders.event_builder import EventBuilder
from tests.utils.builders.track_builder import TrackBuilder, create_track
from tests.utils.builders.track_segment_builder import (
    PANDAS,
    PYTHON,
    TrackSegmentDatasetBuilder,
    TrackSegmentDatasetBuilderProvider,
)

pytest_plugins = ["nicegui.testing.user_plugin"]

T = TypeVar("T")
YieldFixture = Generator[T, None, None]


@pytest.fixture(scope="module")
def test_data_tmp_dir() -> YieldFixture[Path]:
    test_data_tmp_dir = Path(__file__).parent / "data_tmp"
    test_data_tmp_dir.mkdir(exist_ok=True)
    yield test_data_tmp_dir
    shutil.rmtree(test_data_tmp_dir)


@pytest.fixture(scope="module")
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def ottrk_path(test_data_dir: Path) -> Path:
    name = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"
    return test_data_dir / name


@pytest.fixture(scope="module")
def otsection_file(test_data_dir: Path) -> Path:
    name = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otflow"
    return test_data_dir / name


@pytest.fixture(scope="module")
def cyclist_video(test_data_dir: Path) -> Path:
    name = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
    return test_data_dir / name


@pytest.fixture(scope="module")
def otconfig_file(test_data_dir: Path) -> Path:
    name = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otconfig"
    return test_data_dir / name


def do_nothing(arg: Any) -> Any:
    return arg


@pytest.fixture(scope="module")
def do_nothing_fixer() -> Mock:
    fixer = Mock(spec=OtConfigFormatFixer)
    fixer.fix.side_effect = do_nothing
    return fixer


@pytest.fixture(scope="module")
def tracks(ottrk_path: Path) -> list[Track]:
    calculator = PandasByMaxConfidence()
    detection_parser = PandasDetectionParser(
        calculator,
        ShapelyTrackGeometryDataset.from_track_dataset,
        track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
    )
    return OttrkParser(detection_parser).parse(ottrk_path).tracks.as_list()
    # ottrk_parser = OttrkParser(
    #     ByMaxConfidence(),
    #     TrackRepository(),
    #     TrackFileRepository(),
    #     TRACK_LENGTH_LIMIT,
    # )
    # return ottrk_parser.parse(ottrk_path)


@pytest.fixture(scope="module")
def sections(otsection_file: Path) -> Sequence[Section]:
    flow_parser = OtFlowParser()
    return flow_parser.parse(otsection_file)[0]


@pytest.fixture
def track_builder() -> TrackBuilder:
    return TrackBuilder()


@pytest.fixture
def event_builder() -> EventBuilder:
    return EventBuilder()


@pytest.fixture
def straight_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("straight-track")
    track_builder.add_wh_bbox(0.5, 0.5)
    track_builder.add_xy_bbox(1.0, 1.0)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2.0, 1.0)
    track_builder.add_frame(2)
    track_builder.add_microsecond(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3.0, 1.0)
    track_builder.add_frame(3)
    track_builder.add_microsecond(2)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def complex_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("complex-track")
    track_builder.add_xy_bbox(1.0, 1.0)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2.0, 1.0)
    track_builder.add_frame(2)
    track_builder.add_microsecond(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2.0, 1.5)
    track_builder.add_frame(3)
    track_builder.add_microsecond(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(1.0, 1.5)
    track_builder.add_frame(4)
    track_builder.add_microsecond(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(1.0, 2.0)
    track_builder.add_frame(5)
    track_builder.add_microsecond(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2.0, 2.0)
    track_builder.add_frame(5)
    track_builder.add_microsecond(4)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def closed_track() -> Track:
    classification = "car"
    track_builder = TrackBuilder()
    track_builder.add_track_id("closed-track")
    track_builder.add_track_class(classification)
    track_builder.add_detection_class(classification)

    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.add_xy_bbox(1.0, 1.0)
    track_builder.append_detection()

    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.add_xy_bbox(2.0, 1.0)
    track_builder.append_detection()

    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.add_xy_bbox(2.0, 2.0)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.add_xy_bbox(1.0, 2.0)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.add_xy_bbox(1.0, 1.0)
    track_builder.append_detection()
    return track_builder.build_track()


@pytest.fixture
def car_track() -> Track:
    return create_track(
        "1", [(1, 1), (2, 2)], 1, OtcClasses.CAR, confidences=[0.6, 0.8]
    )


@pytest.fixture
def car_track_continuing() -> Track:
    return create_track("1", [(3, 3), (4, 4), (5, 5)], 3, OtcClasses.TRUCK)


@pytest.fixture
def pedestrian_track() -> Track:
    return create_track(
        "2",
        [(1, 1), (2, 2), (3, 3)],
        1,
        OtcClasses.PEDESTRIAN,
        confidences=[0.9, 0.8, 0.7],
    )


@pytest.fixture
def bicycle_track() -> Track:
    return create_track("3", [(1, 1), (2, 2), (3, 3)], 4, OtcClasses.BICYCLIST)


@pytest.fixture
def cargo_bike_track() -> Track:
    return create_track("4", [(1, 1), (2, 2), (3, 3)], 4, OtcClasses.CARGO_BIKE_DRIVER)


@pytest.fixture
def single_detection_track() -> Track:
    return create_track("5", [(2, 2)], 1, OtcClasses.CAR, confidences=[0.8])


@pytest.fixture
def all_tracks(
    car_track: Track,
    pedestrian_track: Track,
    bicycle_track: Track,
    cargo_bike_track: Track,
) -> list[Track]:
    return [car_track, pedestrian_track, bicycle_track, cargo_bike_track]


@pytest.fixture
def track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    return ShapelyTrackGeometryDataset.from_track_dataset


@pytest.fixture
def cutting_section_test_case() -> (
    tuple[LineSection, list[Track], list[Track], set[TrackId]]
):
    track_id_1 = "1"
    track_id_2 = "2"
    track_id_3 = "3"

    first_track = create_track(
        track_id=track_id_1,
        original_id=track_id_1,
        coord=[(1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (3, 2), (2, 2), (1, 2)],
        start_second=1,
    )
    expected_first_track_1 = create_track(
        track_id="1_0",
        original_id=track_id_1,
        coord=[
            (1, 1),
            (2, 1),
        ],
        start_second=1,
    )
    expected_first_track_2 = create_track(
        track_id="1_1",
        original_id=track_id_1,
        coord=[(3, 1), (4, 1), (4, 2), (3, 2)],
        start_second=3,
    )
    expected_first_track_3 = create_track(
        track_id="1_2", original_id=track_id_1, coord=[(2, 2), (1, 2)], start_second=7
    )

    second_track = create_track(
        track_id=track_id_2, coord=[(1, 1), (2, 1), (3, 1)], start_second=1
    )
    expected_second_track_1 = create_track(
        track_id="2_0", original_id=track_id_2, coord=[(1, 1), (2, 1)], start_second=1
    )
    expected_second_track_2 = create_track(
        track_id="2_1", original_id=track_id_2, coord=[(3, 1)], start_second=3
    )

    third_track = create_track(
        track_id=track_id_3,
        original_id=track_id_3,
        coord=[(10, 10), (20, 10)],
        start_second=10,
    )

    _id = "#cut_1"
    cutting_section = LineSection(
        SectionId(_id), _id, {}, {}, [Coordinate(2.5, 0), Coordinate(2.5, 3)]
    )

    expected_original_track_ids = {first_track.id, second_track.id}

    return (
        cutting_section,
        [first_track, second_track, third_track],
        [
            expected_first_track_1,
            expected_first_track_2,
            expected_first_track_3,
            expected_second_track_1,
            expected_second_track_2,
        ],
        expected_original_track_ids,
    )


@pytest.fixture
def track_segment_dataset_builder_provider() -> TrackSegmentDatasetBuilderProvider:
    return TrackSegmentDatasetBuilderProvider()


@pytest.fixture
def python_track_segment_dataset_builder(
    track_segment_dataset_builder_provider: TrackSegmentDatasetBuilderProvider,
) -> TrackSegmentDatasetBuilder:
    return track_segment_dataset_builder_provider.provide(PYTHON)


@pytest.fixture
def pandas_track_segment_dataset_builder(
    track_segment_dataset_builder_provider: TrackSegmentDatasetBuilderProvider,
) -> TrackSegmentDatasetBuilder:
    return track_segment_dataset_builder_provider.provide(PANDAS)


@pytest.fixture
def first_line_section() -> Section:
    return LineSection(
        SectionId("1"), "First Section", {}, {}, [Coordinate(0, 0), Coordinate(1, 0)]
    )


@pytest.fixture
def second_line_section() -> Section:
    return LineSection(
        SectionId("2"), "Second Section", {}, {}, [Coordinate(0, 0), Coordinate(1, 0)]
    )


@pytest.fixture
def first_flow(first_line_section: Section, second_line_section: Section) -> Flow:
    _id = FlowId("First Flow")
    return Flow(_id, _id.id, first_line_section.id, second_line_section.id)


@pytest.fixture
def first_section_event(first_line_section: Section) -> Event:
    builder = EventBuilder()
    builder.add_road_user_id("Road User 1")
    builder.add_section_id(first_line_section.id.id)
    return builder.build_section_event()


@pytest.fixture
def second_section_event(second_line_section: Section) -> Event:
    builder = EventBuilder()
    builder.add_road_user_id("Road User 1")
    builder.add_section_id(second_line_section.id.id)
    return builder.build_section_event()


@pytest.fixture
def first_road_user_assignment(
    first_flow: Flow, first_section_event: Event, second_section_event: Event
) -> RoadUserAssignment:
    return RoadUserAssignment(
        "Road User 1",
        "car",
        first_flow,
        EventPair(first_section_event, second_section_event),
    )


@pytest.fixture
def second_road_user_assignment(
    first_flow: Flow, first_section_event: Event, second_section_event: Event
) -> RoadUserAssignment:
    return RoadUserAssignment(
        "Road User 2",
        "bike",
        first_flow,
        EventPair(first_section_event, second_section_event),
    )
