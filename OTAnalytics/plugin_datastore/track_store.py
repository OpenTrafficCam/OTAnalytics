from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Any, Iterable, Optional, Sequence

import pandas
from more_itertools import batched
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    INTERSECTION_COORDINATE,
    MIN_NUMBER_OF_DETECTIONS,
    Detection,
    Track,
    TrackDataset,
    TrackId,
)


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
    def interpolated_detection(self) -> bool:
        return self.__get_attribute(track.INTERPOLATED_DETECTION)

    @property
    def track_id(self) -> TrackId:
        return TrackId(self.__get_attribute(track.TRACK_ID))

    @property
    def video_name(self) -> str:
        return self.__get_attribute(track.VIDEO_NAME)


@dataclass
class PandasTrack(Track):
    _data: DataFrame

    @property
    def id(self) -> TrackId:
        return TrackId(self._data[track.TRACK_ID].iloc[0])

    @property
    def classification(self) -> str:
        return self._data[track.TRACK_CLASSIFICATION].iloc[0]

    @property
    def detections(self) -> list[Detection]:
        return [PandasDetection(row) for index, row in self._data.iterrows()]

    @property
    def first_detection(self) -> Detection:
        return PandasDetection(self._data.iloc[0])

    @property
    def last_detection(self) -> Detection:
        return PandasDetection(self._data.iloc[-1])


class PandasTrackClassificationCalculator(ABC):
    """
    Defines interface for calculation strategy to determine a track's classification.
    """

    @abstractmethod
    def calculate(self, detections: DataFrame) -> Series:
        """Determine a track's classification.

        Args:
            detections (Detection): the track's detections needed to determine the
                classification

        Returns:
            str: the track's class
        """
        raise NotImplementedError


class PandasByMaxConfidence(PandasTrackClassificationCalculator):
    """Determine a track's classification by its detections max confidence."""

    def calculate(self, detections: DataFrame) -> DataFrame:
        if detections.empty:
            return DataFrame()
        classifications = (
            detections.loc[:, [track.TRACK_ID, track.CLASSIFICATION, track.CONFIDENCE]]
            .groupby(by=[track.TRACK_ID, track.CLASSIFICATION])
            .sum()
            .sort_values(track.CONFIDENCE)
            .groupby(level=0)
            .tail(1)
        )
        reset = classifications.reset_index()
        renamed = reset.rename(
            columns={track.CLASSIFICATION: track.TRACK_CLASSIFICATION}
        )
        return renamed.loc[:, [track.TRACK_ID, track.TRACK_CLASSIFICATION]]


DEFAULT_CLASSIFICATOR = PandasByMaxConfidence()


class PandasTrackDataset(TrackDataset):
    def __init__(
        self,
        dataset: DataFrame = DataFrame(),
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ):
        self._dataset = dataset
        self._calculator = calculator

    @staticmethod
    def from_list(
        tracks: list[Track],
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> TrackDataset:
        return PandasTrackDataset.from_dataframe(_convert_tracks(tracks), calculator)

    @staticmethod
    def from_dataframe(
        tracks: DataFrame,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> TrackDataset:
        if tracks.empty:
            return PandasTrackDataset()
        classified_tracks = _assign_track_classification(tracks, calculator)
        detections_per_track = (
            classified_tracks.groupby(by=track.TRACK_ID)[track.FRAME]
            .count()
            .reset_index()
        )
        valid_track_ids = detections_per_track.loc[
            detections_per_track[track.FRAME] >= MIN_NUMBER_OF_DETECTIONS,
            track.TRACK_ID,
        ]
        valid_tracks = classified_tracks.loc[
            classified_tracks[track.TRACK_ID].isin(valid_track_ids), :
        ]
        return PandasTrackDataset(valid_tracks)

    def add_all(self, other: Iterable[Track]) -> TrackDataset:
        new_tracks = self.__get_tracks(other)
        if new_tracks.empty:
            return self
        if self._dataset.empty:
            return PandasTrackDataset.from_dataframe(new_tracks, self._calculator)
        new_dataset = pandas.concat([self._dataset, new_tracks])
        return PandasTrackDataset.from_dataframe(new_dataset)

    def get_all_ids(self) -> Iterable[TrackId]:
        return self._dataset[track.TRACK_ID].apply(lambda track_id: TrackId(track_id))

    def __get_tracks(self, other: Iterable[Track]) -> DataFrame:
        if isinstance(other, PandasTrackDataset):
            return other._dataset
        return _convert_tracks(other)

    def get_for(self, id: TrackId) -> Optional[Track]:
        if self._dataset.empty:
            return None
        return self.__create_track_flyweight(id.id)

    def clear(self) -> "TrackDataset":
        return PandasTrackDataset()

    def remove(self, track_id: TrackId) -> "TrackDataset":
        remaining_tracks = self._dataset.loc[
            self._dataset[track.TRACK_ID] != track_id.id, :
        ]
        return PandasTrackDataset(remaining_tracks.copy())

    def as_list(self) -> list[Track]:
        if self._dataset.empty:
            return []
        track_ids = self._dataset.loc[:, track.TRACK_ID].unique()
        return [self.__create_track_flyweight(current) for current in track_ids]

    def __create_track_flyweight(self, track_id: str) -> Track:
        track_frame = self._dataset.loc[self._dataset[track.TRACK_ID] == track_id, :]
        return PandasTrack(track_frame)

    def as_dataframe(self) -> DataFrame:
        return self._dataset

    def split(self, batches: int) -> Sequence["TrackDataset"]:
        all_ids = self._dataset[track.TRACK_ID].unique()
        dataset_size = len(all_ids)
        batch_size = ceil(dataset_size / batches)

        new_batches: list["TrackDataset"] = []
        for batch_ids in batched(all_ids, batch_size):
            batch_dataset = self._dataset[self._dataset[track.TRACK_ID].isin(batch_ids)]
            new_batches.append(PandasTrackDataset(batch_dataset, self._calculator))

        return new_batches

    def __len__(self) -> int:
        return len(self._dataset[track.TRACK_ID].unique())

    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        detection_counts_per_track = self._dataset.groupby([track.TRACK_ID])[
            track.CLASSIFICATION
        ].count()
        filtered_ids = detection_counts_per_track[
            detection_counts_per_track > length
        ].index

        filtered_dataset = self._dataset.loc[
            self._dataset[track.TRACK_ID].isin(filtered_ids)
        ]
        return PandasTrackDataset(filtered_dataset, self._calculator)

    def intersecting_tracks(self, sections: list[Section]) -> set[TrackId]:
        raise NotImplementedError

    def intersection_points(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, INTERSECTION_COORDINATE]]]:
        raise NotImplementedError


def _assign_track_classification(
    data: DataFrame, calculator: PandasTrackClassificationCalculator
) -> DataFrame:
    dropped = _drop_track_classification(data)
    classification_per_track = calculator.calculate(dropped)
    return dropped.merge(classification_per_track, on=track.TRACK_ID)


def _drop_track_classification(data: DataFrame) -> DataFrame:
    if track.TRACK_CLASSIFICATION in data.columns:
        return data.drop(columns=[track.TRACK_CLASSIFICATION])
    return data


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
            prepared.append(detection.to_dict())

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
