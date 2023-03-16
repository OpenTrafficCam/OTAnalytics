from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from pydantic import BaseModel, Field, validator

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format


@dataclass(frozen=True)
class TrackId:
    id: int


class Detection(BaseModel, frozen=True, allow_population_by_field_name=True):
    """Represents a detection belonging to a `Track`.

    The detection uses the xywh bounding box format.

    Extends from pydantic.BaseModel.
    IMPORTANT: Instantiation of this class is only possible by using named parameters.

    Raises:
        ValueError: confidence not in [0,1]
        ValueError: x < 0
        ValueError: y < 0
        ValueError: w < 0
        ValueError: h < 0
        ValueError: frame < 0
        ValueError: track_id < 0


    Args:
        classification (str): class of detection.
        confidence (float): the confidence.
        x (float): the x coordinate component of the bounding box.
        y (float): the y coordinate component of the bounding box.
        w (float): the width component of the bounding box.
        h (float): the height component of the bounding box.
        frame (int): the frame that the detection belongs to.
        occurrence (datetime): the time of the detection's occurence.
        input_file_path (Path): absolute path to otdet that the detection belongs to
        at the time of its creation.
        interpolated_detection (bool): whether this detection is interpolated.
        track_id (int): the track id this detection belongs to.
    """

    classification: str = Field(alias=ottrk_format.CLASS)
    confidence: float = Field(
        ge=0, le=1, description="must be in range [0,1]", alias=ottrk_format.CONFIDENCE
    )
    x: float = Field(ge=0, description="must be greater equal 0", alias=ottrk_format.X)
    y: float = Field(ge=0, description="must be greater equal 0", alias=ottrk_format.Y)
    w: float = Field(ge=0, description="must be greater equal 0", alias=ottrk_format.W)
    h: float = Field(ge=0, description="must be greater equal 0", alias=ottrk_format.H)
    frame: int = Field(
        gt=0, description="must be greater than 0", alias=ottrk_format.FRAME
    )
    occurrence: datetime = Field(alias=ottrk_format.OCCURRENCE)
    input_file_path: Path = Field(alias=ottrk_format.INPUT_FILE_PATH)
    interpolated_detection: bool = Field(alias=ottrk_format.INTERPOLATED_DETECTION)
    track_id: TrackId


class Track(BaseModel, frozen=True, allow_population_by_field_name=True):
    """Represents the the track of an object as seen in the task of object tracking
    (computer vision).

    Extends from pydantic.BaseModel.
    IMPORTANT: Instantiation of this class is only possible by using named parameters.

    Args:
        id (int): the track id.
        detections (list[Detection]): the detections belonging to this track.

    Raises:
        ValueError: if detections are not sorted by `occurrence`.
        ValueError: if an empty detections list has been passed.
    """

    id: TrackId
    detections: list[Detection] = Field(alias=ottrk_format.DETECTIONS)

    @validator("detections")
    def detections_must_be_in_right_order(
        cls, detections: list[Detection]
    ) -> list[Detection]:
        if detections != sorted(detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurence")
        return detections

    @validator("detections")
    def detections_must_not_be_empty(
        cls, detections: list[Detection]
    ) -> list[Detection]:
        if not detections:
            raise ValueError("must not be empty")
        return detections


class TrackRepository(BaseModel):
    tracks: dict[TrackId, Track] = {}

    def add(self, track: Track) -> None:
        self.tracks[track.id] = track

    def add_all(self, tracks: Iterable[Track]) -> None:
        for track in tracks:
            self.add(track)

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self.tracks[id]

    def get_all(self) -> Iterable[Track]:
        return self.tracks.values()
