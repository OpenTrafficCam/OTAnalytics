from OTAnalytics.application.export_formats import event_list

START_PREFIX = "start"
END_PREFIX = "end"


def _prepend_start(key: str) -> str:
    return f"{START_PREFIX}_{key}"


def _prepend_end(key: str) -> str:
    return f"{END_PREFIX}_{key}"


FLOW_ID = "flow_id"
FLOW_NAME = "flow_name"
ROAD_USER_ID = event_list.ROAD_USER_ID
ROAD_USER_TYPE = event_list.ROAD_USER_TYPE
MAX_CONFIDENCE = "max_confidence"
START_OCCURRENCE = _prepend_start(event_list.OCCURRENCE)
END_OCCURRENCE = _prepend_end(event_list.OCCURRENCE)
START_OCCURRENCE_DATE = _prepend_start(event_list.OCCURRENCE_DATE)
END_OCCURRENCE_DATE = _prepend_end(event_list.OCCURRENCE_DATE)
START_OCCURRENCE_TIME = _prepend_start(event_list.OCCURRENCE_TIME)
END_OCCURRENCE_TIME = _prepend_end(event_list.OCCURRENCE_TIME)
START_FRAME = _prepend_start(event_list.FRAME_NUMBER)
END_FRAME = _prepend_end(event_list.FRAME_NUMBER)
START_VIDEO_NAME = _prepend_start(event_list.VIDEO_NAME)
END_VIDEO_NAME = _prepend_end(event_list.VIDEO_NAME)
START_SECTION_ID = _prepend_start(event_list.SECTION_ID)
END_SECTION_ID = _prepend_end(event_list.SECTION_ID)
START_SECTION_NAME = _prepend_start(event_list.SECTION_NAME)
END_SECTION_NAME = _prepend_end(event_list.SECTION_NAME)
START_EVENT_COORDINATE_X = _prepend_start(event_list.EVENT_COORDINATE_X)
START_EVENT_COORDINATE_Y = _prepend_start(event_list.EVENT_COORDINATE_Y)
END_EVENT_COORDINATE_X = _prepend_end(event_list.EVENT_COORDINATE_X)
END_EVENT_COORDINATE_Y = _prepend_end(event_list.EVENT_COORDINATE_Y)
START_DIRECTION_VECTOR_X = _prepend_start(event_list.DIRECTION_VECTOR_X)
START_DIRECTION_VECTOR_Y = _prepend_start(event_list.DIRECTION_VECTOR_Y)
END_DIRECTION_VECTOR_X = _prepend_end(event_list.DIRECTION_VECTOR_X)
END_DIRECTION_VECTOR_Y = _prepend_end(event_list.DIRECTION_VECTOR_Y)
START_INTERPOLATED_OCCURRENCE = _prepend_start(event_list.INTERPOLATED_OCCURRENCE)
END_INTERPOLATED_OCCURRENCE = _prepend_end(event_list.INTERPOLATED_OCCURRENCE)
START_INTERPOLATED_EVENT_COORD_X = _prepend_start(
    event_list.INTERPOLATED_EVENT_COORDINATE_X
)
START_INTERPOLATED_EVENT_COORD_Y = _prepend_start(
    event_list.INTERPOLATED_EVENT_COORDINATE_Y
)
END_INTERPOLATED_EVENT_COORD_X = _prepend_end(
    event_list.INTERPOLATED_EVENT_COORDINATE_X
)
END_INTERPOLATED_EVENT_COORD_Y = _prepend_end(
    event_list.INTERPOLATED_EVENT_COORDINATE_Y
)
HOSTNAME = event_list.HOSTNAME

DATE_FORMAT = event_list.DATE_FORMAT
TIME_FORMAT = event_list.TIME_FORMAT
DATE_TIME_FORMAT = event_list.DATE_TIME_FORMAT
