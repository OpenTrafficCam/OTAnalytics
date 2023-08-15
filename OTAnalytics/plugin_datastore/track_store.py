from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

import pandas
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.track import Detection, Track, TrackDataset, TrackId


class PandasDetection(Detection):
    def __init__(self, data: Series):
        self._data = data

    @property
    def classification(self) -> str:
        return self.__get_attribute(track.CLASSIFICATION)

    def __get_attribute(self, column: str) -> Any:
        return self._data.loc[column]

    @property
    def confidence(self) -> float:
        return self.__get_attribute(track.CONFIDENCE)

    @property
    def x(self) -> float:
        return self.__get_attribute(track.X)

    @property
    def y(self) -> float:
        return self.__get_attribute(track.Y)

    @property
    def w(self) -> float:
        return self.__get_attribute(track.W)

    @property
    def h(self) -> float:
        return self.__get_attribute(track.H)

    @property
    def frame(self) -> int:
        return self.__get_attribute(track.FRAME)

    @property
    def occurrence(self) -> datetime:
        return self.__get_attribute(track.OCCURRENCE)

    @property
    def input_file_path(self) -> Path:
        return Path(self.__get_attribute(track.INPUT_FILE_PATH))

    @property
    def interpolated_detection(self) -> bool:
        return self.__get_attribute(track.INTERPOLATED_DETECTION)

    @property
    def track_id(self) -> TrackId:
        return TrackId(self.__get_attribute(track.TRACK_ID))


@dataclass
class PandasTrack(Track):
    _data: DataFrame

    @property
    def id(self) -> TrackId:
        return TrackId(self._data[track.TRACK_ID].iloc[0])

    @property
    def classification(self) -> str:
        return self._data[track.CLASSIFICATION].iloc[0]

    @property
    def detections(self) -> list[Detection]:
        return [PandasDetection(row) for index, row in self._data.iterrows()]


@dataclass
class PandasTrackDataset(TrackDataset):
    def __init__(self, dataset: DataFrame = DataFrame()):
        self._dataset = dataset

    @staticmethod
    def from_list(tracks: list[Track]) -> TrackDataset:
        return PandasTrackDataset(_convert_tracks(tracks))

    def add_all(self, other: TrackDataset) -> TrackDataset:
        new_tracks = _convert_tracks(other.as_list())
        new_dataset = pandas.concat([self._dataset, new_tracks])
        return PandasTrackDataset(new_dataset)

    def get_for(self, id: TrackId) -> Optional[Track]:
        if self._dataset.empty:
            return None
        return self.__create_track_flyweight(id.id)

    def clear(self) -> "TrackDataset":
        return PandasTrackDataset()

    def as_list(self) -> list[Track]:
        if self._dataset.empty:
            return []
        track_ids = self._dataset.loc[:, track.TRACK_ID].unique()
        return [self.__create_track_flyweight(current) for current in track_ids]

    def __create_track_flyweight(self, track_id: int) -> Track:
        track_frame = self._dataset.loc[self._dataset[track.TRACK_ID] == track_id, :]
        return PandasTrack(track_frame)


def _convert_tracks(tracks: Iterable[Track]) -> DataFrame:
    """
    Convert tracks into a dataframe.

    Args:
        tracks (Iterable[Track]): tracks to convert.

    Returns:
        DataFrame: tracks as dataframe.
    """
    prepared: list[dict] = []
    for current_track in list(tracks):
        for detection in current_track.detections:
            detection_dict = detection.to_dict()
            detection_dict[track.CLASSIFICATION] = current_track.classification
            prepared.append(detection_dict)

    return _sort_tracks(DataFrame(prepared))


def _sort_tracks(track_df: DataFrame) -> DataFrame:
    """Sort the given dataframe by trackId and frame,
    if both columns are available.

    Args:
        track_df (DataFrame): dataframe of tracks

    Returns:
        DataFrame: sorted dataframe by track id and frame
    """
    if (track.TRACK_ID in track_df.columns) and (track.FRAME in track_df.columns):
        return track_df.sort_values([track.TRACK_ID, track.FRAME])
    else:
        return track_df
