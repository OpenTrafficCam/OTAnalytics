"""
Tests for the FeathersParser module.
"""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from OTAnalytics.application.datastore import DetectionMetadata, TrackParseResult
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_datastore.polars_track_store import PolarsTrackDataset
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_parser.feathers_parser import FeathersParser


@pytest.fixture
def parser() -> FeathersParser:
    """Create a FeathersParser instance for testing."""
    return FeathersParser()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "track_id": ["1", "1", "2", "2"],
            "frame": [1, 2, 1, 2],
            "x": [100.0, 105.0, 200.0, 205.0],
            "y": [100.0, 105.0, 200.0, 205.0],
            "w": [50.0, 50.0, 60.0, 60.0],
            "h": [80.0, 80.0, 90.0, 90.0],
            "classification": ["car", "car", "truck", "truck"],
            "confidence": [0.9, 0.85, 0.92, 0.88],
            "occurrence": [
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
            ],
            "video_name": [
                "test_video.mp4",
                "test_video.mp4",
                "test_video.mp4",
                "test_video.mp4",
            ],
            "input_file": ["test.ottrk", "test.ottrk", "test.ottrk", "test.ottrk"],
            "interpolated_detection": [False, False, False, False],
            "original_track_id": ["1", "1", "2", "2"],
        }
    )


GIVEN_RECORDED_START_DATE = 1672574400.0  # 2022-01-01T10:00:00 as timestamp
EXPECTED_RECORDED_START_DATE = datetime.fromtimestamp(
    GIVEN_RECORDED_START_DATE, tz=timezone.utc
)


@pytest.fixture
def sample_metadata() -> dict[str, Any]:
    """Create sample metadata for testing."""
    return {
        "detection_metadata": {"detection_classes": ["car", "truck", "bus"]},
        "video_metadata": {
            "path": "test_video.mp4",
            "recorded_start_date": GIVEN_RECORDED_START_DATE,
            "recorded_fps": 30.0,
            "number_of_frames": 900,
            "expected_duration": 30.0,
            "actual_fps": 29.97,
        },
    }


