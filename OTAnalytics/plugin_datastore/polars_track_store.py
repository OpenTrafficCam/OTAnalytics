from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    cast,
)

import numpy
import polars as pl
import shapely
from more_itertools import batched
from shapely.creation import prepare
from shapely.geometry.base import BaseGeometry
from shapely.vectorized import contains

from OTAnalytics.application.logger import logger
from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Detection, Track, TrackId, pack, unpack
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
    EmptyTrackIdSet,
    IntersectionPointsDataset,
    TrackDataset,
    TrackDoesNotExistError,
    TrackIdSet,
    TrackSegmentDataset,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.polars_track_id_set import PolarsTrackIdSet
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    ROW_ID,
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat

RANK = "rank"
MINIMUM_DETECTIONS = 2
OLD_TRACK_ID = "old_track_id"


class PolarsDetection(Detection):
    def __init__(self, track_id: str, row_data: dict, occurrence: datetime):
        self._track_id = track_id
        self._occurrence = occurrence
        self._data = row_data

    @property
    def classification(self) -> str:
        return self.__get_attribute(track.CLASSIFICATION)

    def __get_attribute(self, column: str) -> Any:
        return self._data[column]

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
        if not isinstance(other, PolarsDetection):
            return False
        return (
            self._track_id == other._track_id
            and self._occurrence == other._occurrence
            and self._data == other._data
        )

    def __hash__(self) -> int:
        return hash((self._track_id, self._occurrence))

    def __str__(self) -> str:
        return (
            f"PolarsDetection(track_id={self._track_id}, "
            f"occurrence={self._occurrence}, "
            f"x={self.x}, y={self.y})"
        )

    def __repr__(self) -> str:
        return str(self)


@dataclass
class PolarsTrack(Track):
    _id: str
    _data: pl.DataFrame

    @property
    def id(self) -> TrackId:
        return TrackId(self._id)

    @property
    def original_id(self) -> TrackId:
        return TrackId(self._data.get_column(track.ORIGINAL_TRACK_ID)[0])

    @property
    def classification(self) -> str:
        return self._data.get_column(track.TRACK_CLASSIFICATION)[0]

    @property
    def detections(self) -> list[Detection]:
        detections: list[Detection] = []
        for row in self._data.to_dicts():
            occurrence = row[track.OCCURRENCE]
            detections.append(PolarsDetection(self._id, row, occurrence))
        return detections

    def get_detection(self, index: int) -> Detection:
        row = self._data.row(index, named=True)
        occurrence = row[track.OCCURRENCE]
        return PolarsDetection(self._id, row, occurrence)

    @property
    def first_detection(self) -> Detection:
        row = self._data.row(0, named=True)
        occurrence = row[track.OCCURRENCE]
        return PolarsDetection(self._id, row, occurrence)

    @property
    def last_detection(self) -> Detection:
        row = self._data.row(-1, named=True)
        occurrence = row[track.OCCURRENCE]
        return PolarsDetection(self._id, row, occurrence)


