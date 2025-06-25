from enum import StrEnum
from pathlib import Path

from PIL import Image


class ResourceKey(StrEnum):
    pass


class GeneralKeys(ResourceKey):
    LABEL_APPLY = "label-apply"
    LABEL_CANCEL = "label-cancel"
    LABEL_RESET = "label-reset"
    LABEL_MODES = "label-modes"
    LABEL_EXPORT_OPTIONS = "label-export-options"
    LABEL_EXPORT_MODE = "label-export-mode"
    LABEL_SELECT_OUTPUT_FILE = "label-select-output-file"


class CanvasKeys(ResourceKey):
    LABEL_ADD_SECTION = "label-add-section"
    LABEL_EDIT_SECTION = "label-edit-section"
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


class TrackFormKeys(ResourceKey):
    TAB_ONE = "tab-one"
    TAB_TWO = "tab-two"


class SvzMetadataKeys(ResourceKey):
    LABEL_SVZ_METADATA_FORM_HEADER = "label-svz-metadata-form-header"
    LABEL_TK_NUMBER = "label-tk-number"
    LABEL_COUNTING_LOCATION_NUMBER = "label-counting-location-number"
    LABEL_COUNTING_SELECTION = "label-counting-selection"
    LABEL_DIRECTION_DESCRIPTION = "label-direction-description"
    LABEL_HAS_BICYCLE_LANE = "label-has-bicycle-lane"
    LABEL_IS_BICYCLE_COUNTING = "label-is-bicycle-counting"
    LABEL_COUNTING_DAY_SELECT = "label-counting-day-select"
    LABEL_WEATHER = "label-weather"
    LABEL_REMARK = "label-remark"
    LABEL_COORDINATES = "label-coordinates"
    LABEL_X_COORDINATE = "label-x-coordinate"
    LABEL_Y_COORDINATE = "label-y-coordinate"


class FlowKeys(ResourceKey):
    TABLE_COLUMN_NAME = "table-flow-column-name"
    BUTTON_ADD = "button-add"
    BUTTON_GENERATE = "button-generate"
    BUTTON_PROPERTIES = "button-properties"
    BUTTON_REMOVE = "button-remove"


class FlowAndSectionKeys(ResourceKey):
    TAB_FLOW = "tab-flow"
    TAB_SECTION = "tab-section"


class EditFlowDialogKeys(ResourceKey):
    LABEL_NAME = "Name"
    LABEL_START_SECTION = "Start section"
    LABEL_END_SECTION = "End section"
    LABEL_DISTANCE = "Distance [m]"


class ExportCountsDialogKeys(ResourceKey):
    LABEL_EXPORT_COUNTS = "label-export-counts"
    LABEL_TIME_RANGE = "label-time-range"
    LABEL_START_DATE = "label-start-date"
    LABEL_START_TIME = "label-start-time"
    LABEL_END_DATE = "label-end-date"
    LABEL_END_TIME = "label-end-time"
    LABEL_INTERVAL_MINUTES = "label-interval-minutes"
    LABEL_OUTPUT_FILE = "label-output-file"


class FileChooserDialogKeys(ResourceKey):
    LABEL_FORMAT = "label-format"
    LABEL_FILENAME = "label-filename"
    LABEL_DIRECTORY = "label-directory"
    LABEL_BROWSE = "label-browse"


class AddTracksKeys(ResourceKey):
    BUTTON_ADD_TRACKS = "button-add-tracks"


class AddVideoKeys(ResourceKey):
    BUTTON_ADD_VIDEOS = "button-add-videos"
    BUTTON_REMOVE_VIDEOS = "button-remove-videos"
    TABLE_NAME = "table-name"


class SectionKeys(ResourceKey):
    BUTTON_ADD_LINE = "button-add-line"
    BUTTON_ADD_AREA = "button-add-area"
    BUTTON_EDIT = "button-edit"
    BUTTON_PROPERTIES = "button-properties"
    BUTTON_REMOVE = "button-remove"
    TABLE_COLUMN_NAME = "table-column-name"


class OffsetSliderKeys(ResourceKey):
    LABEL_COORDINATE_X = "label-coordinate-x"
    LABEL_COORDINATE_Y = "label-coordinate-y"


class VisualizationOffsetSliderKeys(ResourceKey):
    BUTTON_UPDATE_OFFSET = "offset-slider-keys-button-update-offset"


