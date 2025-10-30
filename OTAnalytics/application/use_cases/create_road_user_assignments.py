from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssigner,
    RoadUserAssignmentRepository,
)
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.event_repository import GetAllEnterSectionEvents
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows


class CreateRoadUserAssignments:
    def __init__(
        self,
        get_all_flows: GetAllFlows,
        get_all_section_events: GetAllEnterSectionEvents,
        # TODO are section enter events sufficient for flow assignment?
        create_events: CreateEvents,
        assigner: RoadUserAssigner,
        assignment_repository: RoadUserAssignmentRepository,
        enable_event_creation: bool = True,
    ) -> None:
        self._get_all_flows = get_all_flows
        self._get_all_section_events = get_all_section_events
        self._create_events = create_events
        self._assigner = assigner
        self._assignment_repository = assignment_repository
        self._enable_event_creation = enable_event_creation

    def __call__(self, overwrite_non_empty_repo: bool = False) -> None:
        # TODO maybe move event creation completely outside of this use case?
        if self._enable_event_creation:
            self._create_events()

        events = self._get_all_section_events.get()
        flows = self._get_all_flows.get()
        assigned_flows = self._assigner.assign(events, flows)

        # TODO think about when to recompute and where to trigger

        # no harm adding assignments for track_id,flow that already exist -> overwritten
        self._assignment_repository.add_road_user_assignments(assigned_flows)
