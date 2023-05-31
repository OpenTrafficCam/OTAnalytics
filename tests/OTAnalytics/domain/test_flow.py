from unittest.mock import Mock

import pytest

from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section


@pytest.fixture
def flow() -> Flow:
    flow_id = FlowId("1")
    name = "some flow"
    start = Mock(spec=Section)
    end = Mock(spec=Section)
    distance = 1.0
    return Flow(
        id=flow_id,
        name=name,
        start=start,
        end=end,
        distance=distance,
    )


class TestFlow:
    def test_invalid_distance(self) -> None:
        flow_id = FlowId("1")
        name = "some"
        start = Mock(spec=Section)
        end = Mock(spec=Section)
        with pytest.raises(ValueError):
            Flow(flow_id, name, start=start, end=end, distance=-1)


@pytest.fixture
def other_flow() -> Flow:
    flow_id = FlowId("2")
    name = "other flow"
    start = Mock(spec=Section)
    end = Mock(spec=Section)
    distance = 1.0
    return Flow(
        id=flow_id,
        name=name,
        start=start,
        end=end,
        distance=distance,
    )


class TestFlowRepository:
    def test_add_flow(self, flow: Flow) -> None:
        repository = FlowRepository()
        repository.add(flow)

        assert flow in repository.get_all()

    def test_add_all_flows(self, flow: Flow, other_flow: Flow) -> None:
        repository = FlowRepository()
        repository.add_all([flow, other_flow])

        assert flow in repository.get_all()

    def test_get(self, flow: Flow) -> None:
        repository = FlowRepository()
        repository.add(flow)

        assert flow == repository.get(flow.id)

    def test_get_missing_id(self, flow: Flow) -> None:
        repository = FlowRepository()
        repository.add(flow)

        assert None is repository.get(FlowId("missing flow id"))
