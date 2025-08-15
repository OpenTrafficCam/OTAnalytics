"""
Parser for Apache Arrow/Feather format files with metadata.

This module provides a TrackParser implementation that reads track data from
feather files and their accompanying metadata JSON files to create TrackParseResult.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

from OTAnalytics.application.datastore import (
    DetectionMetadata,
    TrackParser,
    TrackParseResult,
)
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    PandasTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser.json_parser import parse_json


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
        track_geometry_factory: Optional[TRACK_GEOMETRY_FACTORY] = None,
    ) -> None:
        """
        Initialize the FeathersParser.

        Args: track_geometry_factory: Factory for creating track geometry datasets.
            If None, uses PandasTrackGeometryDataset.from_track_dataset.
        """
        if track_geometry_factory is None:
            track_geometry_factory = PandasTrackGeometryDataset.from_track_dataset
        self._track_geometry_factory = track_geometry_factory

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
        if not file.exists():
            raise FileNotFoundError(f"Feather file not found: {file}")

        if not file.suffix.lower() == ".feather":
            if file.suffix.lower() == ".ottrk":
                file = file.with_suffix(".feather")
            else:
                raise ValueError(f"Input file must have .feather extension: {file}")

        # Construct metadata file path
        metadata_file = file.parent / f"{file.stem}_metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        # Read the feather file
        df = pd.read_feather(file)

        # Read the metadata
        metadata = parse_json(metadata_file)

        # Create TrackDataset from DataFrame
        calculator = PandasByMaxConfidence()
        tracks = PandasTrackDataset.from_dataframe(
            df, self._track_geometry_factory, calculator=calculator
        )

        # Parse video metadata
        video_metadata = self._parse_video_metadata(metadata["video_metadata"])

        # Parse detection metadata
        detection_metadata = self._parse_detection_metadata(
            metadata["detection_metadata"]
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
        recorded_start_date = datetime.fromisoformat(metadata["recorded_start_date"])

        # Parse optional fields
        expected_duration = None
        if "expected_duration" in metadata:
            expected_duration = timedelta(seconds=metadata["expected_duration"])

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
        detection_classes = frozenset(metadata["detection_classes"])
        return DetectionMetadata(detection_classes)
