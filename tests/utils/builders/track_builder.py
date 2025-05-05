from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self

from OTAnalytics.domain.track import Detection, Track, TrackId
from OTAnalytics.plugin_datastore.python_track_store import PythonDetection, PythonTrack
from OTAnalytics.plugin_parser import ottrk_dataformat
from tests.utils.builders.constants import (
    DEFAULT_INPUT_FILE,
    DEFAULT_OCCURRENCE_DAY,
    DEFAULT_OCCURRENCE_HOUR,
    DEFAULT_OCCURRENCE_MICROSECOND,
    DEFAULT_OCCURRENCE_MINUTE,
    DEFAULT_OCCURRENCE_MONTH,
    DEFAULT_OCCURRENCE_SECOND,
    DEFAULT_OCCURRENCE_YEAR,
    DEFAULT_VIDEO_NAME,
)


@dataclass
class TrackBuilder:
    otdet_version = "1.2"
    ottrk_version = "1.1"
    track_id: str = "1"
    original_id: str | None = None
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
    input_file: str = DEFAULT_INPUT_FILE
    interpolated_detection: bool = False

    def __post_init__(self) -> None:
        self._detections: list[Detection] = []

    def build_track(self) -> Track:
        track_id = TrackId(self.track_id)
        return PythonTrack(
            _id=track_id,
            _original_id=self.create_original_id(),
            _classification=self.track_class,
            _detections=self._detections,
        )

    def create_original_id(self) -> TrackId:
        if self.original_id is None:
            return TrackId(self.track_id)

        return TrackId(self.original_id)

    def build_detections(self) -> list[Detection]:
        return self._detections

    def set_otdet_version(self, otdet_version: str) -> None:
        self.otdet_version = otdet_version

    def set_ottrk_version(self, ottrk_version: str) -> None:
        self.ottrk_version = ottrk_version

    def set_video_name(self, video_name: str) -> None:
        self.video_name = video_name

    def append_detection(self) -> None:
        self._detections.append(self.create_detection())

    def next_frame(self) -> None:
        self.frame += 1

    def create_detection(self) -> Detection:
        return PythonDetection(
            _classification=self.detection_class,
            _confidence=self.confidence,
            _x=float(self.x),
            _y=float(self.y),
            _w=float(self.w),
            _h=float(self.h),
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
            _input_file=self.input_file,
        )

    def add_track_id(self, id: str) -> Self:
        self.track_id = id
        return self

    def add_detection_class(self, classification: str) -> Self:
        self.detection_class = classification
        return self

    def add_confidence(self, confidence: float) -> Self:
        self.confidence = confidence
        return self

    def add_frame(self, frame: int) -> Self:
        self.frame = frame
        return self

    def add_track_class(self, classification: str) -> Self:
        self.track_class = classification
        return self

    def add_occurrence(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        microsecond: int,
    ) -> Self:
        self.occurrence_year = year
        self.occurrence_month = month
        self.occurrence_day = day
        self.occurrence_hour = hour
        self.occurrence_minute = minute
        self.occurrence_second = second
        self.occurrence_microsecond = microsecond
        return self

    def add_second(self, second: int) -> Self:
        self.occurrence_second = second
        return self

    def add_microsecond(self, microsecond: int) -> Self:
        self.occurrence_microsecond = microsecond
        return self

    def add_xy_bbox(self, x: float, y: float) -> Self:
        self.x = x
        self.y = y
        return self

    def add_wh_bbox(self, w: float, h: float) -> Self:
        self.w = w
        self.h = h
        return self

    def add_input_file(self, input_file: str) -> Self:
        self.input_file = input_file
        return self

    def add_original_id(self, original_id: str) -> Self:
        self.original_id = original_id
        return self

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


def create_track(
    track_id: str,
    coord: list[tuple],
    start_second: int,
    track_class: str = "car",
    detection_classes: list[str] | None = None,
    confidences: list[float] | None = None,
    original_id: str | None = None,
) -> Track:
    if detection_classes:
        if len(detection_classes) != len(coord):
            raise ValueError(
                "Track coordinates must match length of detection classifications."
            )
    if confidences:
        if len(confidences) != len(coord):
            raise ValueError("Track coordinates must match length of confidences.")

    if original_id is None:
        original_id = track_id

    track_builder = TrackBuilder()
    track_builder.add_track_id(track_id)
    track_builder.add_original_id(original_id)
    track_builder.add_track_class(track_class)

    current_second = start_second
    for current_index, (x, y) in enumerate(coord, start=0):
        track_builder.add_second(current_second)
        track_builder.add_xy_bbox(x, y)
        if detection_classes:
            track_builder.add_detection_class(detection_classes[current_index])
        else:
            track_builder.add_detection_class(track_class)
        if confidences:
            track_builder.add_confidence(confidences[current_index])
        track_builder.append_detection()
        current_second += 1

    return track_builder.build_track()


def track_builder_with_sample_data(
    input_file: str = DEFAULT_INPUT_FILE,
    frame_offset: int = 0,
    microsecond_offset: int = 0,
) -> TrackBuilder:
    return append_sample_data(
        TrackBuilder(input_file=input_file),
        frame_offset=frame_offset,
        microsecond_offset=microsecond_offset,
    )
