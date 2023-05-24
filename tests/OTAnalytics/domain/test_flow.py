from unittest.mock import Mock

import pytest

from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section


@pytest.fixture
def flow() -> Flow:
    distance = 1.0
    start = Mock(spec=Section)
    end = Mock(spec=Section)
    flow_id = FlowId("some flow")
    return Flow(
        id=flow_id,
        start=start,
        end=end,
        distance=distance,
    )


class TestFlow:
    def test_invalid_distance(self) -> None:
        flow_id = FlowId("some")
        start = Mock(spec=Section)
        end = Mock(spec=Section)
        with pytest.raises(ValueError):
            Flow(flow_id, start=start, end=end, distance=-1)


class TestFlowRepository:
    def test_add_flow(self, flow: Flow) -> None:
        repository = FlowRepository()
        repository.add(flow)

        assert flow in repository.get_all()

    def test_get(self, flow: Flow) -> None:
        repository = FlowRepository()
        repository.add(flow)

        assert flow == repository.get(flow.id)

    def test_get_missing_id(self, flow: Flow) -> None:
        repository = FlowRepository()
        repository.add(flow)

        assert None is repository.get(FlowId("missing flow id"))
