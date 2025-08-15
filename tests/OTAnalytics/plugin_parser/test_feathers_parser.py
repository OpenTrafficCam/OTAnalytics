"""
Tests for the FeathersParser module.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from OTAnalytics.application.datastore import DetectionMetadata, TrackParseResult
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    PandasTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_parser.feathers_parser import FeathersParser


class TestFeathersParser(TestCase):

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = FeathersParser()

        # Sample DataFrame for testing
        self.sample_df = pd.DataFrame(
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

        # Sample metadata for testing
        self.sample_metadata = {
            "detection_metadata": {"detection_classes": ["car", "truck", "bus"]},
            "video_metadata": {
                "path": "test_video.mp4",
                "recorded_start_date": "2023-01-01T10:00:00+00:00",
                "recorded_fps": 30.0,
                "number_of_frames": 900,
                "expected_duration": 30.0,
                "actual_fps": 29.97,
            },
        }

    def test_init_default_geometry_factory(self) -> None:
        """Test initialization with default geometry factory."""
        parser = FeathersParser()
        self.assertEqual(
            parser._track_geometry_factory,
            PandasTrackGeometryDataset.from_track_dataset,
        )

    def test_init_custom_geometry_factory(self) -> None:
        """Test initialization with custom geometry factory."""
        custom_factory = Mock()
        parser = FeathersParser(track_geometry_factory=custom_factory)
        self.assertEqual(parser._track_geometry_factory, custom_factory)

    def test_parse_file_not_found(self) -> None:
        """Test parsing when feather file doesn't exist."""
        non_existent_file = Path("/non/existent/file.feather")

        with self.assertRaises(FileNotFoundError) as context:
            self.parser.parse(non_existent_file)

        self.assertIn("Feather file not found", str(context.exception))

    def test_parse_wrong_extension(self) -> None:
        """Test parsing file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_path = Path(temp_file.name)

            with self.assertRaises(ValueError) as context:
                self.parser.parse(temp_path)

            self.assertIn("must have .feather extension", str(context.exception))

    def test_parse_metadata_file_not_found(self) -> None:
        """Test parsing when metadata file doesn't exist."""
        with tempfile.NamedTemporaryFile(suffix=".feather", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            # Save empty DataFrame to create valid feather file
            pd.DataFrame().to_feather(temp_file.name)

        try:
            with self.assertRaises(FileNotFoundError) as context:
                self.parser.parse(temp_path)

            self.assertIn("Metadata file not found", str(context.exception))
        finally:
            temp_path.unlink()  # Clean up

    @patch("OTAnalytics.plugin_parser.feathers_parser.parse_json")
    @patch("pandas.read_feather")
    @patch("OTAnalytics.plugin_datastore.track_store.PandasTrackDataset.from_dataframe")
    def test_parse_success(
        self, mock_from_dataframe: Mock, mock_read_feather: Mock, mock_parse_json: Mock
    ) -> None:
        """Test successful parsing of feather file and metadata."""
        # Set up mocks
        mock_read_feather.return_value = self.sample_df
        mock_parse_json.return_value = self.sample_metadata
        mock_track_dataset = Mock(spec=PandasTrackDataset)
        mock_from_dataframe.return_value = mock_track_dataset

        with tempfile.NamedTemporaryFile(
            suffix=".feather", delete=False
        ) as feather_file:
            feather_path = Path(feather_file.name)
            # Create the metadata file
            metadata_path = feather_path.parent / f"{feather_path.stem}_metadata.json"
            metadata_path.write_text('{"test": "data"}')

        try:
            result = self.parser.parse(feather_path)

            # Verify result type and structure
            self.assertIsInstance(result, TrackParseResult)
            self.assertEqual(result.tracks, mock_track_dataset)

            # Verify video metadata
            video_metadata = result.video_metadata
            self.assertIsInstance(video_metadata, VideoMetadata)
            self.assertEqual(video_metadata.path, "test_video.mp4")
            self.assertEqual(video_metadata.recorded_fps, 30.0)
            self.assertEqual(video_metadata.number_of_frames, 900)
            self.assertEqual(video_metadata.actual_fps, 29.97)
            self.assertEqual(video_metadata.expected_duration, timedelta(seconds=30.0))

            # Verify detection metadata
            detection_metadata = result.detection_metadata
            self.assertIsInstance(detection_metadata, DetectionMetadata)
            expected_classes = frozenset(["car", "truck", "bus"])
            self.assertEqual(detection_metadata.detection_classes, expected_classes)

            # Verify mock calls
            mock_read_feather.assert_called_once_with(feather_path)
            mock_parse_json.assert_called_once_with(metadata_path)
            mock_from_dataframe.assert_called_once()

        finally:
            # Clean up
            feather_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()

    def test_parse_video_metadata_minimal(self) -> None:
        """Test parsing video metadata with minimal required fields."""
        minimal_metadata = {
            "path": "video.mp4",
            "recorded_start_date": "2023-01-01T10:00:00+00:00",
            "recorded_fps": 30.0,
            "number_of_frames": 900,
        }

        result = self.parser._parse_video_metadata(minimal_metadata)

        self.assertIsInstance(result, VideoMetadata)
        self.assertEqual(result.path, "video.mp4")
        self.assertEqual(result.recorded_fps, 30.0)
        self.assertEqual(result.number_of_frames, 900)
        self.assertIsNone(result.expected_duration)
        self.assertIsNone(result.actual_fps)

    def test_parse_video_metadata_with_optional_fields(self) -> None:
        """Test parsing video metadata with all optional fields."""
        full_metadata = {
            "path": "video.mp4",
            "recorded_start_date": "2023-01-01T10:00:00+00:00",
            "recorded_fps": 30.0,
            "number_of_frames": 900,
            "expected_duration": 30.0,
            "actual_fps": 29.97,
        }

        result = self.parser._parse_video_metadata(full_metadata)

        self.assertIsInstance(result, VideoMetadata)
        self.assertEqual(result.path, "video.mp4")
        self.assertEqual(result.recorded_fps, 30.0)
        self.assertEqual(result.number_of_frames, 900)
        self.assertEqual(result.expected_duration, timedelta(seconds=30.0))
        self.assertEqual(result.actual_fps, 29.97)

    def test_parse_detection_metadata(self) -> None:
        """Test parsing detection metadata."""
        detection_metadata = {
            "detection_classes": ["car", "truck", "bus", "motorcycle"]
        }

        result = self.parser._parse_detection_metadata(detection_metadata)

        self.assertIsInstance(result, DetectionMetadata)
        expected_classes = frozenset(["car", "truck", "bus", "motorcycle"])
        self.assertEqual(result.detection_classes, expected_classes)

    def test_parse_detection_metadata_empty_classes(self) -> None:
        """Test parsing detection metadata with empty classes list."""
        detection_metadata: dict[str, list] = {"detection_classes": []}

        result = self.parser._parse_detection_metadata(detection_metadata)

        self.assertIsInstance(result, DetectionMetadata)
        self.assertEqual(result.detection_classes, frozenset())


if __name__ == "__main__":
    pytest.main([__file__])
