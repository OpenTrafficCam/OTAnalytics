from datetime import datetime, timedelta, timezone

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    RoadUserAssignment,
)
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import Section, SectionId
from tests.utils.builders.event_builder import EventBuilder

_BASE_TIME = datetime(2020, 1, 1, tzinfo=timezone.utc)


def create_assignment(
    distance: float | None,
    start_s: float,
    end_s: float,
    road_user: str = "1",
    road_user_type: str = "car",
) -> RoadUserAssignment:
    """Create an assignment whose events are interpolated at start_s and end_s."""
    start_event = EventBuilder(
        road_user_id=road_user,
        section_id="start",
        interpolated_occurrence=_BASE_TIME + timedelta(seconds=start_s),
    ).build_section_event()
    end_event = EventBuilder(
        road_user_id=road_user,
        section_id="end",
        interpolated_occurrence=_BASE_TIME + timedelta(seconds=end_s),
    ).build_section_event()
    flow = Flow(FlowId("flow"), "flow", SectionId("start"), SectionId("end"), distance)
    return RoadUserAssignment(
        road_user, road_user_type, flow, EventPair(start_event, end_event)
    )


def create_road_user_assignment(
    assignment: RoadUserAssignment,
    start_section: Section,
    end_section: Section,
    max_confidence: float = 0.9,
) -> dict:
    start_event = assignment.events.start
    end_event = assignment.events.end
    metrics = assignment.flow_metrics()

    return {
        ras.FLOW_ID: assignment.assignment.id.id,
        ras.FLOW_NAME: assignment.assignment.name,
        ras.ROAD_USER_ID: assignment.road_user,
        ras.ROAD_USER_TYPE: assignment.road_user_type,
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
        ras.START_DIRECTION_VECTOR_X: start_event.direction_vector.x1,
        ras.START_DIRECTION_VECTOR_Y: start_event.direction_vector.x2,
        ras.END_DIRECTION_VECTOR_X: end_event.direction_vector.x1,
        ras.END_DIRECTION_VECTOR_Y: end_event.direction_vector.x2,
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
        ras.FLOW_DISTANCE_M: metrics.distance_m,
        ras.TRAVEL_TIME_S: metrics.travel_time_s,
        ras.AVG_SPEED_MPS: metrics.avg_speed_mps,
        ras.START_GEO_X: start_event.geo_x,
        ras.START_GEO_Y: start_event.geo_y,
        ras.END_GEO_X: end_event.geo_x,
        ras.END_GEO_Y: end_event.geo_y,
    }
