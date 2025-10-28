from abc import ABC, abstractmethod
from bisect import bisect
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Any, Callable, Generator, Iterable, Iterator, Optional, Sequence

import numpy
import pandas
from more_itertools import batched
from pandas import DataFrame, Index, MultiIndex, Series
from pandas._typing import ListLike

from OTAnalytics.application.logger import logger
from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Detection, Track, TrackId, unpack
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TRACK_GEOMETRY_FACTORY,
    EmptyTrackIdSet,
    IntersectionPointsDataset,
    PythonIntersectionPointsDataset,
    TrackDataset,
    TrackDoesNotExistError,
    TrackGeometryDataset,
    TrackIdSet,
    TrackSegmentDataset,
    contains_true,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackIdSet
from OTAnalytics.plugin_parser import ottrk_dataformat

RANK = "rank"
MINIMUM_DETECTIONS = 2


class PandasDetection(Detection):
    def __init__(self, track_id: str, data: Series):
        self._track_id = track_id
        self._occurrence: Any = data.name  # data.name is tuple
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
        frame_number = self.__get_attribute(track.FRAME)
        if isinstance(frame_number, numpy.int64):
            return frame_number.item()
        return frame_number

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

    @property
    def input_file(self) -> str:
        return self.__get_attribute(track.INPUT_FILE)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PandasDetection):
            return False
        # Ensure a builtins.bool is returned (pandas .all() may return numpy.bool_)
        data_equal: bool = bool((self._data == other._data).all())
        return (
            (self._track_id == other._track_id)
            and (self._occurrence == other._occurrence)
            and data_equal
        )

    def __hash__(self) -> int:
        return hash(self._track_id) + hash(self._occurrence) + hash(self._data)


@dataclass
class PandasTrack(Track):
    _id: str
    _data: DataFrame

    @property
    def id(self) -> TrackId:
        return TrackId(self._id)

    @property
    def original_id(self) -> TrackId:
        return TrackId(self._data[track.ORIGINAL_TRACK_ID].iloc[0])

    @property
    def classification(self) -> str:
        return self._data[track.TRACK_CLASSIFICATION].iloc[0]

    @property
    def detections(self) -> list[Detection]:
        return [PandasDetection(self._id, row) for _, row in self._data.iterrows()]

    def get_detection(self, index: int) -> Detection:
        return PandasDetection(self._id, self._data.iloc[index])

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
    def calculate(self, detections: DataFrame) -> DataFrame:
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


COLUMNS = [
    track.CLASSIFICATION,
    track.CONFIDENCE,
    track.X,
    track.Y,
    track.W,
    track.H,
    track.FRAME,
    track.OCCURRENCE,
    ottrk_dataformat.INPUT_FILE_PATH,
    track.INTERPOLATED_DETECTION,
    ottrk_dataformat.FIRST,
    ottrk_dataformat.FINISHED,
    track.VIDEO_NAME,
    track.INPUT_FILE,
    track.TRACK_ID,
    track.TRACK_CLASSIFICATION,
    track.ORIGINAL_TRACK_ID,
]
DEFAULT_CLASSIFICATOR = PandasByMaxConfidence()
INDEX_NAMES = [track.TRACK_ID, track.OCCURRENCE]
LEVEL_TRACK_ID = track.TRACK_ID
LEVEL_OCCURRENCE = track.OCCURRENCE
CUT_INDICES = "CUT_INDICES"
TRACK_LENGTH = "TRACK_LENGTH"


class PandasTrackSegmentDataset(TrackSegmentDataset):
    def __init__(self, segments: DataFrame) -> None:
        self._segments = segments

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PandasTrackSegmentDataset):
            return self._segments.equals(other._segments)
        return False

    def __hash__(self) -> int:
        return hash(self._segments)

    def __repr__(self) -> str:
        return repr(self._segments)

    def __str__(self) -> str:
        return repr(self._segments)

    def apply(self, consumer: Callable[[dict], None]) -> None:
        as_dict = self._segments.reset_index().to_dict("index")

        for value in as_dict.values():
            consumer(value)


class PandasDataFrameProvider:
    @abstractmethod
    def get_data(self) -> DataFrame:
        pass


