from enum import StrEnum


class ResourceKey(StrEnum):
    pass


class ConfigurationBarKeys(ResourceKey):
    LABEL_CONFIGURATION_BAR_FORM_HEADER = "label-configuration-bar-form-header"


class AnalysisKeys(ResourceKey):
    LABEL_ANALYSIS = "label-analysis"
    BUTTON_TEXT_EXPORT_EVENT_LIST = "button-export-event_list"
    BUTTON_TEXT_EXPORT_COUNTS = "button-export-counts"
    BUTTON_TEXT_EXPORT_ROAD_USER_ASSIGNMENT = "button-road-user-assignment"
    BUTTON_TEXT_EXPORT_TRACK_STATISTICS = "button-export-track-statistics"


class ProjectKeys(ResourceKey):
    LABEL_OPEN_PROJECT = "label-open-project"
    LABEL_PROJECT_FORM_HEADER = "label-project-form-header"
    LABEL_PROJECT_NAME = "label-project-name"
    LABEL_QUICK_SAVE = "label-quick-save"
    LABEL_SAVE_AS_PROJECT = "label-save-project"
    LABEL_START_DATE = "label-start-date"
    LABEL_START_TIME = "label-start-time"


class SvzMetadataKeys(ResourceKey):
    LABEL_SVZ_METADATA_FORM_HEADER = "label-svz-metadata-form-header"


class AddTracksKeys(ResourceKey):
    BUTTON_ADD_TRACKS = "button-add-tracks"


class OffsetSliderKeys(ResourceKey):
    BUTTON_UPDATE_OFFSET = "button-update-offset"


class VisualizationFiltersKeys(ResourceKey):
    LABEL_VISUALIZATION_FILTERS_FORM_HEADER = "label-visualization-filters-form-header"


class VisualizationLayersKeys(ResourceKey):
    LABEL_VISUALIZATION_LAYERS_FORM_HEADER = "label-visualization-layers-form-header"


class WorkspaceKeys(ResourceKey):
    LABEL_WORKSPACE_FORM_HEADER = "label-workspace-form-header"


DEFAULT_RESOURCE_MAP = {
    AddTracksKeys.BUTTON_ADD_TRACKS: "Add tracks...",
    AnalysisKeys.LABEL_ANALYSIS: "Analysis",
    AnalysisKeys.BUTTON_TEXT_EXPORT_EVENT_LIST: "Export eventlist...",
    AnalysisKeys.BUTTON_TEXT_EXPORT_COUNTS: "Export counts...",
    AnalysisKeys.BUTTON_TEXT_EXPORT_ROAD_USER_ASSIGNMENT: "Export road user assignments...",  # noqa
    AnalysisKeys.BUTTON_TEXT_EXPORT_TRACK_STATISTICS: "Export track statistics",
    ConfigurationBarKeys.LABEL_CONFIGURATION_BAR_FORM_HEADER: "Configuration Bar",
    OffsetSliderKeys.BUTTON_UPDATE_OFFSET: "Update with section offset",
    ProjectKeys.LABEL_OPEN_PROJECT: "Open...",
    ProjectKeys.LABEL_PROJECT_NAME: "Project name",
    ProjectKeys.LABEL_PROJECT_FORM_HEADER: "Project",
    ProjectKeys.LABEL_QUICK_SAVE: "Save",
    ProjectKeys.LABEL_SAVE_AS_PROJECT: "Save as...",
    ProjectKeys.LABEL_START_DATE: "Start date",
    ProjectKeys.LABEL_START_TIME: "Start time",
    SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER: "SVZ",
    VisualizationFiltersKeys.LABEL_VISUALIZATION_FILTERS_FORM_HEADER: "Visualization Filters",  # noqa
    VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER: "Visualization Layers",  # noqa
    WorkspaceKeys.LABEL_WORKSPACE_FORM_HEADER: "Workspace",
}


class ResourceManager:

    def __init__(
        self, resources: dict[ResourceKey, str] = DEFAULT_RESOURCE_MAP
    ) -> None:
        self._resources = resources

    def get(self, key: ResourceKey) -> str:
        return self._resources.get(key, str(key))
