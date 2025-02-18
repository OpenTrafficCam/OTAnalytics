from OTAnalytics.application.analysis.traffic_counting import RoadUserAssignment
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.domain.section import Section


def create_road_user_assignment(
    assignment: RoadUserAssignment,
    start_section: Section,
    end_section: Section,
    max_confidence: float = 0.9,
) -> dict:
    start_event = assignment.events.start
    end_event = assignment.events.end

    return {
        ras.FLOW_ID: assignment.assignment.id.id,
        ras.FLOW_NAME: assignment.assignment.name,
        ras.ROAD_USER_ID: assignment.road_user,
        ras.MAX_CONFIDENCE: max_confidence,
        ras.START_OCCURRENCE: start_event.occurrence.strftime(ras.DATE_TIME_FORMAT),
        ras.START_OCCURRENCE_DATE: start_event.occurrence.strftime(ras.DATE_FORMAT),
        ras.START_OCCURRENCE_TIME: start_event.occurrence.strftime(ras.TIME_FORMAT),
        ras.END_OCCURRENCE: end_event.occurrence.strftime(ras.DATE_TIME_FORMAT),
        ras.END_OCCURRENCE_DATE: end_event.occurrence.strftime(ras.DATE_FORMAT),
        ras.END_OCCURRENCE_TIME: end_event.occurrence.strftime(ras.TIME_FORMAT),
        ras.START_FRAME: start_event.frame_number,
        ras.END_FRAME: end_event.frame_number,
        ras.START_VIDEO_NAME: start_event.video_name,
        ras.END_VIDEO_NAME: end_event.video_name,
        ras.START_SECTION_ID: start_section.id.id,
        ras.END_SECTION_ID: end_section.id.id,
        ras.START_SECTION_NAME: start_section.name,
        ras.END_SECTION_NAME: end_section.name,
        ras.START_EVENT_COORDINATE_X: start_event.event_coordinate.x,
        ras.START_EVENT_COORDINATE_Y: start_event.event_coordinate.y,
        ras.END_EVENT_COORDINATE_X: end_event.event_coordinate.x,
        ras.END_EVENT_COORDINATE_Y: end_event.event_coordinate.y,
        ras.START_DIRECTION_VECTOR_X: start_event.event_coordinate.x,
        ras.START_DIRECTION_VECTOR_Y: start_event.event_coordinate.y,
        ras.END_DIRECTION_VECTOR_X: end_event.event_coordinate.x,
        ras.END_DIRECTION_VECTOR_Y: end_event.event_coordinate.y,
        ras.HOSTNAME: start_event.hostname,
        ras.START_INTERPOLATED_OCCURRENCE: start_event.interpolated_occurrence.strftime(
            ras.DATE_TIME_FORMAT
        ),
        ras.END_INTERPOLATED_OCCURRENCE: end_event.interpolated_occurrence.strftime(
            ras.DATE_TIME_FORMAT
        ),
        ras.START_INTERPOLATED_EVENT_COORD_X: start_event.interpolated_event_coordinate.x,  # noqa
        ras.START_INTERPOLATED_EVENT_COORD_Y: start_event.interpolated_event_coordinate.y,  # noqa
        ras.END_INTERPOLATED_EVENT_COORD_X: end_event.interpolated_event_coordinate.x,
        ras.END_INTERPOLATED_EVENT_COORD_Y: end_event.interpolated_event_coordinate.y,
    }
