import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Sequence, TypeVar
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Detection, Track, TrackId
from OTAnalytics.domain.track_dataset import TrackDataset
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.python_track_store import PythonDetection, PythonTrack
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasByMaxConfidence
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_parser.otconfig_parser import OtConfigFormatFixer
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    OtFlowParser,
    OttrkParser,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser

T = TypeVar("T")
YieldFixture = Generator[T, None, None]

DEFAULT_HOSTNAME = "myhostname"
DEFAULT_VIDEO_NAME = f"{DEFAULT_HOSTNAME}_file.mp4"
DEFAULT_OTDET_FILE = f"path/to/{DEFAULT_VIDEO_NAME}"
DEFAULT_OCCURRENCE_YEAR: int = 2020
DEFAULT_OCCURRENCE_MONTH: int = 1
DEFAULT_OCCURRENCE_DAY: int = 1
DEFAULT_OCCURRENCE_HOUR: int = 0
DEFAULT_OCCURRENCE_MINUTE: int = 0
DEFAULT_OCCURRENCE_SECOND: int = 0
DEFAULT_OCCURRENCE_MICROSECOND: int = 0


@dataclass
class TrackBuilder:
    otdet_version = "1.2"
    ottrk_version = "1.1"
    track_id: str = "1"
    track_class: str = "car"
    detection_class: str = "car"
    confidence: float = 0.5
    x: float = 0.0
    y: float = 0.0
    w: float = 10.0
    h: float = 10.0
    frame: int = 1
    occurrence_year: int = DEFAULT_OCCURRENCE_YEAR
    occurrence_month: int = DEFAULT_OCCURRENCE_MONTH
    occurrence_day: int = DEFAULT_OCCURRENCE_DAY
    occurrence_hour: int = DEFAULT_OCCURRENCE_HOUR
    occurrence_minute: int = DEFAULT_OCCURRENCE_MINUTE
    occurrence_second: int = DEFAULT_OCCURRENCE_SECOND
    occurrence_microsecond: int = DEFAULT_OCCURRENCE_MICROSECOND
    video_name: str = DEFAULT_VIDEO_NAME
    interpolated_detection: bool = False

    def __post_init__(self) -> None:
        self._detections: list[Detection] = []

    def build_track(self) -> Track:
        return PythonTrack(TrackId(self.track_id), self.track_class, self._detections)

    def build_detections(self) -> list[Detection]:
        return self._detections

    def set_otdet_version(self, otdet_version: str) -> None:
        self.otdet_version = otdet_version

    def set_ottrk_version(self, ottrk_version: str) -> None:
        self.ottrk_version = ottrk_version

    def append_detection(self) -> None:
        self._detections.append(self.create_detection())

    def create_detection(self) -> Detection:
        return PythonDetection(
            _classification=self.detection_class,
            _confidence=self.confidence,
            _x=self.x,
            _y=self.y,
            _w=self.w,
            _h=self.h,
            _frame=self.frame,
            _occurrence=datetime(
                self.occurrence_year,
                self.occurrence_month,
                self.occurrence_day,
                self.occurrence_hour,
                self.occurrence_minute,
                self.occurrence_second,
                self.occurrence_microsecond,
                tzinfo=timezone.utc,
            ),
            _interpolated_detection=self.interpolated_detection,
            _track_id=TrackId(self.track_id),
            _video_name=self.video_name,
        )

    def add_track_id(self, id: str) -> None:
        self.track_id = id

    def add_detection_class(self, classification: str) -> None:
        self.detection_class = classification

    def add_confidence(self, confidence: float) -> None:
        self.confidence = confidence

    def add_frame(self, frame: int) -> None:
        self.frame = frame

    def add_track_class(self, classification: str) -> None:
        self.track_class = classification

    def add_occurrence(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        microsecond: int,
    ) -> None:
        self.occurrence_year = year
        self.occurrence_month = month
        self.occurrence_day = day
        self.occurrence_hour = hour
        self.occurrence_minute = minute
        self.occurrence_second = second
        self.occurrence_microsecond = microsecond

    def add_second(self, second: int) -> None:
        self.occurrence_second = second

    def add_microsecond(self, microsecond: int) -> None:
        self.occurrence_microsecond = microsecond

    def add_xy_bbox(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def add_wh_bbox(self, w: float, h: float) -> None:
        self.w = w
        self.h = h

    def get_metadata(self) -> dict:
        return {
            "otdet_version": self.otdet_version,
            "video": {
                "filename": "myhostname_file",
                "filetype": ".mp4",
                "width": 800.0,
                "height": 600.0,
                "recorded_fps": 20.0,
                "number_of_frames": 60.0,
                "recorded_start_date": self.__to_timestamp(
                    "2020-01-01 00:00:00.000000"
                ),
                "length": "0:00:03",
            },
            "detection": {
                "otvision_version": "1.0",
                "model": {
                    "name": "YOLOv5",
                    "weights": "yolov5s",
                    "iou_threshold": 0.45,
                    "image_size": 640,
                    "max_confidence": 0.25,
                    "half_precision": False,
                    "classes": {
                        "0": "person",
                        "1": "bicycle",
                        "2": "car",
                        "3": "motorcycle",
                        "5": "bus",
                        "6": "train",
                        "7": "truck",
                        "8": "boat",
                    },
                },
                "chunksize": 1,
                "normalized_bbox": False,
            },
            "ottrk_version": self.ottrk_version,
            "tracking": {
                "otvision_version": "1.0",
                "first_tracked_video_start": self.__to_timestamp(
                    "2020-01-01 00:00:00.000000"
                ),
                "last_tracked_video_end": self.__to_timestamp(
                    "2020-01-01 00:00:02.950000"
                ),
                "tracking_run_id": "1",
                "frame_group": "1",
                "tracker": {
                    "name": "IOU",
                    "sigma_l": 0.27,
                    "sigma_h": 0.42,
                    "sigma_iou": 0.38,
                    "t_min": 5,
                    "t_miss_max": 51,
                },
            },
        }

    def __to_timestamp(self, date_as_string: str) -> str:
        return str(
            datetime.strptime(date_as_string, ottrk_dataformat.DATE_FORMAT)
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

    def serialize_detection(
        self, detection: Detection, is_first: bool, is_finished: bool
    ) -> dict:
        return {
            ottrk_dataformat.CLASS: detection.classification,
            ottrk_dataformat.CONFIDENCE: detection.confidence,
            ottrk_dataformat.X: detection.x,
            ottrk_dataformat.Y: detection.y,
            ottrk_dataformat.W: detection.w,
            ottrk_dataformat.H: detection.h,
            ottrk_dataformat.FRAME: detection.frame,
            ottrk_dataformat.OCCURRENCE: str(detection.occurrence.timestamp()),
            ottrk_dataformat.INTERPOLATED_DETECTION: detection.interpolated_detection,
            ottrk_dataformat.FIRST: is_first,
            ottrk_dataformat.FINISHED: is_finished,
            ottrk_dataformat.TRACK_ID: detection.track_id.id,
        }

    def build_serialized_detections(self) -> list[dict]:
        detections: list[dict] = []
        detections.append(self.serialize_detection(self._detections[0], True, False))
        for detection in self._detections[1:-1]:
            detections.append(self.serialize_detection(detection, False, False))

        detections.append(self.serialize_detection(self._detections[-1], False, True))
        return detections

    def build_ottrk(self) -> dict:
        detections = self.build_serialized_detections()
        return {
            ottrk_dataformat.METADATA: self.get_metadata(),
            ottrk_dataformat.DATA: {ottrk_dataformat.DATA_DETECTIONS: detections},
        }


@dataclass
class EventBuilder:
    road_user_id: str = "1"
    road_user_type: str = "car"
    hostname: str = DEFAULT_HOSTNAME
    occurrence_year: int = DEFAULT_OCCURRENCE_YEAR
    occurrence_month: int = DEFAULT_OCCURRENCE_MONTH
    occurrence_day: int = DEFAULT_OCCURRENCE_DAY
    occurrence_hour: int = DEFAULT_OCCURRENCE_HOUR
    occurrence_minute: int = DEFAULT_OCCURRENCE_MINUTE
    occurrence_second: int = DEFAULT_OCCURRENCE_SECOND
    occurrence_microsecond: int = DEFAULT_OCCURRENCE_MICROSECOND
    frame_number: int = 1
    section_id: str = "N"
    event_coordinate_x: float = 0.0
    event_coordinate_y: float = 0.0
    event_type: str = "section-enter"
    direction_vector_x: float = 0.0
    direction_vector_y: float = 0.0
    video_name: str = DEFAULT_VIDEO_NAME

    def __post_init__(self) -> None:
        self._events: list[Event] = []

    def build_events(self) -> list[Event]:
        return self._events

    def build_section_event(self) -> Event:
        return Event(
            road_user_id=self.road_user_id,
            road_user_type=self.road_user_type,
            hostname=self.hostname,
            occurrence=datetime(
                self.occurrence_year,
                self.occurrence_month,
                self.occurrence_day,
                self.occurrence_hour,
                self.occurrence_minute,
                self.occurrence_second,
                self.occurrence_microsecond,
                tzinfo=timezone.utc,
            ),
            frame_number=self.frame_number,
            section_id=SectionId(self.section_id),
            event_coordinate=ImageCoordinate(
                self.event_coordinate_x, self.event_coordinate_y
            ),
            event_type=EventType.parse(self.event_type),
            direction_vector=DirectionVector2D(
                self.direction_vector_x, self.direction_vector_y
            ),
            video_name=self.video_name,
        )

    def append_section_event(self) -> None:
        self._events.append(self.build_section_event())

    def add_second(self, second: int) -> None:
        self.occurrence_second = second

    def add_microsecond(self, microsecond: int) -> None:
        self.occurrence_microsecond = microsecond

    def add_frame_number(self, frame_number: int) -> None:
        self.frame_number = frame_number

    def add_event_type(self, event_type: str) -> None:
        self.event_type = event_type

    def add_event_coordinate(self, x: float, y: float) -> None:
        self.event_coordinate_x = x
        self.event_coordinate_y = y

    def add_direction_vector(self, x: float, y: float) -> None:
        self.direction_vector_x = x
        self.direction_vector_y = y

    def add_road_user_id(self, id: str) -> None:
        self.road_user_id = id

    def add_road_user_type(self, type: str) -> None:
        self.road_user_type = type

    def add_section_id(self, id: str) -> None:
        self.section_id = id


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
        PygeosTrackGeometryDataset.from_track_dataset,
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


def assert_equal_detection_properties(actual: Detection, expected: Detection) -> None:
    assert expected.classification == actual.classification
    assert expected.confidence == actual.confidence
    assert expected.x == actual.x
    assert expected.y == actual.y
    assert expected.w == actual.w
    assert expected.h == actual.h
    assert expected.frame == actual.frame
    assert expected.occurrence == actual.occurrence
    assert expected.video_name == actual.video_name
    assert expected.interpolated_detection == actual.interpolated_detection
    assert actual.track_id == expected.track_id


def assert_equal_track_properties(actual: Track, expected: Track) -> None:
    assert actual.id == expected.id
    assert actual.classification == expected.classification
    assert len(actual.detections) == len(expected.detections)
    for first_detection, second_detection in zip(
        expected.detections, actual.detections
    ):
        assert_equal_detection_properties(second_detection, first_detection)


def assert_track_datasets_equal(actual: TrackDataset, expected: TrackDataset) -> None:
    assert actual.track_ids == expected.track_ids

    for actual_track in actual.as_list():
        if expected_track := expected.get_for(actual_track.id):
            assert_equal_track_properties(actual_track, expected_track)
        else:
            raise AssertionError(
                f"Track with id {actual_track.id} not found in expected dataset"
            )


def append_sample_data(
    track_builder: TrackBuilder,
    frame_offset: int = 0,
    microsecond_offset: int = 0,
) -> TrackBuilder:
    track_builder.add_frame(frame_offset + 1)
    track_builder.add_microsecond(microsecond_offset + 1)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 2)
    track_builder.add_microsecond(microsecond_offset + 2)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 3)
    track_builder.add_microsecond(microsecond_offset + 3)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 4)
    track_builder.add_microsecond(microsecond_offset + 4)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 5)
    track_builder.add_microsecond(microsecond_offset + 5)
    track_builder.append_detection()

    return track_builder


def create_track(track_id: str, coord: list[tuple], start_second: int) -> Track:
    track_builder = TrackBuilder()

    track_builder.add_track_id(track_id)
    for second, (x, y) in enumerate(coord, start=start_second):
        track_builder.add_second(second)
        track_builder.add_xy_bbox(x, y)
        track_builder.append_detection()
    return track_builder.build_track()