class RemarkKeys(ResourceKey):
    LABEL_REMARK_HEADER = "label-remark-header"
    REMARK_NO_COMMENT = "remark-no-comment"


class HotKeys(ResourceKey):
    SAVE_SECTION_HOTKEY = "save-section-hotkey"
    CANCEL_SECTION_GEOMETRY_HOTKEY = "cancel-section-geometry-hotkey"


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
    BUTTON_UPDATE_FLOW_HIGHLIGHTING = "button-update-flow-highlighting"
    LABEL_VISUALIZATION_LAYERS_FORM_HEADER = "label-visualization-layers-form-header"


class WorkspaceKeys(ResourceKey):
    LABEL_WORKSPACE_FORM_HEADER = "label-workspace-form-header"


DEFAULT_RESOURCE_MAP = {
    AddTracksKeys.BUTTON_ADD_TRACKS: "Add tracks...",
    AddVideoKeys.BUTTON_ADD_VIDEOS: "Add videos...",
    AddVideoKeys.BUTTON_REMOVE_VIDEOS: "Remove videos...",
    AddVideoKeys.TABLE_NAME: "Video file",
    AnalysisKeys.LABEL_ANALYSIS: "Analysis",
    AnalysisKeys.BUTTON_TEXT_EXPORT_EVENT_LIST: "Export eventlist...",
    AnalysisKeys.BUTTON_TEXT_EXPORT_COUNTS: "Export counts...",
    AnalysisKeys.BUTTON_TEXT_EXPORT_ROAD_USER_ASSIGNMENT: "Export road user assignments...",  # noqa
    AnalysisKeys.BUTTON_TEXT_EXPORT_TRACK_STATISTICS: "Export track statistics",
    CanvasKeys.LABEL_ADD_SECTION: "Add section",
    CanvasKeys.LABEL_EDIT_SECTION: "Edit section",
    ConfigurationBarKeys.LABEL_CONFIGURATION_BAR_FORM_HEADER: "Configuration Bar",
    FlowAndSectionKeys.TAB_SECTION: "Section",
    FlowAndSectionKeys.TAB_FLOW: "Flow",
    FlowKeys.TABLE_COLUMN_NAME: "Flows",
    FlowKeys.BUTTON_ADD: "Add",
    FlowKeys.BUTTON_GENERATE: "Generate",
    FlowKeys.BUTTON_REMOVE: "Remove",
    FlowKeys.BUTTON_PROPERTIES: "Properties",
    EditFlowDialogKeys.LABEL_NAME: "Name",
    EditFlowDialogKeys.LABEL_START_SECTION: "Start section",
    EditFlowDialogKeys.LABEL_END_SECTION: "End section",
    EditFlowDialogKeys.LABEL_DISTANCE: "Distance",
    GeneralKeys.LABEL_APPLY: "Apply",
    GeneralKeys.LABEL_RESET: "Reset",
    GeneralKeys.LABEL_CANCEL: "Cancel",
    GeneralKeys.LABEL_MODES: "Modes",
    GeneralKeys.LABEL_EXPORT_OPTIONS: "Export Options",
    GeneralKeys.LABEL_EXPORT_MODE: "Export Mode",
    GeneralKeys.LABEL_SELECT_OUTPUT_FILE: "Select Output File",
    FileChooserDialogKeys.LABEL_FORMAT: "Format",
    FileChooserDialogKeys.LABEL_FILENAME: "Filename",
    FileChooserDialogKeys.LABEL_DIRECTORY: "Directory",
    FileChooserDialogKeys.LABEL_BROWSE: "Browse",
    ExportCountsDialogKeys.LABEL_INTERVAL_MINUTES: "Interval (minutes)",
    ExportCountsDialogKeys.LABEL_OUTPUT_FILE: "Output File",
    ExportCountsDialogKeys.LABEL_EXPORT_COUNTS: "Export Counts",
    ExportCountsDialogKeys.LABEL_TIME_RANGE: "Time Range",
    ExportCountsDialogKeys.LABEL_START_DATE: "Start date",
    ExportCountsDialogKeys.LABEL_START_TIME: "Start time",
    ExportCountsDialogKeys.LABEL_END_DATE: "End date",
    ExportCountsDialogKeys.LABEL_END_TIME: "End time",
    OffsetSliderKeys.LABEL_COORDINATE_X: "X:",
    OffsetSliderKeys.LABEL_COORDINATE_Y: "Y:",
    ProjectKeys.LABEL_OPEN_PROJECT: "Open...",
    ProjectKeys.LABEL_PROJECT_NAME: "Project name",
    ProjectKeys.LABEL_PROJECT_FORM_HEADER: "Project",
    ProjectKeys.LABEL_QUICK_SAVE: "Save",
    ProjectKeys.LABEL_SAVE_AS_PROJECT: "Save as...",
    ProjectKeys.LABEL_PROJECT_FORM_HEADER: "Project",
    ProjectKeys.LABEL_QUICK_SAVE: "Save",
    ProjectKeys.LABEL_SAVE_AS_PROJECT: "Save as...",
    RemarkKeys.LABEL_REMARK_HEADER: "Remark",
    RemarkKeys.REMARK_NO_COMMENT: "No Comment",
    SectionKeys.BUTTON_ADD_AREA: "Add area...",
    SectionKeys.BUTTON_ADD_LINE: "Add line...",
    SectionKeys.BUTTON_EDIT: "Edit...",
    SectionKeys.BUTTON_PROPERTIES: "Properties...",
    SectionKeys.BUTTON_REMOVE: "Remove...",
    SectionKeys.TABLE_COLUMN_NAME: "Sections",
    SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER: "SVZ",
    SvzMetadataKeys.LABEL_TK_NUMBER: "TK-Nummer",
    SvzMetadataKeys.LABEL_COUNTING_LOCATION_NUMBER: "Zählstellennummer",
    SvzMetadataKeys.LABEL_DIRECTION_DESCRIPTION: "Ausrichtung",
    SvzMetadataKeys.LABEL_COUNTING_SELECTION: "Zählrichtung (Name aus ZV)",
    SvzMetadataKeys.LABEL_HAS_BICYCLE_LANE: "Seitlicher Radweg vorhanden",
    SvzMetadataKeys.LABEL_IS_BICYCLE_COUNTING: "Fahrradzählung",
    SvzMetadataKeys.LABEL_COUNTING_DAY_SELECT: "Kategorie Zähltag",
    SvzMetadataKeys.LABEL_WEATHER: "Wetter",
    SvzMetadataKeys.LABEL_REMARK: "Bemerkung",
    SvzMetadataKeys.LABEL_COORDINATES: "Geokoordinate",
    SvzMetadataKeys.LABEL_X_COORDINATE: "X Koordinate",
    SvzMetadataKeys.LABEL_Y_COORDINATE: "Y Koordinate",
    TrackFormKeys.TAB_ONE: "Track",
    TrackFormKeys.TAB_TWO: "Videos",
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
    VisualizationLayersKeys.BUTTON_UPDATE_FLOW_HIGHLIGHTING: "Update flow highlighting",
    VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER: "Visualization Layers",  # noqa
    VisualizationOffsetSliderKeys.BUTTON_UPDATE_OFFSET: "Update with section offset",
    WorkspaceKeys.LABEL_WORKSPACE_FORM_HEADER: "Workspace",
}

