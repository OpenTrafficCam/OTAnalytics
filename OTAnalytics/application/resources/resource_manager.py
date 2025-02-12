from enum import StrEnum


class ResourceKey(StrEnum):
    pass


class ConfigurationBarKeys(ResourceKey):
    LABEL_CONFIGURATION_BAR_FORM_HEADER = "label-configuration-bar-form-header"


class ProjectKeys(ResourceKey):
    LABEL_PROJECT_NAME = "label-project-name"
    LABEL_PROJECT_FORM_HEADER = "label-project-form-header"
    LABEL_OPEN_PROJECT = "label-open-project"
    LABEL_SAVE_AS_PROJECT = "label-save-project"
    LABEL_QUICK_SAVE = "label-quick-save"


class SvzMetadataKeys(ResourceKey):
    LABEL_SVZ_METADATA_FORM_HEADER = "label-svz-metadata-form-header"


class VisualizationFiltersKeys(ResourceKey):
    LABEL_VISUALIZATION_FILTERS_FORM_HEADER = "label-visualization-filters-form-header"


class VisualizationLayersKeys(ResourceKey):
    LABEL_VISUALIZATION_LAYERS_FORM_HEADER = "label-visualization-layers-form-header"


class WorkspaceKeys(ResourceKey):
    LABEL_WORKSPACE_FORM_HEADER = "label-workspace-form-header"


DEFAULT_RESOURCE_MAP = {
    ConfigurationBarKeys.LABEL_CONFIGURATION_BAR_FORM_HEADER: "Configuration Bar",
    ProjectKeys.LABEL_PROJECT_NAME: "Project name",
    ProjectKeys.LABEL_PROJECT_FORM_HEADER: "Project",
    ProjectKeys.LABEL_OPEN_PROJECT: "Open...",
    ProjectKeys.LABEL_SAVE_AS_PROJECT: "Save as...",
    ProjectKeys.LABEL_QUICK_SAVE: "Save",
    SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER: "SVZ",
    VisualizationFiltersKeys.LABEL_VISUALIZATION_FILTERS_FORM_HEADER: "Visualization Filters",  # noqa
    VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER: "Visualization Layers",  # noqa
    WorkspaceKeys.LABEL_WORKSPACE_FORM_HEADER: "Workspace",
}


class ResourceManager:

    def __init__(self) -> None:
        self._resources: dict[ResourceKey, str] = DEFAULT_RESOURCE_MAP

    def get(self, key: ResourceKey) -> str:
        return self._resources.get(key, str(key))
