from unittest.mock import Mock

from OTAnalytics.domain.flow import Flow, FlowRepository
from OTAnalytics.domain.section import Section


class TestFlowRepository:
    def add_flow(self) -> None:
        distance = 1.0
        start = Mock(spec=Section)
        end = Mock(spec=Section)
        flow = Flow(
            name="some flow",
            start=start,
            end=end,
            distance=distance,
        )
        repository = FlowRepository()
        repository.add(flow)

        assert flow in repository.get_all()
