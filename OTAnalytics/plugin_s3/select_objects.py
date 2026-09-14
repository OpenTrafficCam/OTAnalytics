"""Choosing which S3 objects fall inside the selected Load Window."""

from pathlib import PurePosixPath

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_s3.filename_timestamp import (
    NoTimestampInFilename,
    parse_timestamp,
)


def select_in_window(
    keys: list[str], window: LoadWindow, suffixes: set[str]
) -> list[str]:
    """Select the object keys to load, in recording order.

    Matching is strict start-in-range: an object counts only if the timestamp in
    its own name falls inside the window. A chunk that started before the window
    and runs into it is therefore not loaded, which keeps a selection
    predictable at the cost of the leading partial chunk.

    Objects whose names carry no timestamp are skipped rather than treated as an
    error, because a bucket may hold anything.

    Args:
        keys (list[str]): every object key found under the prefix.
        window (LoadWindow): the selected time range.
        suffixes (set[str]): the file extensions to keep, lower case and dotted.

    Returns:
        list[str]: the matching keys, ordered by their recording start time.
    """
    selected = []
    for key in keys:
        if PurePosixPath(key).suffix.lower() not in suffixes:
            continue
        try:
            timestamp = parse_timestamp(key)
        except NoTimestampInFilename:
            logger().debug(f"Skipping '{key}': no timestamp to filter on.")
            continue
        if window.contains(timestamp):
            selected.append((timestamp, key))
    return [key for _, key in sorted(selected)]
