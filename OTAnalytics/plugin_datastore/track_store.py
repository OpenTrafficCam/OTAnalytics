from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Any, Iterable, Optional, Sequence

import pandas
from more_itertools import batched
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    TRACK_GEOMETRY_FACTORY,
    Detection,
    IntersectionPoint,
    Track,
    TrackDataset,
    TrackGeometryDataset,
    TrackId,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)


class PandasDetection(Detection):
    def __init__(self, track_id: str, data: Series):
        self._track_id = track_id
        self._occurrence: Any = data.name
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
        return self._occurrence

    @property
    def interpolated_detection(self) -> bool:
        return self.__get_attribute(track.INTERPOLATED_DETECTION)

    @property
    def track_id(self) -> TrackId:
        return TrackId(self._track_id)

    @property
    def video_name(self) -> str:
        return self.__get_attribute(track.VIDEO_NAME)


@dataclass
class PandasTrack(Track):
    _id: str
    _data: DataFrame

    @property
    def id(self) -> TrackId:
        return TrackId(self._id)

    @property
    def classification(self) -> str:
        return self._data[track.TRACK_CLASSIFICATION].iloc[0]

    @property
    def detections(self) -> list[Detection]:
        return [PandasDetection(self._id, row) for _, row in self._data.iterrows()]

    @property
    def first_detection(self) -> Detection:
        return PandasDetection(self._id, self._data.iloc[0])

    @property
    def last_detection(self) -> Detection:
        return PandasDetection(self._id, self._data.iloc[-1])


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
            detections.loc[:, [track.CLASSIFICATION, track.CONFIDENCE]]
            .groupby(by=[track.TRACK_ID, track.CLASSIFICATION])
            .sum()
            .sort_values(track.CONFIDENCE)
            .groupby(level=0)
            .tail(1)
        )
        reset = classifications.reset_index(level=[1])
        renamed = reset.rename(
            columns={track.CLASSIFICATION: track.TRACK_CLASSIFICATION}
        )
        return renamed.loc[:, [track.TRACK_CLASSIFICATION]]


DEFAULT_CLASSIFICATOR = PandasByMaxConfidence()
INDEX_NAMES = [track.TRACK_ID, track.OCCURRENCE]
LEVEL_TRACK_ID = 0
LEVEL_OCCURRENCE = 1