class PandasTrackDataset(TrackDataset, PandasDataFrameProvider):
    @property
    def track_ids(self) -> TrackIdSet:
        if self._dataset.empty:
            return PythonTrackIdSet()
        track_ids = [
            TrackId(_id)
            for _id in self._dataset.index.get_level_values(LEVEL_TRACK_ID).unique()
        ]
        return PythonTrackIdSet(track_ids)

    @property
    def first_occurrence(self) -> datetime | None:
        if not len(self):
            return None
        return self._dataset.index.get_level_values(LEVEL_OCCURRENCE).min()

    @property
    def last_occurrence(self) -> datetime | None:
        if not len(self):
            return None
        return self._dataset.index.get_level_values(LEVEL_OCCURRENCE).max()

    @property
    def classifications(self) -> frozenset[str]:
        if not len(self):
            return frozenset()
        return frozenset(self._dataset[track.TRACK_CLASSIFICATION].unique())

    @property
    def empty(self) -> bool:
        return self._dataset.empty

    @property
    def track_geometry_factory(self) -> TRACK_GEOMETRY_FACTORY:
        return self._track_geometry_factory

    @property
    def calculator(self) -> PandasTrackClassificationCalculator:
        return self._calculator

    def __init__(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        dataset: DataFrame | None = None,
        geometry_datasets: (
            dict[RelativeOffsetCoordinate, TrackGeometryDataset] | None
        ) = None,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ):
        if dataset is not None:
            self._dataset: DataFrame = dataset
        else:
            self._dataset = create_empty_dataframe()

        self._calculator = calculator
        self._track_geometry_factory = track_geometry_factory
        if geometry_datasets is None:
            self._geometry_datasets = dict[
                RelativeOffsetCoordinate, TrackGeometryDataset
            ]()
        else:
            self._geometry_datasets = geometry_datasets

    def __iter__(self) -> Iterator[Track]:
        yield from self.as_generator()

    def as_generator(self) -> Generator[Track, None, None]:
        if (track_ids := self.get_index()) is None:
            yield from []
        else:
            for current in track_ids.array:
                yield self._create_track_flyweight(current)

    @staticmethod
    def from_list(
        tracks: list[Track],
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> "PandasTrackDataset":
        return PandasTrackDataset.from_dataframe(
            _convert_tracks(tracks),
            track_geometry_factory,
            calculator=calculator,
        )

    @staticmethod
    def from_dataframe(
        tracks: DataFrame,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        geometry_dataset: (
            dict[RelativeOffsetCoordinate, TrackGeometryDataset] | None
        ) = None,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> "PandasTrackDataset":
        if tracks.empty:
            return PandasTrackDataset(track_geometry_factory)
        result = _assign_track_classification(tracks, calculator)
        return PandasTrackDataset(
            track_geometry_factory,
            result,
            geometry_datasets=geometry_dataset,
        )

    def add_all(self, other: Iterable[Track]) -> "PandasTrackDataset":
        new_tracks = self.__get_tracks(other)
        if new_tracks.empty:
            return self
        if self._dataset.empty:
            return PandasTrackDataset.from_dataframe(
                new_tracks, self.track_geometry_factory, calculator=self.calculator
            )
        updated_dataset = pandas.concat([self._dataset, new_tracks]).sort_index()
        new_track_ids = new_tracks.index.unique(LEVEL_TRACK_ID)
        new_dataset = updated_dataset.loc[new_track_ids]
        updated_geometry_dataset = self._add_to_geometry_dataset(
            PandasTrackDataset.from_dataframe(new_dataset, self.track_geometry_factory)
        )
        return PandasTrackDataset.from_dataframe(
            updated_dataset, self.track_geometry_factory, updated_geometry_dataset
        )

    def _add_to_geometry_dataset(
        self, new_tracks: TrackDataset
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated = dict[RelativeOffsetCoordinate, TrackGeometryDataset]()
        for offset, geometries in self._geometry_datasets.items():
            updated[offset] = geometries.add_all(new_tracks)
        return updated

    def __get_tracks(self, other: Iterable[Track]) -> DataFrame:
        if isinstance(other, PandasDataFrameProvider):
            return other.get_data()

        logger().warning(
            "Possible creating track flyweight objects which is really slow in "
            f"'{PandasTrackDataset.__get_tracks.__name__}'."
        )
        return _convert_tracks(other)

    def get_for(self, id: TrackId) -> Optional[Track]:
        if self._dataset.empty:
            return None
        try:
            return self._create_track_flyweight(unpack(id))
        except KeyError:
            return None

    def clear(self) -> "PandasTrackDataset":
        return PandasTrackDataset(self.track_geometry_factory)

    def remove(self, track_id: TrackId) -> "PandasTrackDataset":
        remaining_tracks = self._dataset.drop(unpack(track_id), errors="ignore")
        updated_geometry_datasets = self._remove_from_geometry_dataset([track_id.id])
        return PandasTrackDataset.from_dataframe(
            remaining_tracks, self.track_geometry_factory, updated_geometry_datasets
        )

    def remove_multiple(self, track_ids: TrackIdSet) -> "PandasTrackDataset":
        track_ids_primitive = [unpack(track_id) for track_id in track_ids]
        remaining_tracks = self._dataset.drop(track_ids_primitive, errors="ignore")
        updated_geometry_datasets = self._remove_from_geometry_dataset(
            track_ids_primitive
        )
        return PandasTrackDataset.from_dataframe(
            remaining_tracks, self.track_geometry_factory, updated_geometry_datasets
        )

    def _remove_from_geometry_dataset(
        self, track_ids: Sequence[str]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated_dataset = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            updated_dataset[offset] = geometry_dataset.remove(track_ids)
        return updated_dataset

    def as_list(self) -> list[Track]:
        if (track_ids := self.get_index()) is not None:
            logger().warning(
                "Creating track flyweight objects which is really slow in "
                f"'{PandasTrackDataset.as_list.__name__}'."
            )
            return [self._create_track_flyweight(current) for current in track_ids]

        return []

    def _create_track_flyweight(self, track_id: str) -> Track:
        track_frame = self._dataset.loc[track_id, :]
        if isinstance(track_frame, DataFrame):
            return PandasTrack(track_id, track_frame)
        if isinstance(track_frame, Series):
            return PandasTrack(track_id, track_frame.to_frame(track_id))
        raise NotImplementedError(f"Not implemented for {type(track_frame)}")

    def get_data(self) -> DataFrame:
        return self._dataset

    def split(self, batches: int) -> Sequence["PandasTrackDataset"]:
        dataset_size = len(self)
        batch_size = ceil(dataset_size / batches)

        if (track_ids := self.get_index()) is not None:
            new_batches = []
            for batch_ids in batched(track_ids, batch_size):
                batch_ids_as_list = list(batch_ids)
                batch_dataset = self._dataset.loc[batch_ids_as_list, :]
                batch_geometries = self._get_geometries_for(batch_ids_as_list)
                new_batches.append(
                    PandasTrackDataset.from_dataframe(
                        batch_dataset,
                        self.track_geometry_factory,
                        batch_geometries,
                        calculator=self.calculator,
                    )
                )
            return new_batches

        return [self]

    def get_index(self) -> Index | None:
        if self._dataset.empty:
            return None
        return self._dataset.index.get_level_values(LEVEL_TRACK_ID).unique()

    def _get_geometries_for(
        self, track_ids: list[str]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        geometry_datasets = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            geometry_datasets[offset] = geometry_dataset.get_for(track_ids)
        return geometry_datasets

    def __len__(self) -> int:
        if self._dataset.empty:
            return 0
        return len(self._dataset.index.get_level_values(LEVEL_TRACK_ID).unique())

    def filter_by_min_detection_length(self, length: int) -> TrackDataset:
        detection_counts_per_track: Series[int] = self._dataset.groupby(
            level=LEVEL_TRACK_ID
        )[track.FRAME].size()
        filtered_ids = detection_counts_per_track[
            detection_counts_per_track >= length
        ].index
        filtered_dataset = self._dataset.loc[filtered_ids]
        return PandasTrackDataset(
            self.track_geometry_factory, filtered_dataset, calculator=self.calculator
        )

    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> TrackIdSet:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        intersecting_ids = geometry_dataset.intersecting_tracks(sections)
        return PythonTrackIdSet(intersecting_ids)

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
            geometry_dataset = self.track_geometry_factory(self, offset)
            self._geometry_datasets[offset] = geometry_dataset
        return geometry_dataset

    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> IntersectionPointsDataset:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        intersection_data = geometry_dataset.intersection_points(sections)
        return PythonIntersectionPointsDataset(intersection_data, self)

    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.contained_by_sections(sections)

    def ids_inside(self, sections: list[Section]) -> TrackIdSet:
        results: set[TrackId] = set()
        for cutting_section in sections:
            offset = cutting_section.get_offset(EventType.SECTION_ENTER)
            # set of all tracks where at least one coordinate is contained
            # by at least one cutting section
            results.update(
                set(
                    track_id
                    for track_id, section_data in (
                        self.contained_by_sections([cutting_section], offset).items()
                    )
                    if contains_true(section_data)
                )
            )
        return PythonTrackIdSet(results)

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        for offset in offsets:
            if offset not in self._geometry_datasets.keys():
                self._geometry_datasets[offset] = self._get_geometry_dataset_for(offset)

    def get_first_segments(self) -> TrackSegmentDataset:
        segments = self.__create_segments()
        first_segments: DataFrame = segments.groupby(
            level=LEVEL_TRACK_ID, group_keys=True
        ).head(1)
        return PandasTrackSegmentDataset(first_segments)

    def __create_segments(self) -> DataFrame:
        data: DataFrame = self._dataset.reset_index(level=[LEVEL_OCCURRENCE])
        first_detections = data.groupby(level=LEVEL_TRACK_ID, group_keys=True)
        data[START_X] = first_detections[track.X].shift(1)
        data[START_Y] = first_detections[track.Y].shift(1)
        data[START_OCCURRENCE] = first_detections[track.OCCURRENCE].shift(1)
        data[START_FRAME] = first_detections[track.FRAME].shift(1)
        data[START_VIDEO_NAME] = first_detections[track.VIDEO_NAME].shift(1)
        data.dropna(
            subset=[START_X, START_Y, START_OCCURRENCE, START_FRAME, START_VIDEO_NAME],
            inplace=True,
        )
        segments = data
        segments[START_FRAME] = segments[START_FRAME].astype(
            segments[track.FRAME].dtype
        )
        segments.rename(
            columns={
                track.X: END_X,
                track.Y: END_Y,
                track.OCCURRENCE: END_OCCURRENCE,
                track.FRAME: END_FRAME,
                track.VIDEO_NAME: END_VIDEO_NAME,
            },
            inplace=True,
        )
        final_columns = segments.loc[
            :,
            [
                track.TRACK_CLASSIFICATION,
                START_X,
                START_Y,
                START_OCCURRENCE,
                START_FRAME,
                START_VIDEO_NAME,
                END_X,
                END_Y,
                END_OCCURRENCE,
                END_FRAME,
                END_VIDEO_NAME,
            ],
        ]
        return final_columns

    def get_last_segments(self) -> TrackSegmentDataset:
        segments = self.__create_segments()
        last_segments: DataFrame = segments.groupby(
            level=LEVEL_TRACK_ID, group_keys=True
        ).tail(1)
        return PandasTrackSegmentDataset(last_segments)

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple["PandasTrackDataset", TrackIdSet]:
        if len(self) == 0:
            logger().info("No tracks to cut")
            return self, EmptyTrackIdSet()

        # TODO is this only:
        # - groupby trackid
        # - shift by 1
        # - calculate intersects per segment
        # - cumcount per intersects by track id
        # - add cumcount to track id
        intersection_points = self.intersection_points([section], offset)
        cut_indices = {
            unpack(track_id): [
                ip[1].upper_index
                for ip in sorted(intersection_points, key=lambda ip: ip[1])
            ]
            for track_id, intersection_points in intersection_points.items()
        }
        tracks_to_cut = list(cut_indices.keys())
        cut_tracks_df = self._dataset.loc[tracks_to_cut].copy()
        index_as_df = cut_tracks_df.index.to_frame(
            name=[track.TRACK_ID, track.OCCURRENCE]
        )
        index_as_df["cumcount"] = index_as_df.groupby(level=LEVEL_TRACK_ID).transform(
            "cumcount"
        )
        index_as_df[track.TRACK_ID] = index_as_df.apply(
            lambda row: self._create_cut_track_id(row, cut_indices), axis=1
        )
        cut_tracks_df.index = MultiIndex.from_frame(
            index_as_df[[track.TRACK_ID, track.OCCURRENCE]]
        )
        return PandasTrackDataset(
            self.track_geometry_factory, cut_tracks_df
        ), PythonTrackIdSet(intersection_points.keys())

    def _create_cut_track_id(self, row: Series, cut_info: dict[str, list[int]]) -> str:
        if (track_id := row[track.TRACK_ID]) in cut_info.keys():
            cut_segment_index = bisect(cut_info[track_id], row["cumcount"])
            return f"{track_id}_{cut_segment_index}"
        return row[track.TRACK_ID]

    def get_max_confidences_for(self, track_ids: TrackIdSet) -> dict[str, float]:
        track_id_strings = [track_id.id for track_id in track_ids]
        try:
            return (
                self._dataset.loc[track_id_strings][track.CONFIDENCE]
                .groupby(level=[LEVEL_TRACK_ID])
                .max()
                .to_dict()
            )
        except KeyError as cause:
            raise TrackDoesNotExistError(
                "Some tracks do not exists in dataset with given id"
            ) from cause

    def revert_cuts_for(
        self, original_track_ids: TrackIdSet
    ) -> tuple["PandasTrackDataset", TrackIdSet, TrackIdSet]:
        if self._dataset.empty:
            return self, EmptyTrackIdSet(), EmptyTrackIdSet()
        ids_to_revert = self._get_existing_cut_track_ids(original_track_ids)
        result = self._dataset.reset_index()
        mask_ids_to_revert = result[track.TRACK_ID].isin(ids_to_revert)
        col_reverted_track_ids = result.loc[mask_ids_to_revert, track.ORIGINAL_TRACK_ID]
        result.loc[mask_ids_to_revert, track.TRACK_ID] = col_reverted_track_ids
        result = result.set_index(INDEX_NAMES)
        geometry_dataset = self._remove_from_geometry_dataset(ids_to_revert)

        reverted_track_dataset = PandasTrackDataset.from_dataframe(
            result,
            self.track_geometry_factory,
            geometry_dataset=geometry_dataset,
            calculator=self.calculator,
        )
        removed_ids = to_domain_ids(ids_to_revert)
        reverted_ids = PythonTrackIdSet(
            TrackId(_id) for _id in col_reverted_track_ids.unique()
        )
        return (
            reverted_track_dataset,
            reverted_ids,
            removed_ids,
        )

    def _get_existing_cut_track_ids(self, track_ids: TrackIdSet) -> list[str]:
        """
        Retrieves a list of unique track IDs from the dataset that exist in the provided
        set of track IDs and that also have undergone cutting operations.

        Args:
            track_ids (TrackIdSet): track IDs to be checked against the dataset.

        Returns:
            list[str]: unique track IDs from the dataset that are found in the provided
            set of track IDs and have undergone cutting operations.
        """
        raw_ids = to_raw_ids(track_ids)

        mask_cut_tracks = (
            self._dataset.index.get_level_values(LEVEL_TRACK_ID)
            != self._dataset[track.ORIGINAL_TRACK_ID]
        )
        mask_existing_ids = self._dataset[track.ORIGINAL_TRACK_ID].isin(raw_ids)

        return list(
            self._dataset.loc[mask_cut_tracks & mask_existing_ids].index.unique(
                LEVEL_TRACK_ID
            )
        )

    def remove_by_original_ids(
        self, original_ids: TrackIdSet
    ) -> tuple["PandasTrackDataset", TrackIdSet]:
        raw_ids = to_raw_ids(original_ids)

        mask_remove = self._dataset[track.ORIGINAL_TRACK_ID].isin(raw_ids)
        ids_to_remove = list(
            self._dataset.loc[mask_remove]
            .index.get_level_values(LEVEL_TRACK_ID)
            .unique()
        )
        filtered_dataset = self._dataset.loc[~mask_remove]
        updated_geometry_dataset = self._remove_from_geometry_dataset(ids_to_remove)

        updated_track_dataset = PandasTrackDataset(
            dataset=filtered_dataset,
            calculator=self.calculator,
            track_geometry_factory=self.track_geometry_factory,
            geometry_datasets=updated_geometry_dataset,
        )
        removed_track_ids = to_domain_ids(ids_to_remove)

        return updated_track_dataset, PythonTrackIdSet(removed_track_ids)


def to_raw_ids(track_ids: Iterable[TrackId]) -> frozenset[str]:
    return frozenset((track_id.id for track_id in track_ids))


def to_domain_ids(raw_ids: Iterable[str]) -> TrackIdSet:
    return PythonTrackIdSet((TrackId(raw_id) for raw_id in raw_ids))


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
    if not tracks:
        return create_empty_dataframe()
    prepared: list[dict] = []
    for current_track in list(tracks):
        for detection in current_track.detections:
            dto = detection.to_dict()
            dto[track.ORIGINAL_TRACK_ID] = current_track.original_id.id
            prepared.append(dto)

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


def create_empty_dataframe() -> DataFrame:
    return DataFrame(columns=COLUMNS).set_index(INDEX_NAMES)


def get_rows_by_track_ids(dataframe: DataFrame, track_ids: ListLike) -> DataFrame:
    """
    Get all rows of a DataFrame corresponding to the given track_ids.

    Args:
        dataframe (DataFrame): DataFrame with track_ids in the index
        track_ids (list[str]): List of track_ids to filter by

    Returns:
        DataFrame: Filtered DataFrame containing only rows with the specified track_ids
    """
    if dataframe.empty or len(track_ids) == 0:
        return create_empty_dataframe()

    # Filter the DataFrame to include only rows with track_ids in the provided list
    return dataframe.loc[
        dataframe.index.get_level_values(LEVEL_TRACK_ID).isin(track_ids)
    ]
