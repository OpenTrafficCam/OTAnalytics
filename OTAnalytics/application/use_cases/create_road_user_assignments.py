from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignmentRepository,
)
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository


class CreateRoadUserAssignments:
    def __init__(
        self,
        flow_repository: FlowRepository,
        event_repository: EventRepository,
        create_events: CreateEvents,
        assigner: RoadUserAssigner,
        assignment_repository: RoadUserAssignmentRepository,
        enable_event_creation: bool = True,
    ) -> None:
        self._flow_repository = flow_repository
        self._event_repository = event_repository
        self._create_events = create_events
        self._assigner = assigner
        self._assignment_repository = assignment_repository
        self._enable_event_creation = enable_event_creation

    def __call__(self, overwrite_non_empty_repo: bool = False) -> None:
        if self._enable_event_creation and self._event_repository.is_empty():
            self._create_events()

        if self._assignment_repository.is_empty() or overwrite_non_empty_repo:
            events = self._event_repository.get_all()
            flows = self._flow_repository.get_all()
            assigned_flows = self._assigner.assign(events, flows)
            self._assignment_repository.clear()
            self._assignment_repository.add_road_user_assignments(assigned_flows)
