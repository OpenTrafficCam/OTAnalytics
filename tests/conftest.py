import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Generator, TypeVar

import pytest

from OTAnalytics.domain.event import Event, EventType
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    Detection,
    Track,
    TrackId,
    TrackRepository,
)
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser, OttrkParser

T = TypeVar("T")
YieldFixture = Generator[T, None, None]


@dataclass
class TrackBuilder:
    track_id: int = 1
    track_class: str = "car"
    detection_class: str = "car"
    confidence: float = 0.5
    x: float = 0
    y: float = 0
    w: float = 10
    h: float = 10
    frame: int = 1
    occurrence_year: int = 2020
    occurrence_month: int = 1
    occurrence_day: int = 1
    occurrence_hour: int = 0
    occurrence_minute: int = 0
    occurrence_second: int = 0
    occurrence_microsecond: int = 0
    input_file_path: str = "path/to/myhostname_file.otdet"
    interpolated_detection: bool = False

    def __post_init__(self) -> None:
        self._detections: list[Detection] = []

    def build_track(self) -> Track:
        return Track(TrackId(self.track_id), self.track_class, self._detections)

    def build_detections(self) -> list[Detection]:
        return self._detections

    def append_detection(self) -> None:
        self._detections.append(
            Detection(
                classification=self.detection_class,
                confidence=self.confidence,
                x=self.x,
                y=self.y,
                w=self.w,
                h=self.h,
                frame=self.frame,
                occurrence=datetime(
                    self.occurrence_year,
                    self.occurrence_month,
                    self.occurrence_day,
                    self.occurrence_hour,
                    self.occurrence_minute,
                    self.occurrence_second,
                    self.occurrence_microsecond,
                ),
                input_file_path=Path(self.input_file_path),
                interpolated_detection=self.interpolated_detection,
                track_id=TrackId(self.track_id),
            )
        )

    def add_track_id(self, id: int) -> None:
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

    def add_microsecond(self, microsecond: int) -> None:
        self.occurrence_microsecond = microsecond

    def add_xy_bbox(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def get_example_metadata(self) -> dict:
        return {
            "otdet_version": "1.0",
            "video": {
                "filename": "path/to/myhostname_file",
                "filetype": ".mp4",
                "width": 800.0,
                "height": 600.0,
                "recorded_fps": 20.0,
                "number_of_frames": 60.0,
                "recorded_start_date": "2020-01-01 00:00:00.000000",
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
            "ottrk_version": "1.0",
            "tracking": {
                "otvision_version": "1.0",
                "first_tracked_video_start": "2020-01-01 00:00:00.000000",
                "last_tracked_video_end": "2020-01-01 00:00:02.950000",
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
            ottrk_dataformat.OCCURRENCE: detection.occurrence.strftime(
                ottrk_dataformat.DATE_FORMAT
            ),
            ottrk_dataformat.INPUT_FILE_PATH: str(detection.input_file_path),
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
            ottrk_dataformat.METADATA: self.get_example_metadata(),
            ottrk_dataformat.DATA: {ottrk_dataformat.DETECTIONS: detections},
        }


@dataclass
class EventBuilder:
    road_user_id: int = 1
    road_user_type: str = "car"
    hostname: str = "myhostname"
    occurrence_year: int = 2020
    occurrence_month: int = 1
    occurrence_day: int = 1
    occurrence_hour: int = 0
    occurrence_minute: int = 0
    occurrence_second: int = 0
    occurrence_microsecond: int = 0
    frame_number: int = 1
    section_id: str = "N"
    event_coordinate_x: float = 0.0
    event_coordinate_y: float = 0.0
    event_type: str = "section-enter"
    direction_vector_x: float = 0.0
    direction_vector_y: float = 0.0
    video_name: str = "myhostname_file.otdet"

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

    def add_microsecond(self, microsecond: int) -> None:
        self.occurrence_microsecond = microsecond

    def add_frame_number(self, frame_number: int) -> None:
        self.frame_number = frame_number

    def add_event_type(self, event_type: str) -> None:
        self.event_type = event_type

    def add_event_coordinate(self, x: float, y: float) -> None:
        self.event_coordinate_x = x
        self.event_coordinate_y = y


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
def tracks(ottrk_path: Path) -> list[Track]:
    ottrk_parser = OttrkParser(
        CalculateTrackClassificationByMaxConfidence(),
        TrackRepository(),
    )
    return ottrk_parser.parse(ottrk_path)


@pytest.fixture(scope="module")
def sections(otsection_file: Path) -> list[Section]:
    otsection_parser = OtsectionParser()
    return otsection_parser.parse(otsection_file)


@pytest.fixture
def track_builder() -> TrackBuilder:
    return TrackBuilder()


@pytest.fixture
def event_builder() -> EventBuilder:
    return EventBuilder()
