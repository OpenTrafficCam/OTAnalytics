from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.use_cases.flow_repository import (
    AddFlow,
    ClearAllFlows,
    FlowAlreadyExists,
    FlowIdAlreadyExists,
)
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository


@pytest.fixture
def first_flow() -> Mock:
    flow = Mock(spec=Flow)
    flow.id = FlowId("1")
    flow.name = "first"
    return flow


@pytest.fixture
def second_flow() -> Mock:
    flow = Mock(spec=Flow)
    flow.id = FlowId("2")
    flow.name = "second"
    return flow


@pytest.fixture
def flow_repository(first_flow: Mock) -> Mock:
    repository = Mock(spec=FlowRepository)
    repository.get_all.return_value = [first_flow]
    repository.get_flow_ids.return_value = {first_flow.id}
    return repository


class FlowIdAlreaydyExists:
    pass


class TestAddFlow:
    def test_add_flow_with_different_names(
        self, flow_repository: Mock, first_flow: Mock, second_flow: Mock
    ) -> None:
        use_case = AddFlow(flow_repository)

        use_case(second_flow)

        assert flow_repository.add.call_args_list == [
            call(second_flow),
        ]
        flow_repository.get_flow_ids.assert_called_once()

    def test_add_flow_with_same_names(
        self, flow_repository: Mock, first_flow: Mock
    ) -> None:
        flow_repository.get_all.return_value = [first_flow]
        use_case = AddFlow(flow_repository)

        with pytest.raises(FlowAlreadyExists):
            use_case(first_flow)

    def test_add_flow_with_existing_id(
        self, first_flow: Mock, flow_repository: Mock
    ) -> None:
        new_section = Mock(spec=Flow)
        new_section.id = first_flow.id
        new_section.name = "New"

        use_case = AddFlow(flow_repository)

        with pytest.raises(FlowIdAlreadyExists):
            use_case(new_section)


class TestClearAllFlows:
    def test_clear_all_flows(self) -> None:
        flow_repository = Mock(spec=FlowRepository)
        clear_all_flows = ClearAllFlows(flow_repository)
        clear_all_flows()
        flow_repository.clear.assert_called_once()
