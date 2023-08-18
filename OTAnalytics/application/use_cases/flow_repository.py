from OTAnalytics.domain.flow import Flow, FlowRepository


class FlowAlreadyExists(Exception):
    pass


class AddFlow:
    """
    Add a single flow to the repository.
    """

    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def add(self, flow: Flow) -> None:
        if not self.is_flow_name_valid(flow.name):
            raise FlowAlreadyExists(
                f"A flow with the name {flow.name} already exists. "
                "Choose another name."
            )
        self._flow_repository.add(flow)

    def is_flow_name_valid(self, flow_name: str) -> bool:
        if not flow_name:
            return False
        return all(
            stored_flow.name != flow_name
            for stored_flow in self._flow_repository.get_all()
        )