class PolarsTrackClassificationCalculator(ABC):
    @abstractmethod
    def calculate(self, detections: pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError


class PolarsByMaxConfidence(PolarsTrackClassificationCalculator):
    def calculate(self, detections: pl.DataFrame) -> pl.DataFrame:
        if detections.is_empty():
            return pl.DataFrame()

        # Group by track_id and classification, sum confidence, then get max per track
        classifications = (
            detections.select([track.TRACK_ID, track.CLASSIFICATION, track.CONFIDENCE])
            .group_by([track.TRACK_ID, track.CLASSIFICATION])
            .agg(pl.col(track.CONFIDENCE).sum())
            .sort(track.CONFIDENCE)
            .group_by(track.TRACK_ID)
            .last()
            .rename({track.CLASSIFICATION: track.TRACK_CLASSIFICATION})
            .select([track.TRACK_ID, track.TRACK_CLASSIFICATION])
        )
        return classifications


COLUMNS = [
    track.CLASSIFICATION,
    track.CONFIDENCE,
    track.X,
    track.Y,
    track.W,
    track.H,
    track.FRAME,
    track.OCCURRENCE,
    track.INTERPOLATED_DETECTION,
    ottrk_dataformat.FIRST,
    ottrk_dataformat.FINISHED,
    track.VIDEO_NAME,
    track.INPUT_FILE,
    track.TRACK_ID,
    track.TRACK_CLASSIFICATION,
    track.ORIGINAL_TRACK_ID,
]
DEFAULT_CLASSIFICATOR = PolarsByMaxConfidence()
INDEX_NAMES = [track.TRACK_ID, track.OCCURRENCE]
LEVEL_TRACK_ID = track.TRACK_ID
LEVEL_OCCURRENCE = track.OCCURRENCE
CUT_INDICES = "CUT_INDICES"
TRACK_LENGTH = "TRACK_LENGTH"


class PolarsTrackSegmentDataset(TrackSegmentDataset):
    def __init__(self, segments: pl.DataFrame) -> None:
        self._segments = segments

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PolarsTrackSegmentDataset):
            return self._segments.equals(other._segments)
        return False

    def __hash__(self) -> int:
        return hash(str(self._segments))

    def __repr__(self) -> str:
        return repr(self._segments)

    def __str__(self) -> str:
        return repr(self._segments)

    def apply(self, consumer: Callable[[dict], None]) -> None:
        for row in self._segments.to_dicts():
            # Filter out None values to match pandas behavior
            filtered_row = {k: v for k, v in row.items() if v is not None}
            consumer(filtered_row)


class PolarsDataFrameProvider(ABC):
    @abstractmethod
    def get_data(self) -> pl.DataFrame:
        pass


def drop_row_id(df: pl.DataFrame) -> pl.DataFrame:
    return df.drop(ROW_ID, strict=False)


POLARS_TRACK_GEOMETRY_FACTORY = Callable[
    [TrackDataset, RelativeOffsetCoordinate], PolarsTrackGeometryDataset
]


