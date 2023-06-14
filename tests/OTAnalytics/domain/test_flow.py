from unittest.mock import Mock

import pytest

from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId


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
    def test_unset_distance(self) -> None:
        flow_id = FlowId("1")
        name = "some"
        start = Mock(spec=Section)
        end = Mock(spec=Section)

        flow = Flow(flow_id, name, start=start, end=end)

        assert not flow.distance

    def test_invalid_distance(self) -> None:
        flow_id = FlowId("1")
        name = "some"
        start = Mock(spec=Section)
        end = Mock(spec=Section)
        with pytest.raises(ValueError):
            Flow(flow_id, name, start=start, end=end, distance=-1)

    def test_uses_section(self) -> None:
        start = SectionId("1")
        end = SectionId("2")
        flow = Flow(FlowId("1"), name="some", start=start, end=end, distance=1.0)

        assert flow.is_using(start)
        assert flow.is_using(end)
        assert flow.is_using(SectionId("3")) is False


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
    def test_get_id(self) -> None:
        flow = Mock(spec=Flow)
        flow.id = FlowId("3")
        repository = FlowRepository()
        repository.add(flow)

        first_id = repository.get_id()
        second_id = repository.get_id()
        third_id = repository.get_id()

        assert first_id == FlowId("1")
        assert second_id == FlowId("2")
        assert third_id == FlowId("4")

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