class TestFeathersParser:

    def test_init_default_geometry_factory(self) -> None:
        """Test initialization with default geometry factory."""
        parser = FeathersParser()
        assert (
            parser._track_geometry_factory
            == PolarsTrackGeometryDataset.from_track_dataset
        )

    def test_init_custom_geometry_factory(self) -> None:
        """Test initialization with custom geometry factory."""
        custom_factory = Mock()
        parser = FeathersParser(track_geometry_factory=custom_factory)
        assert parser._track_geometry_factory == custom_factory

    def test_parse_file_not_found(self, parser: FeathersParser) -> None:
        """Test parsing when feather file doesn't exist."""
        non_existent_file = Path("/non/existent/file.feather")

        with pytest.raises(FileNotFoundError) as exc_info:
            parser.parse(non_existent_file)

        assert "Feather file not found" in str(exc_info.value)

    def test_parse_wrong_extension(self, parser: FeathersParser) -> None:
        """Test parsing file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_path = Path(temp_file.name)

            with pytest.raises(ValueError) as exc_info:
                parser.parse(temp_path)

            assert "must have .feather or .ottrk extension" in str(exc_info.value)

    def test_parse_metadata_file_not_found(self, parser: FeathersParser) -> None:
        """Test parsing when metadata file doesn't exist."""
        with tempfile.NamedTemporaryFile(suffix=".feather", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            # Save empty DataFrame to create valid feather file
            pd.DataFrame().to_feather(temp_file.name)

        try:
            with pytest.raises(FileNotFoundError) as exc_info:
                parser.parse(temp_path)

            assert "Metadata file not found" in str(exc_info.value)
        finally:
            temp_path.unlink()  # Clean up

    @patch("OTAnalytics.plugin_parser.feathers_parser.parse_json")
    @patch("polars.read_ipc")
    @patch(
        "OTAnalytics.plugin_datastore.polars_track_store."
        "PolarsTrackDataset.from_dataframe"
    )
    def test_parse_success(
        self,
        mock_from_dataframe: Mock,
        mock_read_ipc: Mock,
        mock_parse_json: Mock,
        parser: FeathersParser,
        sample_df: pd.DataFrame,
        sample_metadata: dict[str, Any],
    ) -> None:
        """Test successful parsing of feather file and metadata."""
        # Set up mocks
        mock_read_ipc.return_value = sample_df
        mock_parse_json.return_value = sample_metadata
        mock_track_dataset = Mock(spec=PolarsTrackDataset)
        mock_from_dataframe.return_value = mock_track_dataset

        with tempfile.NamedTemporaryFile(
            suffix=".feather", delete=False
        ) as feather_file:
            feather_path = Path(feather_file.name)
            # Create the metadata file
            metadata_path = feather_path.parent / f"{feather_path.stem}_metadata.json"
            metadata_path.write_text('{"test": "data"}')

        try:
            result = parser.parse(feather_path)

            # Verify result type and structure
            assert isinstance(result, TrackParseResult)
            assert result.tracks == mock_track_dataset

            # Verify video metadata
            video_metadata = result.video_metadata
            assert isinstance(video_metadata, VideoMetadata)
            assert video_metadata.path == "test_video.mp4"
            assert video_metadata.start == EXPECTED_RECORDED_START_DATE
            assert video_metadata.recorded_fps == 30.0
            assert video_metadata.number_of_frames == 900
            assert video_metadata.actual_fps == 29.97
            assert video_metadata.expected_duration == timedelta(seconds=30.0)

            # Verify detection metadata
            detection_metadata = result.detection_metadata
            assert isinstance(detection_metadata, DetectionMetadata)
            expected_classes = frozenset(["car", "truck", "bus"])
            assert detection_metadata.detection_classes == expected_classes

            # Verify mock calls
            mock_read_ipc.assert_called_once_with(feather_path)
            mock_parse_json.assert_called_once_with(metadata_path)
            mock_from_dataframe.assert_called_once()

        finally:
            # Clean up
            feather_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()

    def test_parse_video_metadata_minimal(self, parser: FeathersParser) -> None:
        """Test parsing video metadata with minimal required fields."""
        minimal_metadata = {
            "path": "video.mp4",
            "recorded_start_date": GIVEN_RECORDED_START_DATE,
            "recorded_fps": 30.0,
            "number_of_frames": 900,
        }

        result = parser._parse_video_metadata(minimal_metadata)

        assert isinstance(result, VideoMetadata)
        assert result.path == "video.mp4"
        assert result.start == EXPECTED_RECORDED_START_DATE
        assert result.recorded_fps == 30.0
        assert result.number_of_frames == 900
        assert result.expected_duration is None
        assert result.actual_fps is None

    def test_parse_video_metadata_with_optional_fields(
        self, parser: FeathersParser
    ) -> None:
        """Test parsing video metadata with all optional fields."""
        full_metadata = {
            "path": "video.mp4",
            "recorded_start_date": GIVEN_RECORDED_START_DATE,
            "recorded_fps": 30.0,
            "number_of_frames": 900,
            "expected_duration": 30.0,
            "actual_fps": 29.97,
        }

        result = parser._parse_video_metadata(full_metadata)

        assert isinstance(result, VideoMetadata)
        assert result.path == "video.mp4"
        assert result.recorded_fps == 30.0
        assert result.number_of_frames == 900
        assert result.expected_duration == timedelta(seconds=30.0)
        assert result.actual_fps == 29.97
        assert result.start == EXPECTED_RECORDED_START_DATE

    def test_parse_detection_metadata(self, parser: FeathersParser) -> None:
        """Test parsing detection metadata."""
        detection_metadata = {
            "detection_classes": ["car", "truck", "bus", "motorcycle"]
        }

        result = parser._parse_detection_metadata(detection_metadata)

        assert isinstance(result, DetectionMetadata)
        expected_classes = frozenset(["car", "truck", "bus", "motorcycle"])
        assert result.detection_classes == expected_classes

    def test_parse_detection_metadata_empty_classes(
        self, parser: FeathersParser
    ) -> None:
        """Test parsing detection metadata with empty classes list."""
        detection_metadata: dict[str, list] = {"detection_classes": []}

        result = parser._parse_detection_metadata(detection_metadata)

        assert isinstance(result, DetectionMetadata)
        assert result.detection_classes == frozenset()
