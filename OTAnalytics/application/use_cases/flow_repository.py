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
        self.check_flow_already_exists(flow)

        self._flow_repository.add(flow)

    def check_flow_already_exists(self, flow: Flow) -> None:
        if not self.is_flow_name_valid(flow.name):
            raise FlowAlreadyExists(
                f"A flow with the name {flow.name} already exists. "
                "Choose another name."
            )
        if not self.is_flow_id_valid(flow.id):
            raise FlowIdAlreadyExists(f"A flow with id {flow.id} already exists.")

        if self.flow_with_same_start_end_section_exists(flow):
            raise FlowAlreadyExists(
                "Flow with same start and end section already exists."
            )

    def flow_with_same_start_end_section_exists(self, flow: Flow) -> bool:
        existing_flows = self._flow_repository.get_all()
        for existing_flow in existing_flows:
            if existing_flow.start == flow.start and existing_flow.end == flow.end:
                return True
        return False

    def is_flow_name_valid(self, flow_name: str) -> bool:
        if not flow_name:
            return False
        return all(
            stored_flow.name != flow_name
            for stored_flow in self._flow_repository.get_all()
        )

    def is_flow_id_valid(self, flow_id: FlowId) -> bool:
        return not (flow_id in self._flow_repository.get_flow_ids())


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
    def __init__(self, add_flow: AddFlow) -> None:
        self._add_flow = add_flow

    def add(self, flows: Iterable[Flow]) -> None:
        for flow in flows:
            self._add_flow(flow)
