from unittest.mock import Mock

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    RoadUserAssignment,
    RoadUserAssignmentRepository,
)
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import SectionId


class TestRoadUserAssignmentRepository:

    def test_remove_assignment_of_event(self) -> None:
        """
        Fix bug OP#8926 - dictionary changed size during iteration
        """
        start_event = Mock()
        start_event.road_user_id = "road_user_1"
        end_event = Mock()
        end_event.road_user_id = "road_user_1"
        assignment = RoadUserAssignment(
            road_user="road_user_1",
            road_user_type="car",
            assignment=Flow(
                id=FlowId("flow_1"),
                name="Flow 1",
                start=SectionId("0"),
                end=SectionId("1"),
            ),
            events=EventPair(start=start_event, end=end_event),
        )
        repository = RoadUserAssignmentRepository(track_id_set_factory=Mock())
        repository.add(assignment)

        repository.remove_assignments_of_event(start_event)

        assert repository.get_all().as_list() == []
