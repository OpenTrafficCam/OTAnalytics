from pathlib import Path
from typing import Any, Dict

from OTAnalytics.application.datastore import TrackParseResult
from OTAnalytics.application.logger import logger
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackDataset
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser.json_parser import write_json
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    OttrkParser,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser

METADATA_SUFFIX = "_metadata.json"
FEATHER_FILETYPE = ".feather"
KEY_DETECTION_METADATA = "detection_metadata"
KEY_DETECTION_CLASSES = "detection_classes"
KEY_VIDEO_METADATA = "video_metadata"


def create_track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    """Create a track geometry factory for PandasTrackDataset."""
    return PolarsTrackGeometryDataset.from_track_dataset


def create_ottrk_parser() -> OttrkParser:
    """Create an OttrkParser with the required detection parser."""
    track_classification_calculator = PandasByMaxConfidence()
    track_geometry_factory = create_track_geometry_factory()

    detection_parser = PandasDetectionParser(
        calculator=track_classification_calculator,
        track_geometry_factory=track_geometry_factory,
        track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
    )
    return OttrkParser(detection_parser)


def convert_to_pandas_dataset(
    python_dataset: PythonTrackDataset, track_geometry_factory: TRACK_GEOMETRY_FACTORY
) -> PandasTrackDataset:
    """Convert PythonTrackDataset to PandasTrackDataset."""
    tracks_list = python_dataset.as_list()
    return PandasTrackDataset.from_list(tracks_list, track_geometry_factory)


def create_metadata_dict(parse_result: TrackParseResult) -> Dict[str, Any]:
    """Create a metadata dictionary from TrackParseResult."""
    metadata = {
        KEY_DETECTION_METADATA: {
            KEY_DETECTION_CLASSES: list(
                parse_result.detection_metadata.detection_classes
            )
        },
        KEY_VIDEO_METADATA: parse_result.video_metadata.to_dict(),
    }
    return metadata


def convert_ottrk_to_feather(input_file: Path) -> None:
    """
    Convert an ottrk file to Apache Arrow/Feather format with metadata export.

    Args:
        input_file: Path to the input ottrk file
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not input_file.suffix.lower() == ".ottrk":
        raise ValueError(f"Input file must have .ottrk extension: {input_file}")

    # Create output file paths using the same stem as input
    output_stem = input_file.stem
    output_dir = input_file.parent
    feather_file = output_dir / f"{output_stem}{FEATHER_FILETYPE}"
    metadata_file = output_dir / f"{output_stem}{METADATA_SUFFIX}"

    logger().info(f"Reading ottrk file: {input_file}")

    # Parse the ottrk file
    parser = create_ottrk_parser()
    parse_result = parser.parse(input_file)

    logger().info(f"Parsed {len(parse_result.tracks)} tracks")

    if isinstance(parse_result.tracks, PandasTrackDataset):
        pandas_dataset = parse_result.tracks
    else:
        raise TypeError(f"Unsupported track dataset type: {type(parse_result.tracks)}")

    # Get the pandas DataFrame
    df = pandas_dataset.get_data()
    logger().info(f"DataFrame shape: {df.shape}")

    # Save DataFrame to feather format
    logger().info(f"Saving DataFrame to: {feather_file}")
    df.to_feather(feather_file)

    # Create and save metadata
    metadata = create_metadata_dict(parse_result)
    logger().info(f"Saving metadata to: {metadata_file}")
    write_json(metadata, metadata_file)

    logger().info("Conversion completed successfully!")
    logger().info("Output files:")
    logger().info(f"  - Data: {feather_file}")
    logger().info(f"  - Metadata: {metadata_file}")
