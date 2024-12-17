from OTAnalytics.application.analysis.traffic_counting import (
    RoadUserAssigner,
    RoadUserAssignment,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository


class GetRoadUserAssignments:
    def __init__(
        self,
        flow_repository: FlowRepository,
        event_repository: EventRepository,
        assigner: RoadUserAssigner,
    ) -> None:
        self._flow_repository = flow_repository
        self._event_repository = event_repository
        self._assigner = assigner

    def get(self) -> list[RoadUserAssignment]:
        return self._assigner.assign(
            self._event_repository.get_all(), self._flow_repository.get_all()
        ).as_list()
