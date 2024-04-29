import platform
from pathlib import Path

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate

DEFAULT_LOG_DIR = Path("logs").absolute()
"""The log save directory."""

ALLOWED_TRACK_SIZE_PARSING = 5
TRACK_LENGTH_LIMIT = 12000
GEOMETRY_CACHE_SIZE: int = 20000
CUTTING_SECTION_MARKER: str = "#cut"
CLI_CUTTING_SECTION_MARKER: str = "#clicut"
DEFAULT_EVENTLIST_FILE_STEM: str = "events"
DEFAULT_EVENTLIST_FILE_TYPE: str = "otevents"
DEFAULT_COUNTS_FILE_STEM: str = "counts"
DEFAULT_COUNTS_FILE_TYPE: str = "csv"
DEFAULT_COUNT_INTERVAL_TIME_UNIT: str = "min"
DEFAULT_TRACK_FILE_TYPE: str = "ottrk"
DEFAULT_SECTIONS_FILE_TYPE: str = "otflow"
DEFAULT_COUNTING_INTERVAL_IN_MINUTES: int = 15
DEFAULT_TRACK_OFFSET: RelativeOffsetCoordinate = RelativeOffsetCoordinate(0.5, 0.5)
DEFAULT_PROGRESSBAR_STEP_PERCENTAGE: int = 5
DEFAULT_NUM_PROCESSES = 4


# File Types
CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS = "road_user_assignment"
CONTEXT_FILE_TYPE_EVENTS = "events"
OTCONFIG_FILE_TYPE = "otconfig"
OTFLOW_FILE_TYPE = "otflow"

OS: str = platform.system()
"""OS OTAnalytics is currently running on"""

ON_WINDOWS: bool = OS == "Windows"
"""Whether OS is Windows or not"""

ON_LINUX: bool = OS == "Linux"
"""Whether OS is Linux or not"""

ON_MAC: bool = OS == "Darwin"
"""Whether OS is MacOS or not"""

if not (ON_LINUX or ON_WINDOWS or ON_MAC):
    raise RuntimeError("OTAnalytics is running on an unknown platform")
