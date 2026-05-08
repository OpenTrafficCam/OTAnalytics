from typing import Iterable

from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository


class FlowAlreadyExists(Exception):
    pass


class FlowIdAlreadyExists(Exception):
    pass


class AddFlow:
    """
    Add a single flow to the repository.

    Args:
        flow_repository (FlowRepository): the flow repository to add the flow to.
    """

    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def __call__(self, flow: Flow) -> None:
        """Adds flow to the flow repository.

        Raises:
            FlowAlreadyExists: if flow name already exists in repository.
            FlowIdAlreadyExists: if flow id already exists in repository.

        Args:
            flow (Flow): the flow to be added.
        """
        check_flow_already_exists(flow, self._flow_repository.get_all())

        self._flow_repository.add(flow)


def check_flow_already_exists(given: Flow, existing_flows: list[Flow]) -> None:
    if not is_flow_name_valid(given.name, existing_flows):
        raise FlowAlreadyExists(
            f"A flow with the name {given.name} already exists. " "Choose another name."
        )
    existing_flow_ids = {flow.id for flow in existing_flows}
    if not is_flow_id_valid(given.id, existing_flow_ids):
        raise FlowIdAlreadyExists(f"A flow with id {given.id} already exists.")

    if flow_with_same_start_end_section_exists(given, existing_flows):
        raise FlowAlreadyExists("Flow with same start and end section already exists.")


def flow_with_same_start_end_section_exists(
    given: Flow, existing_flows: Iterable[Flow]
) -> bool:
    for existing_flow in existing_flows:
        if existing_flow.start == given.start and existing_flow.end == given.end:
            return True
    return False


def is_flow_name_valid(flow_name: str, existing_flows: Iterable[Flow]) -> bool:
    if not flow_name:
        return False
    return all(stored_flow.name != flow_name for stored_flow in existing_flows)


def is_flow_id_valid(given: FlowId, existing_ids: Iterable[FlowId]) -> bool:
    return not (given in existing_ids)


class ClearAllFlows:
    """Clear the flow repository.

    Args:
        flow_repository: the flow repository to be cleared.
    """

    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def __call__(self) -> None:
        """Clear the flow repository."""
        self._flow_repository.clear()


class GetAllFlows:
    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def get(self) -> list[Flow]:
        return self._flow_repository.get_all()


class AddAllFlows:
    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def add(self, flows: Iterable[Flow]) -> None:
        flow_list = list(flows)

        if not flow_list:
            return

        if not flows_are_unique(flow_list):
            raise FlowAlreadyExists("Flows to be added are not unique.")

        existing_flows = self._flow_repository.get_all()
        for flow in flow_list:
            check_flow_already_exists(flow, existing_flows)

        self._flow_repository.add_all(flow_list)


def flows_are_unique(flows: list[Flow]) -> bool:
    return len(flows) == len(set(flows))
