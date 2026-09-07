"""Reading the recording start time out of an object's filename.

Filtering has to work from the name alone: deciding whether an object is in the
selected Load Window happens before it is downloaded, and the recorded start
date inside an ottrk is only readable once the bz2 is already on disk.

The convention is shared with OTVision and OTCloud:
`<hostname>_<YYYY-MM-DD_HH-MM-SS>.<ext>`. The digits are UTC, as
`OTVision/helpers/date.py` treats them.
"""

import re
from datetime import datetime, timezone

FILE_NAME_PATTERN = re.compile(
    r".*(?P<start_date>\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}).*"
)
DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"


class NoTimestampInFilename(Exception):
    """Raised when a name carries no timestamp to filter on."""


def parse_timestamp(key: str) -> datetime:
    """Read the recording start time from an object key or filename.

    Args:
        key (str): the S3 object key or plain filename.

    Returns:
        datetime: the recording start time, in UTC.

    Raises:
        NoTimestampInFilename: if the name carries no timestamp.
    """
    match = FILE_NAME_PATTERN.match(key)
    if not match:
        raise NoTimestampInFilename(
            f"'{key}' carries no '{DATE_FORMAT}' timestamp to filter on."
        )
    return datetime.strptime(match.group("start_date"), DATE_FORMAT).replace(
        tzinfo=timezone.utc
    )
