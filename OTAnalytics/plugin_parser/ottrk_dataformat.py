"""Defines the dictionary keys to access an ottrk file.
"""
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"

# Ottrk Data Format
METADATA = "metadata"
DETECTIONS = "detections"
DATA = "data"

# METADATA
OTDET_VERSION = "otdet_version"
VIDEO = "video"
FILENAME = "filename"
FILETYPE = "filetype"
WIDTH = "width"
HEIGHT = "height"
RECORDED_FPS = "recorded_fps"
NUMBER_OF_FRAMES = "number_of_frames"
RECORDED_START_DATE = "recorded_start_date"
LENGTH = "length"
OTVISION_VERSION = "otvision_version"
MODEL = "model"
NAME = "name"
WEIGHTS = "weights"
IOU_THRESHOLD = "iou_threshold"
IMAGE_SIZE = "image_size"
MAX_CONFIDENCE = "max_confidence"
HALF_PRECISION = "half_precision"
CLASSES = "classes"
CHUNKSIZE = "chunksize"
NOMRALIZED_BBOX = "normalized_bbox"
OTTRK_VERSION = "ottrk_version"
TRACKING = "tracking"
OTVISION_VERSION = "otvision_version"
FIRST_TRACKED_VIDEO_START = "first_tracked_video_start"
LAST_TRACKED_VIDEO_END = "last_tracked_video_end"
TRACKER = "tracker"
SIGMA_L = "sigma_l"
SIGMA_H = "sigma_h"
SIGMA_IOU = "sigma_iou"
T_MIN = "t_min"
T_MISS_MAX = "t_miss_max"

# DETECTION
CLASS = "class"
CONFIDENCE = "confidence"
X = "x"
Y = "y"
W = "w"
H = "h"
FRAME = "frame"
OCCURENCE = "occurrence"
INPUT_FILE_PATH = "input_file_path"
INTERPOLATED_DETECTION = "interpolated-detection"
FIRST = "first"
FINISHED = "finished"
TRACK_ID = "track-id"