class PandasTrackDataset(TrackDataset):
    def __init__(
        self,
        dataset: DataFrame = DataFrame(),
        geometry_datasets: dict[RelativeOffsetCoordinate, TrackGeometryDataset]
        | None = None,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY = (
            PygeosTrackGeometryDataset.from_track_dataset
        ),
    ):
        self._dataset = dataset
        self._calculator = calculator
        self._track_geometry_factory = track_geometry_factory
        if geometry_datasets is None:
            self._geometry_datasets = dict[
                RelativeOffsetCoordinate, TrackGeometryDataset
            ]()
        else:
            self._geometry_datasets = geometry_datasets

    @staticmethod
    def from_list(
        tracks: list[Track],
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> TrackDataset:
        return PandasTrackDataset.from_dataframe(
            _convert_tracks(tracks), calculator=calculator
        )

    @staticmethod
    def from_dataframe(
        tracks: DataFrame,
        geometry_dataset: dict[RelativeOffsetCoordinate, TrackGeometryDataset]
        | None = None,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> TrackDataset:
        if tracks.empty:
            return PandasTrackDataset()
        classified_tracks = _assign_track_classification(tracks, calculator)
        return PandasTrackDataset(classified_tracks, geometry_datasets=geometry_dataset)

    def add_all(self, other: Iterable[Track]) -> TrackDataset:
        new_tracks = self.__get_tracks(other)
        if new_tracks.empty:
            return self
        if self._dataset.empty:
            return PandasTrackDataset.from_dataframe(
                new_tracks, calculator=self._calculator
            )
        updated_dataset = pandas.concat([self._dataset, new_tracks]).sort_index()
        new_track_ids = new_tracks.index.levels[LEVEL_TRACK_ID]
        new_dataset = updated_dataset.loc[new_track_ids]
        updated_geometry_dataset = self._add_to_geometry_dataset(
            PandasTrackDataset.from_dataframe(new_dataset)
        )
        return PandasTrackDataset.from_dataframe(
            updated_dataset, updated_geometry_dataset
        )

    def _add_to_geometry_dataset(
        self, new_tracks: TrackDataset
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated = dict[RelativeOffsetCoordinate, TrackGeometryDataset]()
        for offset, geometries in self._geometry_datasets.items():
            updated[offset] = geometries.add_all(new_tracks)
        return updated

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
        remaining_tracks = self._dataset.drop(track_id.id, errors="ignore")
        updated_geometry_datasets = self._remove_from_geometry_dataset({track_id})
        return PandasTrackDataset.from_dataframe(
            remaining_tracks, updated_geometry_datasets
        )

    def _remove_from_geometry_dataset(
        self, track_ids: set[TrackId]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated_dataset = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            updated_dataset[offset] = geometry_dataset.remove(track_ids)
        return updated_dataset

    def as_list(self) -> list[Track]:
        if self._dataset.empty:
            return []
        track_ids = self._get_track_ids()
        return [self.__create_track_flyweight(current) for current in track_ids]

    def __create_track_flyweight(self, track_id: str) -> Track:
        track_frame = self._dataset.loc[track_id, :]
        return PandasTrack(track_id, track_frame)

    def as_dataframe(self) -> DataFrame:
        return self._dataset

    def split(self, batches: int) -> Sequence["TrackDataset"]:
        dataset_size = len(self)
        batch_size = ceil(dataset_size / batches)

        new_batches: list["TrackDataset"] = []
        for batch_ids in batched(self._get_track_ids(), batch_size):
            batch_dataset = self._dataset.loc[list(batch_ids), :]
            batch_geometries = self._get_geometries_for(batch_ids)
            new_batches.append(
                PandasTrackDataset.from_dataframe(
                    batch_dataset, batch_geometries, calculator=self._calculator
                )
            )
        return new_batches

    def _get_track_ids(self) -> list[str]:
        if self._dataset.empty:
            return []
        return list(self._dataset.index.get_level_values(LEVEL_TRACK_ID).unique())

    def _get_geometries_for(
        self, track_ids: Iterable[str]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        geometry_datasets = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            geometry_datasets[offset] = geometry_dataset.get_for(track_ids)
        return geometry_datasets

    def __len__(self) -> int:
        return len(self._get_track_ids())

    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        detection_counts_per_track = self._dataset.groupby(level=LEVEL_TRACK_ID).size()
        filtered_ids = detection_counts_per_track[
            detection_counts_per_track > length
        ].index
        filtered_dataset = self._dataset.loc[filtered_ids]
        return PandasTrackDataset(filtered_dataset, calculator=self._calculator)

    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> set[TrackId]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.intersecting_tracks(sections)

    def _get_geometry_dataset_for(
        self, offset: RelativeOffsetCoordinate
    ) -> TrackGeometryDataset:
        """Retrieves track geometries for given offset.

        If offset does not exist, a new TrackGeometryDataset with the applied offset
        will be created and saved.

        Args:
            offset (RelativeOffsetCoordinate): the offset to retrieve track geometries
                for.

        Returns:
            TrackGeometryDataset: the track geometry dataset with the given offset
                applied.
        """
        if (geometry_dataset := self._geometry_datasets.get(offset, None)) is None:
            geometry_dataset = self._track_geometry_factory(self, offset)
            self._geometry_datasets[offset] = geometry_dataset
        return geometry_dataset

    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.intersection_points(sections)

    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.contained_by_sections(sections)


def _assign_track_classification(
    data: DataFrame, calculator: PandasTrackClassificationCalculator
) -> DataFrame:
    dropped = _drop_track_classification(data)
    classification_per_track = calculator.calculate(dropped)
    return dropped.merge(classification_per_track, left_index=True, right_index=True)


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

    if not prepared:
        return DataFrame(prepared)

    df = DataFrame(prepared).set_index(INDEX_NAMES)
    df.index.names = INDEX_NAMES
    return _sort_tracks(df)


def _sort_tracks(track_df: DataFrame) -> DataFrame:
    """Sort the given dataframe by trackId and occurrence.

    Args:
        track_df (DataFrame): dataframe of tracks

    Returns:
        DataFrame: sorted dataframe by track id and frame
    """
    return track_df.sort_index()
