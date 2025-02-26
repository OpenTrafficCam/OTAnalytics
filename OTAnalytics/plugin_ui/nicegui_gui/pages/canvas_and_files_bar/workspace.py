from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    WorkspaceKeys,
)


class Workspace:
    def __init__(
        self,
        resource_manager: ResourceManager,
    ) -> None:
        self._resource_manager = resource_manager

    def build(self) -> None:
        ui.label(self._resource_manager.get(WorkspaceKeys.LABEL_WORKSPACE_FORM_HEADER))
