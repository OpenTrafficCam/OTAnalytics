"""
Parser for Apache Arrow/Feather format files with metadata.

This module provides a TrackParser implementation that reads track data from
feather files and their accompanying metadata JSON files to create TrackParseResult.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, cast

import polars as pl

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.application.logger import logger
from OTAnalytics.application.orthophoto import (
    FALLBACK_GEO_CRS,
    NoOrthophotoGeoreference,
    ProvideOrthophotoGeoreference,
)
from OTAnalytics.application.parser.track_parser import (
    DetectionMetadata,
    TrackParser,
    TrackParseResult,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.georeference import GeoreferenceMetadata, geo_to_pixel_transform
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsByMaxConfidence,
    PolarsTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_parser.convert_ottrk_to_feathers import (
    FEATHER_FILETYPE,
    KEY_DETECTION_CLASSES,
    KEY_DETECTION_METADATA,
    KEY_VIDEO_METADATA,
    METADATA_SUFFIX,
    convert_ottrk_to_feather,
)
from OTAnalytics.plugin_parser.geo_only import is_geo_only
from OTAnalytics.plugin_parser.georeference_parsing import (
    GeoreferenceMetadataParsingMixin,
)
from OTAnalytics.plugin_parser.json_parser import parse_json


def place_on_orthophoto(
    df: pl.DataFrame, georeference: GeoreferenceMetadata
) -> pl.DataFrame:
    """Derive image coordinates from geo coordinates.

    Recomputed on every parse rather than stored in the feather: the feather is
    cached next to the ottrk and must not bind a file to one Orthophoto.

    Args:
        df (pl.DataFrame): detections with geo_x / geo_y.
        georeference (GeoreferenceMetadata): the Orthophoto's mapping.

    Returns:
        pl.DataFrame: the detections with x / y on the Orthophoto's pixels, or
            the detections unchanged if there are none to place.
    """
    if track.GEO_X not in df.columns:
        return df
    transform = geo_to_pixel_transform(georeference)
    return df.with_columns(
        (pl.col(track.GEO_X) * transform.scale_x + transform.offset_x).alias(track.X),
        (pl.col(track.GEO_Y) * transform.scale_y + transform.offset_y).alias(track.Y),
    )


def use_feather_file(file: Path) -> Path:
    if not file.suffix.lower() == FEATHER_FILETYPE:
        if file.suffix.lower() == ".ottrk":
            if not file.with_suffix(FEATHER_FILETYPE).exists():
                convert_ottrk_to_feather(file)
            return file.with_suffix(FEATHER_FILETYPE)
        else:
            raise ValueError(
                f"Input file must have {FEATHER_FILETYPE} or .ottrk extension: {file}"
            )
    return file


class FeathersParser(TrackParser, GeoreferenceMetadataParsingMixin):
    """
    Parse feather files with accompanying metadata JSON files.

    The parser expects two files:
    - A .feather file containing the track data as a pandas DataFrame
    - A _metadata.json file containing detection and video metadata

    For example, if the input file is "data.feather", the parser will also
    look for "data_metadata.json" in the same directory.
    """

    def __init__(
        self,
        track_geometry_factory: Optional[POLARS_TRACK_GEOMETRY_FACTORY] = None,
        orthophoto_georeference: ProvideOrthophotoGeoreference = (
            NoOrthophotoGeoreference()
        ),
    ) -> None:
        """
        Initialize the FeathersParser.

        Args: track_geometry_factory: Factory for creating track geometry datasets.
            If None, uses PandasTrackGeometryDataset.from_track_dataset.
            orthophoto_georeference: Tells where the project's Orthophoto lies.
            Needed to place Geo-only Track Files; by default there is none.
        """
        if track_geometry_factory is None:
            track_geometry_factory = PolarsTrackGeometryDataset.from_track_dataset
        self._track_geometry_factory = track_geometry_factory
        self._orthophoto_georeference = orthophoto_georeference

    def parse(self, file: Path) -> TrackParseResult:
        """Parse feather file and its metadata to create TrackParseResult.

        Args:
            file: Path to the feather file

        Returns:
            TrackParseResult: Contains tracks, detection metadata, and video metadata

        Raises:
            FileNotFoundError: If the feather file or metadata file is not found
        """
        file = use_feather_file(file)

        if not file.exists():
            raise FileNotFoundError(f"Feather file not found: {file}")
        metadata_file = file.parent / f"{file.stem}{METADATA_SUFFIX}"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        df = pl.read_ipc(file)
        metadata = parse_json(metadata_file)

        georeference_metadata = self.parse_georeference_metadata(metadata)
        geo_only = is_geo_only(
            has_georeference=georeference_metadata is not None,
            carries_geo_coordinates=track.GEO_X in df.columns,
            declares_geo_coordinates=ottrk_format.GEO_COORDINATES in metadata,
        )
        if geo_only:
            georeference_metadata = self._orthophoto_georeference.for_crs(
                self._geo_coordinates_crs(metadata, file)
            )
            df = place_on_orthophoto(df, georeference_metadata)

        tracks: TrackDataset = PolarsTrackDataset.from_dataframe(
            df, self._track_geometry_factory, calculator=PolarsByMaxConfidence()
        )
        if georeference_metadata is not None:
            tracks = tracks.with_georeference_metadata(georeference_metadata)

        return TrackParseResult(
            tracks,
            self._parse_detection_metadata(metadata[KEY_DETECTION_METADATA]),
            self._parse_video_metadata(metadata[KEY_VIDEO_METADATA]),
            geo_coordinates_crs=self.parse_geo_coordinates_crs(metadata),
            is_geo_only=geo_only,
        )

    def _geo_coordinates_crs(self, metadata: dict, file: Path) -> str:
        if (crs := self.parse_geo_coordinates_crs(metadata)) is not None:
            return crs
        logger().warning(
            f"'{file.name}' does not say which CRS its geo coordinates are in."
            f" Assuming {FALLBACK_GEO_CRS}."
        )
        return FALLBACK_GEO_CRS

    def _parse_video_metadata(self, metadata: dict) -> VideoMetadata:
        """
        Parse video metadata from the metadata dictionary.

        Args:
            metadata: Dictionary containing video metadata

        Returns:
            VideoMetadata: Parsed video metadata object
        """
        recorded_start_date = datetime.fromtimestamp(
            metadata["recorded_start_date"], tz=timezone.utc
        )

        # Parse optional fields
        expected_duration = None
        if entry := metadata.get("expected_duration"):
            expected_duration = timedelta(seconds=entry)

        actual_fps = metadata.get("actual_fps")

        return VideoMetadata(
            path=metadata["path"],
            recorded_start_date=recorded_start_date,
            expected_duration=expected_duration,
            recorded_fps=metadata["recorded_fps"],
            actual_fps=actual_fps,
            number_of_frames=metadata["number_of_frames"],
        )

    def _parse_detection_metadata(self, metadata: dict) -> DetectionMetadata:
        """
        Parse detection metadata from the metadata dictionary.

        Args:
            metadata: Dictionary containing detection metadata

        Returns:
            DetectionMetadata: Parsed detection metadata object
        """
        detection_classes = frozenset(metadata[KEY_DETECTION_CLASSES])
        return DetectionMetadata(detection_classes)

    def _combine_track_datasets(
        self, parse_results: list[TrackParseResult]
    ) -> TrackDataset:
        datasets = [r.tracks for r in parse_results]
        if all(isinstance(ds, PolarsTrackDataset) for ds in datasets):
            return PolarsTrackDataset.merge_all(
                cast(list[PolarsTrackDataset], datasets)
            )
        return super()._combine_track_datasets(parse_results)
