import platform
from pathlib import Path

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate

LOG_DIR = Path(".logs").absolute()
"""The log save directory."""

GEOMETRY_CACHE_SIZE: int = 20000
CUTTING_SECTION_MARKER: str = "#cut"
DEFAULT_EVENTLIST_FILE_STEM: str = "events"
DEFAULT_EVENTLIST_FILE_TYPE: str = "otevents"
DEFAULT_COUNTS_FILE_STEM: str = "counts"
DEFAULT_COUNTS_FILE_TYPE: str = "csv"
DEFAULT_TRACK_FILE_TYPE: str = "ottrk"
DEFAULT_SECTIONS_FILE_TYPE: str = "otflow"
DEFAULT_COUNTING_INTERVAL_IN_MINUTES: int = 15
DEFAULT_TRACK_OFFSET: RelativeOffsetCoordinate = RelativeOffsetCoordinate(0.5, 0.5)

OS: str = platform.system()
"""OS OTAnalyitcs is currently running on"""

ON_WINDOWS: bool = OS == "Windows"
"""Wether OS is Windows or not"""

ON_LINUX: bool = OS == "Linux"
"""Wether OS is Linux or not"""

ON_MAC: bool = OS == "Darwin"
"""Wether OS is MacOS or not"""

if not (ON_LINUX or ON_WINDOWS or ON_MAC):
    raise RuntimeError("OTAnalytics is running on an unknown platform")
