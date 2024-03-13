from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.use_cases.flow_repository import (
    AddAllFlows,
    AddFlow,
    ClearAllFlows,
    FlowAlreadyExists,
    FlowIdAlreadyExists,
    GetAllFlows,
)
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import SectionId


@pytest.fixture
def first_flow() -> Mock:
    flow = Mock(spec=Flow)
    flow.id = FlowId("1")
    flow.name = "first"
    flow.start = SectionId("section_1")
    flow.end = SectionId("section_2")
    return flow


@pytest.fixture
def second_flow() -> Mock:
    flow = Mock(spec=Flow)
    flow.id = FlowId("2")
    flow.name = "second"
    flow.start = SectionId("section_3")
    flow.end = SectionId("section_4")
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

    def test_add_flow_fails_with_existing_start_end_section(
        self, first_flow: Flow, second_flow: Mock, flow_repository: Mock
    ) -> None:
        second_flow.name = first_flow.name + "suffix"
        second_flow.start = first_flow.start
        second_flow.end = first_flow.end

        use_case = AddFlow(flow_repository)
        with pytest.raises(FlowAlreadyExists):
            use_case(second_flow)


class TestClearAllFlows:
    def test_clear_all_flows(self) -> None:
        flow_repository = Mock(spec=FlowRepository)
        clear_all_flows = ClearAllFlows(flow_repository)
        clear_all_flows()
        flow_repository.clear.assert_called_once()


class TestGetAllFlows:
    def test_get(self) -> None:
        expected_flows = Mock()
        flow_repository = Mock(spec=FlowRepository)
        flow_repository.get_all.return_value = expected_flows
        get_all_flows = GetAllFlows(flow_repository)
        actual_flows = get_all_flows.get()
        assert actual_flows == expected_flows
        flow_repository.get_all.assert_called_once()


class TestAddAllFlows:
    def test_add(self, first_flow: Flow, second_flow: Flow) -> None:
        add_flow = Mock()
        add_all_flows = AddAllFlows(add_flow)

        add_all_flows.add([first_flow, second_flow])

        assert add_flow.call_args_list == [
            call(first_flow),
            call(second_flow),
        ]