DEFAULT_IMAGE_RESOURCE_MAP: dict[ResourceKey, str] = {
    CanvasKeys.IMAGE_DEFAULT: r"OTAnalytics/assets/OpenTrafficCam_800.png"
}

DEFAULT_HOTKEYS: dict[HotKeys, str] = {
    HotKeys.SAVE_SECTION_HOTKEY: "Enter",
    HotKeys.CANCEL_SECTION_GEOMETRY_HOTKEY: "Escape",
}


class ResourceManager:

    def __init__(
        self,
        resources: dict[ResourceKey, str] = DEFAULT_RESOURCE_MAP,
        image_resources: dict[ResourceKey, str] = DEFAULT_IMAGE_RESOURCE_MAP,
        hotkeys: dict[HotKeys, str] = DEFAULT_HOTKEYS,
    ) -> None:
        self._resources = resources
        self._image_resources = image_resources
        self._hotkeys = hotkeys

    def get(self, key: ResourceKey) -> str:
        return self._resources.get(key, str(key))

    def get_image(self, key: ResourceKey) -> Image.Image | None:
        if key in self._image_resources:
            return load_image(self._image_resources.get(key))
        return None

    def get_hotkey(self, key: HotKeys) -> str | None:
        return self._hotkeys.get(key)


def load_image(src: str | None) -> Image.Image | None:
    if src is None:
        return None
    if Path(src).exists():
        return Image.open(src)
    return None
