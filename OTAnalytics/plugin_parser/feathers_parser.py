"""
Parser for Apache Arrow/Feather format files with metadata.

This module provides a TrackParser implementation that reads track data from
feather files and their accompanying metadata JSON files to create TrackParseResult.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import polars as pl

from OTAnalytics.application.datastore import (
    DetectionMetadata,
    TrackParser,
    TrackParseResult,
    TracksParseResult,
)
from OTAnalytics.application.logger import logger
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
from OTAnalytics.plugin_parser.json_parser import parse_json


def use_feathers_files(files: list[Path]) -> list[Path]:
    raised_exceptions: list[Exception] = []
    result = []
    for file in files:
        try:
            result.append(use_feather_file(file))
        except Exception as cause:
            raised_exceptions.append(cause)
    if raised_exceptions:
        raise ExceptionGroup(
            "Errors occurred while loading the track files:", raised_exceptions
        )
    return result


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


class FeathersParser(TrackParser):
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
    ) -> None:
        """
        Initialize the FeathersParser.

        Args: track_geometry_factory: Factory for creating track geometry datasets.
            If None, uses PandasTrackGeometryDataset.from_track_dataset.
        """
        if track_geometry_factory is None:
            track_geometry_factory = PolarsTrackGeometryDataset.from_track_dataset
        self._track_geometry_factory = track_geometry_factory

    def parse_files(self, files: list[Path]) -> TracksParseResult:
        """
        Parse feather file and its metadata to create TrackParseResult.

        Args:
            file: Path to the feather file

        Returns:
            TrackParseResult: Contains tracks, detection metadata, and video metadata

        Raises:
            FileNotFoundError: If the feather file or metadata file is not found
            ValueError: If the file extension is not .feather
        """
        logger().info(f"Parsing {len(files)} track files...")
        files_to_process = use_feathers_files(files)
        videos_metadata = []
        detections_metadata = []
        data_frames = []
        for file in files_to_process:
            if not file.exists():
                raise FileNotFoundError(f"Feather file not found: {file}")
            # Construct metadata file path
            metadata_file = file.parent / f"{file.stem}{METADATA_SUFFIX}"
            if not metadata_file.exists():
                raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

            # Read the feather file
            df = pl.read_ipc(file)
            data_frames.append(df)

            # Read the metadata
            metadata = parse_json(metadata_file)

            # Parse video metadata
            video_metadata = self._parse_video_metadata(metadata["video_metadata"])
            videos_metadata.append(video_metadata)

            # Parse detection metadata
            detection_metadata = self._parse_detection_metadata(
                metadata["detection_metadata"]
            )
            detections_metadata.append(detection_metadata)
        logger().info(f"{len(files)} track files parsed.")

        df = pl.concat(data_frames)
        # Create TrackDataset from DataFrame
        calculator = PolarsByMaxConfidence()
        tracks = PolarsTrackDataset.from_dataframe(
            df, self._track_geometry_factory, calculator=calculator
        )
        logger().info("TrackDataset created.")
        return TracksParseResult(tracks, detections_metadata, videos_metadata)

    def parse(self, file: Path) -> TrackParseResult:
        """
        Parse feather file and its metadata to create TrackParseResult.

        Args:
            file: Path to the feather file

        Returns:
            TrackParseResult: Contains tracks, detection metadata, and video metadata

        Raises:
            FileNotFoundError: If the feather file or metadata file is not found
            ValueError: If the file extension is not .feather
        """
        file = use_feather_file(file)

        if not file.exists():
            raise FileNotFoundError(f"Feather file not found: {file}")
        # Construct metadata file path
        metadata_file = file.parent / f"{file.stem}{METADATA_SUFFIX}"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        # Read the feather file
        df = pl.read_ipc(file)

        # Read the metadata
        metadata = parse_json(metadata_file)

        # Create TrackDataset from DataFrame
        calculator = PolarsByMaxConfidence()
        tracks = PolarsTrackDataset.from_dataframe(
            df, self._track_geometry_factory, calculator=calculator
        )

        # Parse video metadata
        video_metadata = self._parse_video_metadata(metadata[KEY_VIDEO_METADATA])

        # Parse detection metadata
        detection_metadata = self._parse_detection_metadata(
            metadata[KEY_DETECTION_METADATA]
        )

        return TrackParseResult(tracks, detection_metadata, video_metadata)

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
