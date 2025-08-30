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

from OTAnalytics.plugin_parser.convert_ottrk_to_feathers import convert_ottrk_to_feather


def main() -> None:
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
