from enum import StrEnum
from pathlib import Path

from PIL import Image


class ResourceKey(StrEnum):
    pass


class GeneralKeys(ResourceKey):
    LABEL_APPLY = "label-apply"
    LABEL_RESET = "label-reset"


class CanvasKeys(ResourceKey):
    IMAGE_DEFAULT = "image-default"


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


class RemarkKeys(ResourceKey):
    LABEL_REMARK_HEADER = "label-remark-header"
    REMARK_NO_COMMENT = "remark-no-comment"


class VisualizationFiltersKeys(ResourceKey):
    LABEL_VISUALIZATION_FILTERS_FORM_HEADER = "label-visualization-filters-form-header"
    BUTTON_FILTER_BY_DATE = "button-filter-by-date"
    BUTTON_FILTER_BY_CLASSIFICATION = "button-filter-by-classification"
    LABEL_EVENT = "label-event"
    LABEL_DATE_RANGE_FROM = "label-date-range-from"
    LABEL_DATE_RANGE_TO = "label-date-range-to"
    LABEL_FIRST_DETECTION_OCCURRENCE = "label-first-detection-occurrence"
    LABEL_LAST_DETECTION_OCCURRENCE = "label-last-detection-occurrence"
    LABEL_START_DATE = "label-start-date"
    LABEL_START_TIME = "label-start-time"
    LABEL_END_DATE = "label-end-date"
    LABEL_END_TIME = "label-end-time"
    LABEL_SECONDS = "Seconds"
    LABEL_FRAMES = "Frames"


class TrackStatisticKeys(ResourceKey):
    COLUMN_NAME = "column-name"
    COLUMN_NUMBER = "column-number"
    LABEL_TRACK_STATISTIC_FORM_HEADER = "label-track-statistic-form-header"
    LABEL_ALL_TRACKS = "label-all-tracks"
    LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED = "label-tracks-intersecting-not-assigned"
    LABEL_TRACKS_ASSIGNED_TO_FLOWS = "label-tracks-assigned-to-flows"
    LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS = (
        "label-number-of-tracks-with-simultaneous-section-events"  # noqa
    )
    LABEL_INSIDE_CUTTING_SECTIONS = "label-inside-cutting-sections"
    LABEL_TRACKS_NOT_INTERSECTING_SECTIONS = "label-tracks-not-intersecting-sections"
    LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED = "label-number-of-tracks-to-be-validated"
    TABLE_TRACK_STATISTICS_TITLE = "table-track-statistics-title"


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
    GeneralKeys.LABEL_APPLY: "Apply",
    GeneralKeys.LABEL_RESET: "Reset",
    OffsetSliderKeys.BUTTON_UPDATE_OFFSET: "Update with section offset",
    ProjectKeys.LABEL_OPEN_PROJECT: "Open...",
    ProjectKeys.LABEL_PROJECT_NAME: "Project name",
    ProjectKeys.LABEL_PROJECT_FORM_HEADER: "Project",
    ProjectKeys.LABEL_QUICK_SAVE: "Save",
    ProjectKeys.LABEL_SAVE_AS_PROJECT: "Save as...",
    ProjectKeys.LABEL_START_DATE: "Start date",
    ProjectKeys.LABEL_START_TIME: "Start time",
    RemarkKeys.LABEL_REMARK_HEADER: "Remark",
    RemarkKeys.REMARK_NO_COMMENT: "No Comment",
    SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER: "SVZ",
    TrackStatisticKeys.COLUMN_NAME: "Name",
    TrackStatisticKeys.COLUMN_NUMBER: "Number",
    TrackStatisticKeys.LABEL_TRACK_STATISTIC_FORM_HEADER: "Track Statistics",
    TrackStatisticKeys.LABEL_ALL_TRACKS: "All tracks:",
    TrackStatisticKeys.LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED: "Tracks intersecting not assigned:",  # noqa
    TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS: "Tracks assigend to flows:",
    TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS: "Number of tracks with simultaneous section events",  # noqa
    TrackStatisticKeys.LABEL_INSIDE_CUTTING_SECTIONS: "Inside cutting section:",
    TrackStatisticKeys.LABEL_TRACKS_NOT_INTERSECTING_SECTIONS: "Tracks not intersecting section:",  # noqa
    TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED: "Number of tracks to be validated:",  # noqa
    TrackStatisticKeys.TABLE_TRACK_STATISTICS_TITLE: "Track Statistics",
    VisualizationFiltersKeys.LABEL_VISUALIZATION_FILTERS_FORM_HEADER: "Visualization Filters",  # noqa
    VisualizationFiltersKeys.BUTTON_FILTER_BY_DATE: "Filter by Date",
    VisualizationFiltersKeys.BUTTON_FILTER_BY_CLASSIFICATION: "Filter by Classification",  # noqa
    VisualizationFiltersKeys.LABEL_EVENT: "Event",
    VisualizationFiltersKeys.LABEL_DATE_RANGE_TO: "To",
    VisualizationFiltersKeys.LABEL_DATE_RANGE_FROM: "From",
    VisualizationFiltersKeys.LABEL_LAST_DETECTION_OCCURRENCE: "Last detection occurrence",  # noqa
    VisualizationFiltersKeys.LABEL_FIRST_DETECTION_OCCURRENCE: "First detection occurrence",  # noqa
    VisualizationFiltersKeys.LABEL_START_DATE: "Start date",
    VisualizationFiltersKeys.LABEL_START_TIME: "Start time",
    VisualizationFiltersKeys.LABEL_END_DATE: "End date",
    VisualizationFiltersKeys.LABEL_END_TIME: "End time",
    VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER: "Visualization Layers",  # noqa
    WorkspaceKeys.LABEL_WORKSPACE_FORM_HEADER: "Workspace",
}

DEFAULT_IMAGE_RESOURCE_MAP: dict[ResourceKey, str] = {
    CanvasKeys.IMAGE_DEFAULT: r"OTAnalytics/assets/OpenTrafficCam_800.png"
}


class ResourceManager:

    def __init__(
        self,
        resources: dict[ResourceKey, str] = DEFAULT_RESOURCE_MAP,
        image_resources: dict[ResourceKey, str] = DEFAULT_IMAGE_RESOURCE_MAP,
    ) -> None:
        self._resources = resources
        self._image_resources = image_resources

    def get(self, key: ResourceKey) -> str:
        return self._resources.get(key, str(key))

    def get_image(self, key: ResourceKey) -> Image.Image | None:
        if key in self._image_resources:
            return load_image(self._image_resources.get(key))
        return None


def load_image(src: str | None) -> Image.Image | None:
    if src is None:
        return None
    if Path(src).exists():
        return Image.open(src)
    return None
