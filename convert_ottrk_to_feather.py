#!/usr/bin/env python3
"""
Script to convert ottrk files to Apache Arrow/Feather format with metadata export.

This script reads one or more ottrk files using the OttrkParser, extracts the pandas
DataFrame, and saves it in Apache Arrow/Feather format. The metadata is saved as a
separate JSON file. Both output files use the same stem as the input file.

Requirements:
    - pyarrow: Required for feather format export (install with: pip install pyarrow)

Usage:
    python convert_ottrk_to_feather.py <input_file1.ottrk> [input_file2.ottrk ...]

Examples:
    # Convert single file
    python convert_ottrk_to_feather.py data/sample.ottrk

    # Convert multiple files python convert_ottrk_to_feather.py data/sample1.ottrk
        data/sample2.ottrk data/sample3.ottrk

    # Convert all ottrk files in a directory using shell globbing
    python convert_ottrk_to_feather.py data/*.ottrk

    Each input file will create:
    - <input_stem>.feather (DataFrame in feather format)
    - <input_stem>_metadata.json (metadata in JSON format)
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

from OTAnalytics.application.datastore import TrackParseResult
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackDataset
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    PandasTrackGeometryDataset,
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


def create_track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    """Create a track geometry factory for PandasTrackDataset."""
    return PandasTrackGeometryDataset.from_track_dataset


def create_ottrk_parser() -> OttrkParser:
    """Create an OttrkParser with the required detection parser."""
    # Create required dependencies for PythonDetectionParser
    track_classification_calculator = PandasByMaxConfidence()
    track_geometry_factory = create_track_geometry_factory()

    # Create detection parser with all required dependencies
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
        "detection_metadata": {
            "detection_classes": list(parse_result.detection_metadata.detection_classes)
        },
        "video_metadata": {
            "path": parse_result.video_metadata.path,
            "recorded_start_date": parse_result.video_metadata.recorded_start_date.isoformat(),  # noqa
            "recorded_fps": parse_result.video_metadata.recorded_fps,
            "number_of_frames": parse_result.video_metadata.number_of_frames,
        },
    }

    # Add optional fields if they exist
    if parse_result.video_metadata.expected_duration is not None:
        metadata["video_metadata"][
            "expected_duration"
        ] = parse_result.video_metadata.expected_duration.total_seconds()

    if parse_result.video_metadata.actual_fps is not None:
        metadata["video_metadata"][
            "actual_fps"
        ] = parse_result.video_metadata.actual_fps

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
    feather_file = output_dir / f"{output_stem}.feather"
    metadata_file = output_dir / f"{output_stem}_metadata.json"

    print(f"Reading ottrk file: {input_file}")

    # Parse the ottrk file
    parser = create_ottrk_parser()
    parse_result = parser.parse(input_file)

    print(f"Parsed {len(parse_result.tracks)} tracks")

    # Convert to pandas dataset if needed
    if isinstance(parse_result.tracks, PythonTrackDataset):
        print("Converting to pandas dataset...")
        track_geometry_factory = create_track_geometry_factory()
        pandas_dataset = convert_to_pandas_dataset(
            parse_result.tracks, track_geometry_factory
        )
    elif isinstance(parse_result.tracks, PandasTrackDataset):
        pandas_dataset = parse_result.tracks
    else:
        raise TypeError(f"Unsupported track dataset type: {type(parse_result.tracks)}")

    # Get the pandas DataFrame
    df = pandas_dataset.get_data()
    print(f"DataFrame shape: {df.shape}")

    # Save DataFrame to feather format
    print(f"Saving DataFrame to: {feather_file}")
    df.to_feather(feather_file)

    # Create and save metadata
    metadata = create_metadata_dict(parse_result)
    print(f"Saving metadata to: {metadata_file}")
    write_json(metadata, metadata_file)

    print("Conversion completed successfully!")
    print("Output files:")
    print(f"  - Data: {feather_file}")
    print(f"  - Metadata: {metadata_file}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert ottrk files to Apache Arrow/Feather format with metadata "
        "export"
    )
    parser.add_argument(
        "input_files",
        type=Path,
        nargs="+",
        help="Path(s) to the input ottrk file(s)",
    )

    args = parser.parse_args()

    # Process each input file
    failed_files = []
    for input_file in args.input_files:
        try:
            convert_ottrk_to_feather(input_file)
        except Exception as e:
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            failed_files.append(input_file)

    # Report overall results
    total_files = len(args.input_files)
    successful_files = total_files - len(failed_files)

    print("\nProcessing complete:")
    print(f"  - Successfully converted: {successful_files}/{total_files} files")

    if failed_files:
        print(f"  - Failed to convert: {len(failed_files)} files")
        for failed_file in failed_files:
            print(f"    * {failed_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