class PolarsTrackDataset(TrackDataset, PolarsDataFrameProvider):
    """High-performance TrackDataset implementation using Polars for vectorized
    operations.

    This implementation leverages Polars DataFrames to provide significant performance
    improvements for large-scale track data processing through vectorized operations.

    Key features:
    - Vectorized intersection calculations
    - Efficient memory usage through lazy evaluation
    - Optimized filtering and aggregation operations

    Note:
        This implementation may have different performance characteristics
        compared to other TrackDataset implementations, particularly for
        small datasets where setup overhead may outweigh benefits.
    """

    @property
    def track_ids(self) -> TrackIdSet:
        if self._dataset.is_empty():
            return PolarsTrackIdSet()
        unique_track_ids = self._dataset.get_column(track.TRACK_ID).unique()
        return PolarsTrackIdSet(unique_track_ids)

    @property
    def first_occurrence(self) -> datetime | None:
        if not len(self):
            return None
        return cast(datetime, self._dataset.get_column(track.OCCURRENCE).min())

    @property
    def last_occurrence(self) -> datetime | None:
        if not len(self):
            return None
        return cast(datetime, self._dataset.get_column(track.OCCURRENCE).max())

    @property
    def classifications(self) -> frozenset[str]:
        if not len(self):
            return frozenset()
        return frozenset(self._dataset.get_column(track.TRACK_CLASSIFICATION).unique())

    @property
    def empty(self) -> bool:
        return self._dataset.is_empty()

    @property
    def track_geometry_factory(self) -> POLARS_TRACK_GEOMETRY_FACTORY:
        return self._track_geometry_factory

    @property
    def calculator(self) -> PolarsTrackClassificationCalculator:
        return self._calculator

    def __init__(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        dataset: pl.DataFrame | None = None,
        geometry_datasets: (
            dict[RelativeOffsetCoordinate, PolarsTrackGeometryDataset] | None
        ) = None,
        calculator: PolarsTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ):
        if dataset is not None:
            self._dataset: pl.DataFrame = dataset
        else:
            self._dataset = create_empty_dataframe()

        self._calculator = calculator
        self._track_geometry_factory = track_geometry_factory
        if geometry_datasets is None:
            self._geometry_datasets = dict[
                RelativeOffsetCoordinate, PolarsTrackGeometryDataset
            ]()
        else:
            self._geometry_datasets = geometry_datasets

    def __iter__(self) -> Iterator[Track]:
        yield from self.as_generator()

    def as_generator(self) -> Generator[Track, None, None]:
        track_ids = self._dataset.get_column(LEVEL_TRACK_ID).unique()
        for track_id in track_ids:
            yield self._create_track_flyweight(track_id)

    @staticmethod
    def from_list(
        tracks: list[Track],
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        calculator: PolarsTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> "PolarsTrackDataset":
        return PolarsTrackDataset.from_dataframe(
            _convert_tracks(tracks),
            track_geometry_factory,
            calculator=calculator,
        )

    @staticmethod
    def from_dataframe(
        tracks: pl.DataFrame,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        geometry_dataset: (
            dict[RelativeOffsetCoordinate, PolarsTrackGeometryDataset] | None
        ) = None,
        calculator: PolarsTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> "PolarsTrackDataset":
        if tracks.is_empty():
            return PolarsTrackDataset(track_geometry_factory)
        tracks = (
            tracks.drop(ROW_ID, strict=False)
            .sort(by=[track.TRACK_ID, track.OCCURRENCE, track.VIDEO_NAME, track.FRAME])
            .with_row_index(ROW_ID)
        )
        result = _assign_track_classification(tracks, calculator)
        return PolarsTrackDataset(
            track_geometry_factory,
            result,
            geometry_datasets=geometry_dataset,
        )

    def add_all(self, other: Iterable[Track]) -> "PolarsTrackDataset":
        new_tracks = self.__get_tracks(other)
        if new_tracks.is_empty():
            return self
        if self._dataset.is_empty():
            return PolarsTrackDataset.from_dataframe(
                new_tracks, self.track_geometry_factory, calculator=self.calculator
            )

        # Ensure new_tracks has track classification before concatenating
        new_tracks_with_classification = _assign_track_classification(
            new_tracks, self.calculator
        )

        # Get all tracks (existing + new) and assign classification
        combined_tracks = pl.concat(
            [
                drop_row_id(self._dataset).select(COLUMNS),
                drop_row_id(new_tracks_with_classification).select(COLUMNS),
            ]
        ).sort(INDEX_NAMES)

        # Re-assign track classification to the combined dataset
        updated_dataset = _assign_track_classification(combined_tracks, self.calculator)

        updated_geometry_dataset = self._add_to_geometry_dataset(
            PolarsTrackDataset.from_dataframe(
                updated_dataset, self.track_geometry_factory
            )
        )
        return PolarsTrackDataset.from_dataframe(
            updated_dataset, self.track_geometry_factory, updated_geometry_dataset
        )

    def __get_tracks(self, other: Iterable[Track]) -> pl.DataFrame:
        if isinstance(other, PolarsDataFrameProvider):
            return other.get_data()
        else:
            return _convert_tracks(other)

    def get_for(self, id: TrackId) -> Optional[Track]:
        track_data = self._dataset.filter(pl.col(LEVEL_TRACK_ID) == unpack(id))
        if track_data.is_empty():
            return None
        return self._create_track_flyweight(unpack(id))

    def clear(self) -> "PolarsTrackDataset":
        return PolarsTrackDataset(self.track_geometry_factory)

    def _create_track_flyweight(self, track_id: str) -> Track:
        """Create a Track flyweight object for the given track_id."""
        track_data = self._dataset.filter(pl.col(LEVEL_TRACK_ID) == track_id)
        return PolarsTrack(track_id, track_data)

    def remove(self, track_id: TrackId) -> "PolarsTrackDataset":
        filtered_data = self._dataset.filter(pl.col(LEVEL_TRACK_ID) != unpack(track_id))
        return PolarsTrackDataset(
            self.track_geometry_factory,
            filtered_data,
            self._geometry_datasets,
            self.calculator,
        )

    def remove_multiple(self, track_ids: TrackIdSet) -> "PolarsTrackDataset":
        track_id_strings = self.__to_raw_ids(track_ids)
        filtered_data = self._dataset.filter(
            ~pl.col(LEVEL_TRACK_ID).is_in(track_id_strings)
        )
        return PolarsTrackDataset(
            self.track_geometry_factory,
            filtered_data,
            self._geometry_datasets,
            self.calculator,
        )

    def __to_raw_ids(self, track_ids: TrackIdSet) -> pl.Series | list:
        if isinstance(track_ids, PolarsTrackIdSet):
            return track_ids._series
        return [unpack(track_id) for track_id in track_ids]

    def as_list(self) -> list[Track]:
        return list(self.as_generator())

    def get_data(self) -> pl.DataFrame:
        return self._dataset

    def __len__(self) -> int:
        return self._dataset.get_column(LEVEL_TRACK_ID).n_unique()

    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> TrackIdSet:
        """Return a set of tracks intersecting a set of sections.

        This implementation uses Polars-based vectorized geometry operations for
        improved performance on large track datasets.

        Args:
            sections (list[Section]): the list of sections to intersect.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            TrackIdSet: the track ids intersecting the given sections.

        Performance:
            O(n*m) where n is number of tracks and m is number of sections,
            but with vectorized operations for significant speedup on large datasets.
        """
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.intersecting_tracks(sections)

    def _get_geometry_dataset_for(
        self, offset: RelativeOffsetCoordinate
    ) -> PolarsTrackGeometryDataset:
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
        return geometry_dataset.wrap_intersection_points(sections)

    def ids_inside(self, sections: list[Section]) -> TrackIdSet:
        result: TrackIdSet = PolarsTrackIdSet()
        for _section in sections:
            contains_masks = self.__calculate_contains_by_section_mask(_section)
            result = result.union(
                PolarsTrackIdSet(
                    self._dataset.filter(contains_masks)
                    .select(pl.col(track.TRACK_ID))
                    .unique()
                    .to_series()
                )
            )
        return result

    def __calculate_contains_by_section_mask(self, section: Section) -> numpy.ndarray:
        section_geom = area_section_to_shapely(section)
        offset = section.get_offset(EventType.SECTION_ENTER)
        x_coords = (
            self._dataset[track.X] + offset.x * self._dataset[track.W]
        ).to_numpy()
        y_coords = (
            self._dataset[track.Y] + offset.y * self._dataset[track.H]
        ).to_numpy()
        return contains(section_geom, x_coords, y_coords)

    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        contains_result: dict[TrackId, list[tuple[SectionId, list[bool]]]] = (
            defaultdict(list)
        )
        for _section in sections:
            contains_masks = self.__calculate_contains_by_section_mask(_section)
            if any(contains_masks):
                temp = (
                    self._dataset.with_columns(
                        pl.Series("contains_mask", contains_masks)
                    )
                    .group_by(pl.col(track.TRACK_ID))
                    .agg(pl.col("contains_mask").alias("grouped"))
                )
                for track_id, contains_mask in temp.iter_rows():
                    contains_result[pack(track_id)].append((_section.id, contains_mask))
        return contains_result

    def _add_to_geometry_dataset(self, dataset: "PolarsTrackDataset") -> dict:
        """Add to geometry dataset - placeholder implementation."""
        return self._geometry_datasets

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        for offset in offsets:
            if offset not in self._geometry_datasets.keys():
                self._geometry_datasets[offset] = self._get_geometry_dataset_for(offset)

    def get_first_segments(self) -> TrackSegmentDataset:
        segments = self.__create_segments()
        if segments.is_empty():
            return PolarsTrackSegmentDataset(segments)

        first_segments = segments.group_by(LEVEL_TRACK_ID, maintain_order=True).first()
        return PolarsTrackSegmentDataset(first_segments)

    def get_last_segments(self) -> TrackSegmentDataset:
        segments = self.__create_segments()
        if segments.is_empty():
            return PolarsTrackSegmentDataset(segments)

        last_segments = segments.group_by(LEVEL_TRACK_ID, maintain_order=True).last()
        return PolarsTrackSegmentDataset(last_segments)

    def __create_segments(self) -> pl.DataFrame:
        """Create track segments from detections."""
        if self._dataset.is_empty():
            schema = {
                track.TRACK_ID: pl.Utf8,
                track.OCCURRENCE: pl.Datetime,
                track.TRACK_CLASSIFICATION: pl.Utf8,
                START_X: pl.Float64,
                START_Y: pl.Float64,
                START_OCCURRENCE: pl.Datetime,
                START_FRAME: pl.Int64,
                START_VIDEO_NAME: pl.Utf8,
                END_X: pl.Float64,
                END_Y: pl.Float64,
                END_OCCURRENCE: pl.Datetime,
                END_FRAME: pl.Int64,
                END_VIDEO_NAME: pl.Utf8,
            }
            return pl.DataFrame(schema=schema)

        data = self._dataset.sort([LEVEL_TRACK_ID, LEVEL_OCCURRENCE])

        # Create shifted columns for start positions
        segments = (
            data.with_columns(
                [
                    pl.col(track.X).shift(1).over(LEVEL_TRACK_ID).alias(START_X),
                    pl.col(track.Y).shift(1).over(LEVEL_TRACK_ID).alias(START_Y),
                    pl.col(track.OCCURRENCE)
                    .shift(1)
                    .over(LEVEL_TRACK_ID)
                    .alias(START_OCCURRENCE),
                    pl.col(track.FRAME)
                    .shift(1)
                    .over(LEVEL_TRACK_ID)
                    .alias(START_FRAME),
                    pl.col(track.VIDEO_NAME)
                    .shift(1)
                    .over(LEVEL_TRACK_ID)
                    .alias(START_VIDEO_NAME),
                ]
            )
            .drop_nulls(
                subset=[
                    START_X,
                    START_Y,
                    START_OCCURRENCE,
                    START_FRAME,
                    START_VIDEO_NAME,
                ]
            )
            .rename(
                {
                    track.X: END_X,
                    track.Y: END_Y,
                    track.OCCURRENCE: END_OCCURRENCE,
                    track.FRAME: END_FRAME,
                    track.VIDEO_NAME: END_VIDEO_NAME,
                }
            )
            .select(
                [
                    track.TRACK_ID,
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
                ]
            )
        )
        return segments

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple["PolarsTrackDataset", TrackIdSet]:
        if len(self) == 0:
            logger().info("No tracks to cut")
            return self, EmptyTrackIdSet()

        geometry_dataset = self._get_geometry_dataset_for(offset)
        new_track_ids = geometry_dataset.track_ids_after_cut(section)
        original_track_ids = PolarsTrackIdSet(
            self._dataset.get_column(track.TRACK_ID).unique()
        )
        old_track_ids = self._dataset.rename({track.TRACK_ID: OLD_TRACK_ID})

        result = old_track_ids.join(new_track_ids, on=ROW_ID, how="left")

        # Keep existing track IDs for rows without a segment match
        # (single detection track)
        result = result.with_columns(
            pl.coalesce([pl.col(track.TRACK_ID), pl.col(OLD_TRACK_ID)]).alias(
                track.TRACK_ID
            )
        ).drop(OLD_TRACK_ID)
        return (
            PolarsTrackDataset.from_dataframe(result, self.track_geometry_factory),
            original_track_ids,
        )

    def filter_by_min_detection_length(self, length: int) -> TrackDataset:
        if self._dataset.is_empty():
            return self

        detection_counts = self._dataset.group_by(LEVEL_TRACK_ID).agg(
            pl.len().alias("count")
        )

        valid_track_ids = (
            detection_counts.filter(pl.col("count") >= length)
            .get_column(LEVEL_TRACK_ID)
            .to_list()
        )

        filtered_dataset = self._dataset.filter(
            pl.col(LEVEL_TRACK_ID).is_in(valid_track_ids)
        )

        return PolarsTrackDataset(
            self.track_geometry_factory, filtered_dataset, calculator=self.calculator
        )

    def get_max_confidences_for(self, track_ids: TrackIdSet) -> dict[str, float]:
        if not track_ids or self._dataset.is_empty():
            return {}

        try:
            track_id_strings = [unpack(track_id) for track_id in track_ids]
            result = (
                self._dataset.filter(pl.col(LEVEL_TRACK_ID).is_in(track_id_strings))
                .group_by(LEVEL_TRACK_ID)
                .agg(pl.col(track.CONFIDENCE).max())
            )

            if result.is_empty():
                raise TrackDoesNotExistError(
                    "Some tracks do not exist in dataset with given id"
                )

            return dict(
                zip(
                    result.get_column(LEVEL_TRACK_ID).to_list(),
                    result.get_column(track.CONFIDENCE).to_list(),
                )
            )
        except Exception as cause:
            raise TrackDoesNotExistError(
                "Some tracks do not exist in dataset with given id"
            ) from cause

    def revert_cuts_for(
        self, original_track_ids: TrackIdSet
    ) -> tuple["PolarsTrackDataset", TrackIdSet, TrackIdSet]:
        if self._dataset.is_empty():
            return self, EmptyTrackIdSet(), EmptyTrackIdSet()

        ids_to_revert = self._get_existing_track_ids(original_track_ids)
        if not ids_to_revert:
            return self, EmptyTrackIdSet(), EmptyTrackIdSet()

        # Revert track IDs back to original IDs
        ids_to_revert_strings = [unpack(track_id) for track_id in ids_to_revert]
        result = self._dataset.with_columns(
            pl.when(pl.col(LEVEL_TRACK_ID).is_in(ids_to_revert_strings))
            .then(pl.col(track.ORIGINAL_TRACK_ID))
            .otherwise(pl.col(LEVEL_TRACK_ID))
            .alias(LEVEL_TRACK_ID)
        )

        return (
            PolarsTrackDataset.from_dataframe(
                result,
                self.track_geometry_factory,
                geometry_dataset=self._geometry_datasets,
                calculator=self.calculator,
            ),
            ids_to_revert,
            ids_to_revert,
        )

    def _get_existing_track_ids(self, track_ids: TrackIdSet) -> TrackIdSet:
        if self._dataset.is_empty():
            return EmptyTrackIdSet()

        converted_ids = [unpack(track_id) for track_id in track_ids]
        existing_ids = (
            self._dataset.filter(pl.col(track.ORIGINAL_TRACK_ID).is_in(converted_ids))
            .get_column(LEVEL_TRACK_ID)
            .unique()
        )
        return PolarsTrackIdSet(existing_ids)

    def split(self, batches: int) -> Sequence["PolarsTrackDataset"]:
        dataset_size = len(self)
        if dataset_size == 0:
            return [self]

        batch_size = ceil(dataset_size / batches)
        track_ids = self._dataset.get_column(LEVEL_TRACK_ID).unique().to_list()

        new_batches = []
        for batch_track_ids in batched(track_ids, batch_size):
            batch_ids_list = list(batch_track_ids)
            batch_dataset = self._dataset.filter(
                pl.col(LEVEL_TRACK_ID).is_in(batch_ids_list)
            )
            batch_geometries = self._get_geometries_for(batch_ids_list)
            new_batches.append(
                PolarsTrackDataset.from_dataframe(
                    batch_dataset,
                    self.track_geometry_factory,
                    batch_geometries,
                    calculator=self.calculator,
                )
            )
        return new_batches

    def _get_geometries_for(
        self, track_ids: list[str]
    ) -> dict[RelativeOffsetCoordinate, PolarsTrackGeometryDataset]:
        geometry_datasets: dict[
            RelativeOffsetCoordinate, PolarsTrackGeometryDataset
        ] = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            geometry_datasets[offset] = geometry_dataset.get_for(track_ids)
        return geometry_datasets

    def remove_by_original_ids(
        self, original_ids: TrackIdSet
    ) -> tuple["PolarsTrackDataset", TrackIdSet]:
        unique_track_ids = self._dataset.get_column(track.ORIGINAL_TRACK_ID).unique()
        self_ids = PolarsTrackIdSet(unique_track_ids)
        ids_to_remove = self_ids.intersection(original_ids)
        filtered_dataset = self._dataset.filter(
            ~pl.col(track.ORIGINAL_TRACK_ID).is_in(
                PolarsTrackIdSet(ids_to_remove)._series
            )
        )

        updated_track_dataset = PolarsTrackDataset(
            dataset=filtered_dataset,
            calculator=self.calculator,
            track_geometry_factory=self.track_geometry_factory,
        )

        return updated_track_dataset, ids_to_remove


def create_empty_dataframe() -> pl.DataFrame:
    """Create an empty Polars DataFrame with the required schema."""
    specified_columns = [
        track.X,
        track.Y,
        track.W,
        track.H,
        track.FRAME,
        track.CONFIDENCE,
        track.INTERPOLATED_DETECTION,
        track.OCCURRENCE,
    ]
    unspecified_columns = set(COLUMNS) - set(specified_columns)
    schema: dict[str, type] = {}
    for col in unspecified_columns:
        schema[col] = pl.Utf8
    # Set specific data types for known columns
    schema[track.X] = pl.Float64
    schema[track.Y] = pl.Float64
    schema[track.W] = pl.Float64
    schema[track.H] = pl.Float64
    schema[track.FRAME] = pl.Int64
    schema[track.CONFIDENCE] = pl.Float64
    schema[track.INTERPOLATED_DETECTION] = pl.Boolean
    schema[track.OCCURRENCE] = pl.Datetime

    return pl.DataFrame(schema=schema)


def _convert_tracks(tracks: Iterable[Track]) -> pl.DataFrame:
    """
    Convert tracks into a Polars dataframe.

    Args:
        tracks (Iterable[Track]): tracks to convert.

    Returns:
        pl.DataFrame: tracks as dataframe.
    """
    if not tracks:
        return create_empty_dataframe()

    prepared: list[dict] = []
    for current_track in list(tracks):
        for detection in current_track.detections:
            dto = detection.to_dict()
            dto[track.ORIGINAL_TRACK_ID] = current_track.original_id.id
            dto[ottrk_dataformat.FIRST] = current_track.first_detection == detection
            dto[ottrk_dataformat.FINISHED] = current_track.last_detection == detection
            prepared.append(dto)

    if not prepared:
        return pl.DataFrame(prepared)

    df = pl.DataFrame(prepared)
    return _sort_tracks(df)


def _sort_tracks(track_df: pl.DataFrame) -> pl.DataFrame:
    """Sort the given dataframe by trackId and occurrence.

    Args:
        track_df (pl.DataFrame): dataframe of tracks

    Returns:
        pl.DataFrame: sorted dataframe by track id and occurrence
    """
    return track_df.sort(INDEX_NAMES)


def _assign_track_classification(
    data: pl.DataFrame, calculator: PolarsTrackClassificationCalculator
) -> pl.DataFrame:
    dropped = _drop_track_classification(data)
    classification_per_track = calculator.calculate(dropped)
    result = dropped.join(classification_per_track, on=track.TRACK_ID, how="left")
    return result


def _drop_track_classification(data: pl.DataFrame) -> pl.DataFrame:
    if track.TRACK_CLASSIFICATION in data.columns:
        return data.drop(track.TRACK_CLASSIFICATION)
    return data


def get_rows_by_track_ids(dataframe: pl.DataFrame, track_ids: list) -> pl.DataFrame:
    """
    Get all rows of a DataFrame corresponding to the given track_ids.

    Args:
        dataframe (pl.DataFrame): DataFrame with track_ids
        track_ids (list[str]): List of track_ids to filter by

    Returns:
        pl.DataFrame: Filtered DataFrame containing only rows with the given track_ids
    """
    if dataframe.is_empty() or len(track_ids) == 0:
        return create_empty_dataframe()

    # Filter the DataFrame to include only rows with track_ids in the provided list
    return dataframe.filter(pl.col(LEVEL_TRACK_ID).is_in(track_ids))


def area_section_to_shapely(section: Section) -> BaseGeometry:
    geometry = shapely.Polygon([(c.x, c.y) for c in section.get_coordinates()])
    prepare(geometry)
    return geometry
