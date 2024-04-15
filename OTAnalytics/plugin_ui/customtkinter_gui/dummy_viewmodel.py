import contextlib
import functools
from datetime import datetime
from pathlib import Path
from time import sleep
from tkinter.filedialog import askopenfilename, askopenfilenames
from typing import Any, Iterable, Optional

from OTAnalytics.adapter_ui.abstract_button_quick_save_config import (
    AbstractButtonQuickSaveConfig,
)
from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameProject
from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.abstract_main_window import AbstractMainWindow
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.default_values import (
    DATETIME_FORMAT,
    RELATIVE_SECTION_OFFSET,
    SUPPORTED_FORMATS,
)
from OTAnalytics.adapter_ui.flow_adapter import (
    GeometricCenterCalculator,
    InnerSegmentsCenterCalculator,
    SectionRefPointCalculator,
)
from OTAnalytics.adapter_ui.view_model import (
    MetadataProvider,
    MissingCoordinate,
    ViewModel,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.application import (
    CancelAddFlow,
    CancelAddSection,
    MultipleFlowsSelected,
    MultipleSectionsSelected,
    OTAnalyticsApplication,
)
from OTAnalytics.application.config import (
    CUTTING_SECTION_MARKER,
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
)
from OTAnalytics.application.logger import logger
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.playback import SkipTime
from OTAnalytics.application.use_cases.config import MissingDate
from OTAnalytics.application.use_cases.config_has_changed import NoExistingConfigFound
from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.application.use_cases.export_events import (
    EventListExporter,
    ExporterNotFoundError,
)
from OTAnalytics.application.use_cases.flow_repository import FlowAlreadyExists
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.application.use_cases.quick_save_configuration import (
    NoExistingFileToSave,
)
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportSpecification,
)
from OTAnalytics.application.use_cases.save_otflow import NoSectionsToSave
from OTAnalytics.domain import geometry
from OTAnalytics.domain.date import (
    DateRange,
    validate_date,
    validate_hour,
    validate_minute,
    validate_second,
)
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import Flow, FlowId, FlowListObserver
from OTAnalytics.domain.section import (
    COORDINATES,
    ID,
    NAME,
    RELATIVE_OFFSET_COORDINATES,
    Area,
    LineSection,
    MissingSection,
    Section,
    SectionId,
    SectionListObserver,
    SectionRepositoryEvent,
)
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent
from OTAnalytics.domain.types import EventType
from OTAnalytics.domain.video import DifferentDrivesException, Video, VideoListObserver
from OTAnalytics.plugin_ui.customtkinter_gui import toplevel_export_events
from OTAnalytics.plugin_ui.customtkinter_gui.frame_sections import COLUMN_SECTION
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import ask_for_save_file_path
from OTAnalytics.plugin_ui.customtkinter_gui.line_section import (
    ArrowPainter,
    CanvasElementDeleter,
    SectionBuilder,
    SectionGeometryEditor,
    SectionPainter,
)
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox, MinimalInfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.style import (
    ARROW_STYLE,
    COLOR_ORANGE,
    DEFAULT_SECTION_STYLE,
    EDITED_SECTION_STYLE,
    PRE_EDIT_SECTION_STYLE,
    SELECTED_KNOB_STYLE,
    SELECTED_SECTION_STYLE,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_export_counts import (
    END,
    EXPORT_FILE,
    EXPORT_FORMAT,
    INTERVAL,
    START,
    CancelExportCounts,
    ToplevelExportCounts,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_export_events import (
    CancelExportEvents,
    ToplevelExportEvents,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_flows import (
    DISTANCE,
    END_SECTION,
    FLOW_ID,
    FLOW_NAME,
    START_SECTION,
    ToplevelFlows,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import ColumnResource

MESSAGE_CONFIGURATION_NOT_SAVED = "The configuration has not been saved.\n"
SUPPORTED_VIDEO_FILE_TYPES = ["*.avi", "*.mkv", "*.mov", "*.mp4"]
TAG_SELECTED_SECTION: str = "selected_section"
LINE_SECTION: str = "line_section"
TO_SECTION = "to_section"
FROM_SECTION = "from_section"
OTFLOW = "otflow"
MISSING_TRACK_FRAME_MESSAGE = "tracks frame"
MISSING_VIDEO_FRAME_MESSAGE = "videos frame"
MISSING_VIDEO_CONTROL_FRAME_MESSAGE = "video control frame"
MISSING_SECTION_FRAME_MESSAGE = "sections frame"
MISSING_FLOW_FRAME_MESSAGE = "flows frame"
MISSING_ANALYSIS_FRAME_MESSAGE = "analysis frame"
OTCONFIG = "otconfig"


class MissingInjectedInstanceError(Exception):
    """Raise when no instance of an object was injected before referencing it"""

    def __init__(self, injected_object: str):
        message = (
            f"An instance of {injected_object} has to be injected before referencing it"
        )
        super().__init__(message)


def flow_id(from_section: str, to_section: str) -> str:
    return f"{from_section} -> {to_section}"


def action(func: Any) -> Any:
    @functools.wraps(func)
    def wrapper_decorator(self: Any, *args: Any, **kwargs: Any) -> Any:
        self._start_action()
        try:
            value = func(self, *args, **kwargs)
            return value
        finally:
            self._finish_action()

    return wrapper_decorator


class DummyViewModel(
    ViewModel,
    VideoListObserver,
    TrackListObserver,
    SectionListObserver,
    FlowListObserver,
):

    def __init__(
        self,
        application: OTAnalyticsApplication,
        flow_parser: FlowParser,
        name_generator: FlowNameGenerator,
        event_list_export_formats: dict,
    ) -> None:
        self._application = application
        self._flow_parser: FlowParser = flow_parser
        self._name_generator = name_generator
        self._event_list_export_formats = event_list_export_formats
        self._window: Optional[AbstractMainWindow] = None
        self._frame_project: Optional[AbstractFrameProject] = None
        self._frame_tracks: Optional[AbstractFrameTracks] = None
        self._frame_videos: Optional[AbstractFrame] = None
        self._frame_canvas: Optional[AbstractFrameCanvas] = None
        self._frame_video_control: Optional[AbstractFrame] = None
        self._frame_sections: Optional[AbstractFrame] = None
        self._frame_flows: Optional[AbstractFrame] = None
        self._frame_filter: Optional[AbstractFrameFilter] = None
        self._frame_analysis: Optional[AbstractFrame] = None
        self._canvas: Optional[AbstractCanvas] = None
        self._frame_track_plotting: Optional[AbstractFrameTrackPlotting] = None
        self._treeview_sections: Optional[AbstractTreeviewInterface]
        self._treeview_flows: Optional[AbstractTreeviewInterface]
        self._button_quick_save_config: AbstractButtonQuickSaveConfig | None = None
        self._new_section: dict = {}

    def notify_videos(self, videos: list[Video]) -> None:
        if self._treeview_videos is None:
            raise MissingInjectedInstanceError(type(self._treeview_videos).__name__)
        self.update_quick_save_button(videos)
        self._treeview_videos.update_items()
        self._update_enabled_buttons()

    def notify_files(self) -> None:
        if self._treeview_files is None:
            raise MissingInjectedInstanceError(type(self._treeview_files).__name__)
        self._treeview_files.update_items()
        self._update_enabled_buttons()

    def _update_enabled_buttons(self) -> None:
        self._update_enabled_general_buttons()
        self._update_enabled_track_buttons()
        self._update_enabled_video_buttons()
        self._update_enabled_section_buttons()
        self._update_enabled_flow_buttons()
        self._update_enabled_video_control_buttons()

    def _update_enabled_general_buttons(self) -> None:
        frames = self._get_frames()
        action_running = self._application.action_state.action_running.get()
        general_buttons_enabled = not action_running
        for frame in frames:
            if frame is None:
                raise MissingInjectedInstanceError(type(frame).__name__)
            frame.set_enabled_general_buttons(general_buttons_enabled)

    def _get_frames(self) -> list:
        return [
            self._frame_tracks,
            self._frame_videos,
            self._frame_project,
            self._frame_sections,
            self._frame_flows,
            self._frame_analysis,
        ]

    def _update_enabled_track_buttons(self) -> None:
        if self._frame_tracks is None:
            raise MissingInjectedInstanceError(MISSING_TRACK_FRAME_MESSAGE)
        action_running = self._application.action_state.action_running.get()
        selected_section_ids = self.get_selected_section_ids()
        single_section_selected = len(selected_section_ids) == 1
        single_track_enabled = (not action_running) and single_section_selected
        self._frame_tracks.set_enabled_change_single_item_buttons(single_track_enabled)

    def _update_enabled_video_buttons(self) -> None:
        if self._frame_videos is None:
            raise MissingInjectedInstanceError(MISSING_VIDEO_FRAME_MESSAGE)
        action_running = self._application.action_state.action_running.get()
        selected_videos: list[Video] = self._application.get_selected_videos()
        any_video_selected = len(selected_videos) > 0
        multiple_videos_enabled = (not action_running) and any_video_selected
        self._frame_videos.set_enabled_change_multiple_items_buttons(
            multiple_videos_enabled
        )

    def _update_enabled_section_buttons(self) -> None:
        if self._frame_sections is None:
            raise MissingInjectedInstanceError(MISSING_SECTION_FRAME_MESSAGE)
        action_running = self._application.action_state.action_running.get()
        videos_exist = len(self._application.get_all_videos()) > 0
        selected_section_ids = self.get_selected_section_ids()
        single_section_selected = len(selected_section_ids) == 1
        any_section_selected = len(selected_section_ids) > 0

        add_section_enabled = (not action_running) and videos_exist
        single_section_enabled = add_section_enabled and single_section_selected
        multiple_sections_enabled = add_section_enabled and any_section_selected

        self._frame_sections.set_enabled_add_buttons(add_section_enabled)
        self._frame_sections.set_enabled_change_single_item_buttons(
            single_section_enabled
        )
        self._frame_sections.set_enabled_change_multiple_items_buttons(
            multiple_sections_enabled
        )

    def _update_enabled_flow_buttons(self) -> None:
        if self._frame_flows is None:
            raise MissingInjectedInstanceError(MISSING_FLOW_FRAME_MESSAGE)
        action_running = self._application.action_state.action_running.get()
        two_sections_exist = len(self._application.get_all_sections()) > 1
        flows_exist = len(self._application.get_all_flows()) > 0
        selected_flow_ids = self.get_selected_flow_ids()
        single_flow_selected = len(selected_flow_ids) == 1
        any_flow_selected = len(selected_flow_ids) > 0

        add_flow_enabled = (not action_running) and two_sections_exist
        single_flow_enabled = add_flow_enabled and single_flow_selected and flows_exist
        multiple_flows_enabled = add_flow_enabled and any_flow_selected and flows_exist

        self._frame_flows.set_enabled_add_buttons(add_flow_enabled)
        self._frame_flows.set_enabled_change_single_item_buttons(single_flow_enabled)
        self._frame_flows.set_enabled_change_multiple_items_buttons(
            multiple_flows_enabled
        )

    def _update_enabled_video_control_buttons(self) -> None:
        if self._frame_video_control is None:
            raise MissingInjectedInstanceError(MISSING_VIDEO_CONTROL_FRAME_MESSAGE)
        action_running = self._application.action_state.action_running.get()
        videos_exist = len(self._application.get_all_videos()) > 0
        general_activated = not action_running and videos_exist
        self._frame_video_control.set_enabled_general_buttons(general_activated)

    def _on_section_changed(self, section: SectionId) -> None:
        self._refresh_sections_in_ui()

    def _on_flow_changed(self, flow_id: FlowId) -> None:
        self.notify_flows([flow_id])

    def _on_background_updated(self, image: Optional[TrackImage]) -> None:
        if self._frame_canvas is None:
            raise MissingInjectedInstanceError(AbstractFrameCanvas.__name__)

        if image:
            self._frame_canvas.update_background(image)
        else:
            self._frame_canvas.clear_image()

    def _update_date_range(self, filter_element: FilterElement) -> None:
        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        date_range = filter_element.date_range
        start_date = (
            date_range.start_date.strftime(DATETIME_FORMAT)
            if date_range.start_date
            else ""
        )

        end_date = (
            date_range.end_date.strftime(DATETIME_FORMAT) if date_range.end_date else ""
        )
        self._frame_filter.update_date_range(
            {"start_date": start_date, "end_date": end_date}
        )

    def update_quick_save_button(self, _: Any) -> None:
        if self._button_quick_save_config is None:
            raise MissingInjectedInstanceError(AbstractButtonQuickSaveConfig.__name__)
        try:
            if self._application.config_has_changed():
                self._button_quick_save_config.set_state_changed_color()
            else:
                self._button_quick_save_config.set_default_color()
        except NoExistingConfigFound:
            self._button_quick_save_config.set_default_color()

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        self.notify_files()

    def _intersect_tracks_with_sections(self) -> None:
        if self._window is None:
            raise MissingInjectedInstanceError(type(self._window).__name__)

        start_msg_popup = MinimalInfoBox(
            message="Create events...",
            initial_position=self._window.get_position(),
        )
        self._application.intersect_tracks_with_sections()
        start_msg_popup.update_message(message="Creating events completed")
        start_msg_popup.close()

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        self._refresh_sections_in_ui()
        self.update_quick_save_button(section_event)

    def _refresh_sections_in_ui(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        self.refresh_items_on_canvas()
        self._treeview_sections.update_items()
        self._update_enabled_buttons()

    def notify_flows(self, flows: list[FlowId]) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        self.refresh_items_on_canvas()
        self._treeview_flows.update_items()
        self.update_quick_save_button(flow_id)

    def _notify_action_running_state(self, running: bool) -> None:
        self._update_enabled_buttons()

    def register_observers(self) -> None:
        self._application._datastore.register_video_observer(self)
        self._application.track_view_state.selected_videos.register(
            self._update_selected_videos
        )
        self._application.section_state.selected_sections.register(
            self._update_selected_sections
        )
        self._application.register_section_changed_observer(self._on_section_changed)
        self._application.register_section_changed_observer(
            self.update_quick_save_button
        )
        self._application.file_state.last_saved_config.register(
            self.update_quick_save_button
        )

    def _start_action(self) -> None:
        self._application.action_state.action_running.set(True)

    def _finish_action(self) -> None:
        self._application.action_state.action_running.set(False)

    def set_window(self, window: AbstractMainWindow) -> None:
        self._window = window

    def _update_selected_videos(self, videos: list[Video]) -> None:
        current_paths = [str(video.get_path()) for video in videos]
        self._selected_videos = current_paths
        if self._treeview_videos is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        self._treeview_videos.update_selected_items(current_paths)
        self._update_enabled_video_buttons()

    def add_video(self) -> None:
        track_files = askopenfilenames(
            title="Load video files",
            filetypes=[("video file", SUPPORTED_VIDEO_FILE_TYPES)],
        )
        if not track_files:
            return
        logger().info(f"Video files to load: {track_files}")
        paths = [Path(file) for file in track_files]
        self._application.add_videos(files=paths)

    def remove_videos(self) -> None:
        self._application.remove_videos()

    def set_treeview_videos(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_videos = treeview

    def set_treeview_files(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_files = treeview

    def set_selected_videos(self, video_paths: list[str]) -> None:
        self._selected_videos = video_paths
        selected_videos: list[Video] = []
        for path in video_paths:
            if video := self._application._datastore.get_video_at(Path(path)):
                selected_videos.append(video)
        self._application.track_view_state.selected_videos.set(selected_videos)

    def get_all_videos(self) -> list[Video]:
        return self._application.get_all_videos()

    def get_all_track_files(self) -> set[Path]:
        return self._application.get_all_track_files()

    def set_frame_project(self, project_frame: AbstractFrameProject) -> None:
        self._frame_project = project_frame
        self._show_current_project()

    def _show_current_project(self) -> None:
        if self._frame_project is None:
            raise MissingInjectedInstanceError(type(self._frame_project).__name__)
        project = self._application._datastore.project
        self._frame_project.update(name=project.name, start_date=project.start_date)

    def save_otconfig(self) -> None:
        title = "Save configuration as"
        file_types = [(f"{OTCONFIG} file", f"*.{OTCONFIG}")]
        defaultextension = f".{OTCONFIG}"
        initialfile = f"config.{OTCONFIG}"
        otconfig_file: Path = ask_for_save_file_path(
            title, file_types, defaultextension, initialfile=initialfile
        )
        if not otconfig_file:
            return
        self._save_otconfig(otconfig_file)

    def _save_otconfig(self, otconfig_file: Path) -> None:
        logger().info(f"Config file to save: {otconfig_file}")
        try:
            self._application.save_otconfig(otconfig_file)
        except NoSectionsToSave as cause:
            message = (
                f"{MESSAGE_CONFIGURATION_NOT_SAVED}"
                f"No sections to save, please add new sections first."
            )
            self.__show_error(cause, message)
            return
        except DifferentDrivesException as cause:
            message = (
                f"{MESSAGE_CONFIGURATION_NOT_SAVED}"
                f"Configuration and video files are located on different drives."
            )
            self.__show_error(cause, message)
            return
        except MissingDate as cause:
            message = (
                f"{MESSAGE_CONFIGURATION_NOT_SAVED}"
                f"Start date is missing or invalid. Please add a valid start date."
            )
            self.__show_error(cause, message)
            return

    def _get_window_position(self) -> tuple[int, int]:
        if self._window is None:
            raise MissingInjectedInstanceError(type(self._window).__name__)
        return self._window.get_position()

    def __show_error(self, cause: Exception, message: str) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(
                type(self._treeview_sections).__name__
            ) from cause
        position = self._treeview_sections.get_position()

        InfoBox(
            message=message,
            initial_position=position,
        )

    def load_otconfig(self) -> None:
        otconfig_file = Path(
            askopenfilename(
                title="Load configuration file",
                filetypes=[
                    (f"{OTFLOW} file", f"*.{OTFLOW}"),
                    (f"{OTCONFIG} file", f"*.{OTCONFIG}"),
                ],
                defaultextension=f".{OTFLOW}",
            )
        )
        if not otconfig_file:
            return
        self._load_otconfig(otconfig_file)

    def _load_otconfig(self, otconfig_file: Path) -> None:
        proceed = InfoBox(
            message=(
                "This will load a stored configuration from file. \n"
                "All configured sections, flows and videos will be removed before "
                "loading."
            ),
            initial_position=self._get_window_position(),
            show_cancel=True,
        )
        if proceed.canceled:
            return
        logger().info(f"{OTCONFIG} file to load: {otconfig_file}")
        self._application.load_otconfig(file=Path(otconfig_file))
        self._show_current_project()

    def set_tracks_frame(self, tracks_frame: AbstractFrameTracks) -> None:
        self._frame_tracks = tracks_frame

    def set_video_frame(self, frame: AbstractFrame) -> None:
        self._frame_videos = frame

    def set_sections_frame(self, frame: AbstractFrame) -> None:
        self._frame_sections = frame
        self._update_enabled_section_buttons()

    def set_flows_frame(self, frame: AbstractFrame) -> None:
        self._frame_flows = frame
        self._update_enabled_flow_buttons()

    def set_canvas(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def set_frame_canvas(self, frame_canvas: AbstractFrameCanvas) -> None:
        self._frame_canvas = frame_canvas

    def set_filter_frame(self, filter_frame: AbstractFrameFilter) -> None:
        self._frame_filter = filter_frame

    def set_treeview_sections(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_sections = treeview

    def set_treeview_flows(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_flows = treeview

    def _update_selected_sections(self, section_ids: list[SectionId]) -> None:
        self._update_selected_section_items()
        self._update_enabled_buttons()
        self.update_section_offset_button_state()

    def _update_selected_section_items(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)

        new_section_ids = self.get_selected_section_ids()

        self._treeview_sections.update_selected_items(new_section_ids)
        self.refresh_items_on_canvas()

    def update_section_offset_button_state(self) -> None:
        if self._frame_tracks is None:
            raise MissingInjectedInstanceError(type(self._frame_tracks).__name__)

        currently_selected_sections = (
            self._application.section_state.selected_sections.get()
        )
        default_color = self._frame_tracks.get_default_offset_button_color()
        single_section_selected = len(currently_selected_sections) == 1

        if not single_section_selected:
            self._frame_tracks.configure_offset_button(default_color, False)
            return

        section_offset = self._application.get_section_offset(
            currently_selected_sections[0], EventType.SECTION_ENTER
        )
        if not section_offset:
            # No offset entry found in section for EventType.SECTION_ENTER
            return

        visualization_offset = self._application.track_view_state.track_offset.get()
        if section_offset == visualization_offset:
            self._frame_tracks.configure_offset_button(default_color, False)
        else:
            self._frame_tracks.configure_offset_button(COLOR_ORANGE, True)

    def _update_selected_flows(self, flow_ids: list[FlowId]) -> None:
        self._update_selected_flow_items()
        self._update_enabled_buttons()

    def _update_selected_flow_items(self) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        new_selected_flow_ids = self.get_selected_flow_ids()

        self._treeview_flows.update_selected_items(new_selected_flow_ids)
        self.refresh_items_on_canvas()

    def set_selected_flow_ids(self, ids: list[str]) -> None:
        if self._application.action_state.action_running.get():
            return

        self._application.set_selected_flows(ids)

        logger().debug(f"New flows selected in treeview: id={ids}")

    def set_selected_section_ids(self, ids: list[str]) -> None:
        if self._application.action_state.action_running.get():
            return

        self._application.set_selected_section(ids)

        logger().debug(f"New line sections selected in treeview: id={ids}")

    def get_selected_flow_ids(self) -> list[str]:
        return [
            flow_id.id for flow_id in self._application.flow_state.selected_flows.get()
        ]

    def get_selected_section_ids(self) -> list[str]:
        return [
            section_id.id
            for section_id in self._application.section_state.selected_sections.get()
        ]

    @action
    def load_tracks(self) -> None:
        track_files = askopenfilenames(
            title="Load track files", filetypes=[("tracks file", "*.ottrk")]
        )
        if not track_files:
            return
        logger().info(f"Tracks files to load: {track_files}")
        track_paths = [Path(file) for file in track_files]
        self._application.add_tracks_of_files(track_files=track_paths)

    def load_configuration(self) -> None:  # sourcery skip: avoid-builtin-shadow
        # INFO: Current behavior: Overwrites existing sections
        configuration_file = Path(
            askopenfilename(
                title="Load sections file",
                filetypes=[
                    (f"{OTFLOW} file", f"*.{OTFLOW}"),
                    (f"{OTCONFIG} file", f"*.{OTCONFIG}"),
                ],
                defaultextension=f".{OTFLOW}",
            )
        )
        if not configuration_file.stem:
            return
        elif configuration_file.suffix == f".{OTFLOW}":
            self._load_otflow(configuration_file)
        elif configuration_file.suffix == f".{OTCONFIG}":
            self._load_otconfig(configuration_file)
        else:
            raise ValueError("Configuration file to load has unknown file extension")

    def _load_otflow(self, otflow_file: Path) -> None:
        sections = self._application.get_all_sections()
        flows = self._application.get_all_flows()
        if sections or flows:
            proceed = InfoBox(
                message=(
                    "This will load a stored otflow configuration from file. \n"
                    "All configured sections and flows will be removed before "
                    "loading."
                ),
                initial_position=self._get_window_position(),
                show_cancel=True,
            )
            if proceed.canceled:
                return
        logger().info(f"otflow file to load: {otflow_file}")
        self._application.load_otflow(sections_file=Path(otflow_file))
        self.set_selected_section_ids([])
        self.set_selected_flow_ids([])
        self.refresh_items_on_canvas()

    def save_configuration(self) -> None:
        initial_dir = Path.cwd()
        if config_file := self._application.file_state.last_saved_config.get():
            initial_dir = config_file.file.parent

        configuration_file = ask_for_save_file_path(
            title="Save configuration as",
            filetypes=[
                (f"{OTFLOW} file", f"*.{OTFLOW}"),
                (f"{OTCONFIG} file", f"*.{OTCONFIG}"),
            ],
            defaultextension=f".{OTFLOW}",
            initialfile=f"flows.{OTFLOW}",
            initialdir=initial_dir,
        )
        if not configuration_file.stem:
            return
        elif configuration_file.suffix == f".{OTFLOW}":
            self._save_otflow(configuration_file)
        elif configuration_file.suffix == f".{OTCONFIG}":
            self._save_otconfig(configuration_file)
        else:
            raise ValueError("Configuration file to save has unknown file extension")

    def quick_save_configuration(self) -> None:
        try:
            self._application.quick_save_configuration()
        except NoExistingFileToSave:
            self.save_configuration()

    def _save_otflow(self, otflow_file: Path) -> None:
        logger().info(f"Sections file to save: {otflow_file}")
        try:
            self._application.save_otflow(Path(otflow_file))
        except NoSectionsToSave as cause:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(
                    type(self._treeview_sections).__name__
                ) from cause
            position = self._treeview_sections.get_position()
            InfoBox(
                message="No sections to save, please add new sections first",
                initial_position=position,
            )
            return

    def cancel_action(self) -> None:
        self._finish_action()

    def add_line_section(self) -> None:
        self.set_selected_section_ids([])
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        self._start_action()
        SectionBuilder(viewmodel=self, canvas=self._canvas, style=EDITED_SECTION_STYLE)

    def add_area_section(self) -> None:
        self.set_selected_section_ids([])
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        self._start_action()
        SectionBuilder(
            viewmodel=self,
            canvas=self._canvas,
            is_area_section=True,
            style=EDITED_SECTION_STYLE,
        )

    def get_section_metadata(
        self,
        title: str,
        initial_position: tuple[int, int],
        input_values: dict | None = None,
    ) -> dict:
        if not (
            section_offset := self._application.track_view_state.track_offset.get()
        ):
            section_offset = RELATIVE_SECTION_OFFSET
        return ToplevelSections(
            title=title,
            viewmodel=self,
            section_offset=section_offset,
            initial_position=initial_position,
            input_values=input_values,
            show_offset=self._show_offset(),
        ).get_metadata()

    def _show_offset(self) -> bool:
        return True

    def is_section_name_valid(self, section_name: str) -> bool:
        return self._application.is_section_name_valid(section_name)

    def add_new_section(
        self,
        coordinates: list[tuple[int, int]],
        is_area_section: bool,
        get_metadata: MetadataProvider,
    ) -> None:
        if not coordinates:
            raise MissingCoordinate("First coordinate is missing")
        elif len(coordinates) == 1:
            raise MissingCoordinate("Second coordinate is missing")
        with contextlib.suppress(CancelAddSection):
            section = self.__create_section(coordinates, is_area_section, get_metadata)
            if not section.name.startswith(CUTTING_SECTION_MARKER):
                logger().info(f"New section created: {section.id}")
                self._update_selected_sections([section.id])
        self._finish_action()

    def __create_section(
        self,
        coordinates: list[tuple[int, int]],
        is_area_section: bool,
        get_metadata: MetadataProvider,
    ) -> Section:
        metadata = self.__get_metadata(get_metadata)
        relative_offset_coordinates_enter = metadata[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ]
        section: Section | None = None
        if is_area_section:
            section = Area(
                id=self._application.get_section_id(),
                name=metadata[NAME],
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: geometry.RelativeOffsetCoordinate(
                        **relative_offset_coordinates_enter
                    )
                },
                plugin_data={},
                coordinates=[
                    self._to_coordinate(coordinate) for coordinate in coordinates
                ],
            )
        else:
            section = LineSection(
                id=self._application.get_section_id(),
                name=metadata[NAME],
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: geometry.RelativeOffsetCoordinate(
                        **relative_offset_coordinates_enter
                    )
                },
                plugin_data={},
                coordinates=[
                    self._to_coordinate(coordinate) for coordinate in coordinates
                ],
            )
        if section is None:
            raise TypeError("section has to be LineSection or Area, but is None")
        self._application.add_section(section)
        return section

    def __get_metadata(self, get_metadata: MetadataProvider) -> dict:
        metadata = get_metadata()
        while (
            (not metadata)
            or (NAME not in metadata)
            or (not self.is_section_name_valid(metadata[NAME]))
            or (RELATIVE_OFFSET_COORDINATES not in metadata)
        ):
            metadata = get_metadata()
        return metadata

    def __validate_section_information(
        self, meta_data: dict, coordinates: list[tuple[int, int]]
    ) -> None:
        if not coordinates:
            raise MissingCoordinate("First coordinate is missing")
        elif len(coordinates) == 1:
            raise MissingCoordinate("Second coordinate is missing")
        if not meta_data:
            raise ValueError("Metadata of line_section are not defined")

    def update_section_coordinates(
        self, meta_data: dict, coordinates: list[tuple[int, int]]
    ) -> None:
        self.__validate_section_information(meta_data, coordinates)
        section_id = SectionId(meta_data[ID])
        if not (section := self._application.get_section_for(section_id)):
            raise MissingSection(
                f"Could not update section '{section_id.serialize()}' after editing"
            )
        section.update_coordinates(
            [self._to_coordinate(coordinate) for coordinate in coordinates]
        )
        self._application.update_section(section)
        logger().info(f"Update section: {section.id}")
        self._update_selected_sections([section.id])
        self._finish_action()

    def _to_coordinate(self, coordinate: tuple[int, int]) -> geometry.Coordinate:
        return geometry.Coordinate(coordinate[0], coordinate[1])

    def _is_area_section(self, section: Section | None) -> bool:
        return isinstance(section, Area)

    def _is_line_section(self, section: Section | None) -> bool:
        return isinstance(section, LineSection)

    def edit_section_geometry(self) -> None:
        if len(selected_section_ids := self.get_selected_section_ids()) != 1:
            raise MultipleSectionsSelected(
                "Multiple sections are selected. Unable to edit section geometry!"
            )

        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        self._start_action()
        CanvasElementDeleter(canvas=self._canvas).delete(tag_or_id=TAG_SELECTED_SECTION)
        if selected_section_ids:
            if current_section := self._application.get_section_for(
                SectionId(selected_section_ids[0])
            ):
                SectionGeometryEditor(
                    viewmodel=self,
                    canvas=self._canvas,
                    section=current_section,
                    edited_section_style=EDITED_SECTION_STYLE,
                    pre_edit_section_style=PRE_EDIT_SECTION_STYLE,
                    selected_knob_style=SELECTED_KNOB_STYLE,
                    is_area_section=self._is_area_section(current_section),
                )

    def edit_selected_section_metadata(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)

        if not (selected_section_ids := self.get_selected_section_ids()):
            position = self._treeview_sections.get_position()
            InfoBox(
                message="Please select a section to edit", initial_position=position
            )
            return

        if len(selected_section_ids) != 1:
            raise MultipleSectionsSelected(
                "Multiple sections are selected. Unable to edit section metadata!"
            )

        section_id = SectionId(selected_section_ids[0])
        if selected_section := self._application.get_section_for(section_id):
            self._update_metadata(selected_section)
            self.update_section_offset_button_state()

    @action
    def _update_metadata(self, selected_section: Section) -> None:
        current_data = selected_section.to_dict()
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        position = self._canvas.get_position()
        with contextlib.suppress(CancelAddSection):
            self.__update_section_metadata(selected_section, current_data, position)

    def __update_section_metadata(
        self, selected_section: Section, current_data: dict, position: tuple[int, int]
    ) -> None:
        updated_section_data = self.get_section_metadata(
            title="Edit section",
            initial_position=position,
            input_values=current_data,
        )
        self._set_section_data(
            id=selected_section.id,
            data=updated_section_data,
        )
        self.refresh_items_on_canvas()
        logger().info(f"Updated line_section Metadata: {updated_section_data}")

    def _set_section_data(self, id: SectionId, data: dict) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(AbstractTreeviewInterface.__name__)
        section = self._flow_parser.parse_section(data)
        self._application.update_section(section)
        if not section.name.startswith(CUTTING_SECTION_MARKER):
            self._treeview_sections.update_selected_items([id.serialize()])

    @action
    def remove_sections(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)

        if not (selected_section_ids := self.get_selected_section_ids()):
            position = self._treeview_sections.get_position()
            InfoBox(
                message="Please select one or more sections to remove",
                initial_position=position,
            )
            return

        section_ids = [SectionId(id) for id in selected_section_ids]
        for section_id in section_ids:
            if self._application.is_flow_using_section(section_id):
                message = (
                    "The section you want to remove is being used in flows.\n"
                    "Please remove the following flows before removing the section.\n"
                )
                for flow in self._application.flows_using_section(section_id):
                    message += flow.name + "\n"
                position = self._treeview_sections.get_position()
                InfoBox(
                    message=message,
                    initial_position=position,
                )
                return

        for section_id in section_ids:
            self._application.remove_section(section_id)
        self.refresh_items_on_canvas()

    def refresh_items_on_canvas(self) -> None:
        self._remove_items_from_canvas()
        self._draw_items_on_canvas()

    def _remove_items_from_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        CanvasElementDeleter(canvas=self._canvas).delete(tag_or_id=LINE_SECTION)

    def _draw_items_on_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        sections_to_highlight = self._get_sections_to_highlight()
        self._draw_sections(sections_to_highlight)
        if self._application.flow_state.selected_flows.get():
            self._draw_arrow_for_selected_flows()

    def _get_sections_to_highlight(self) -> list[str]:
        if selected_section_ids := self.get_selected_section_ids():
            return selected_section_ids
        return []

    def _draw_sections(self, sections_to_highlight: list[str]) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        section_painter = SectionPainter(canvas=self._canvas)
        for section in self._get_sections():
            tags = [LINE_SECTION]
            if section[ID] in sections_to_highlight:
                style = SELECTED_SECTION_STYLE
                tags.append(TAG_SELECTED_SECTION)
            else:
                style = DEFAULT_SECTION_STYLE
            section_painter.draw(
                tags=tags,
                id=section[ID],
                coordinates=section[COORDINATES],
                section_style=style,
                is_area_section=self._is_area_section(
                    self._application.get_section_for(SectionId(section[ID]))
                ),
            )

    def _draw_arrow_for_selected_flows(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        for flow in self._get_selected_flows():
            if start_section := self._application.get_section_for(flow.start):
                if end_section := self._application.get_section_for(flow.end):
                    start_refpt_calculator = self._get_section_refpt_calculator(
                        start_section
                    )
                    end_refpt_calculator = self._get_section_refpt_calculator(
                        end_section
                    )
                    ArrowPainter(self._canvas).draw(
                        start_section=start_section,
                        end_section=end_section,
                        start_refpt_calculator=start_refpt_calculator,
                        end_refpt_calculator=end_refpt_calculator,
                        tags=[LINE_SECTION],
                        arrow_style=ARROW_STYLE,
                    )

    def _get_section_refpt_calculator(
        self, section: Section
    ) -> SectionRefPointCalculator:
        if self._is_line_section(section):
            return InnerSegmentsCenterCalculator()
        elif self._is_area_section(section):
            return GeometricCenterCalculator()
        else:
            raise ValueError("section has to be a LineSection or an Area, but isnt")

    def _get_selected_flows(self) -> list[Flow]:
        flows: list[Flow] = []
        for flow_id in self._application.flow_state.selected_flows.get():
            flow = self._application.get_flow_for(flow_id)
            if flow:
                flows.append(flow)
        return flows

    def _get_sections(self) -> Iterable[dict]:
        return map(
            lambda section: self._transform_coordinates(section),
            map(
                lambda section: section.to_dict(),
                self._application.get_all_sections(),
            ),
        )

    def _transform_coordinates(self, section: dict) -> dict:
        section[COORDINATES] = [
            self._to_coordinate_tuple(coordinate) for coordinate in section[COORDINATES]
        ]
        return section

    def _to_coordinate_tuple(self, coordinate: dict) -> tuple[int, int]:
        return (coordinate[geometry.X], coordinate[geometry.Y])

    def get_all_sections(self) -> Iterable[Section]:
        return self._application.get_all_sections()

    def get_all_flows(self) -> Iterable[Flow]:
        return self._application.get_all_flows()

    @action
    def add_flow(self) -> None:
        with contextlib.suppress(CancelAddFlow):
            flow = self.__create_flow()
            logger().info(f"Added new flow: {flow.id}")
            self.set_selected_flow_ids([flow.id.serialize()])

    def __create_flow(self) -> Flow:
        flow_data = self._show_flow_popup()
        flow_id = self._application.get_flow_id()
        name = flow_data[FLOW_NAME]
        new_from_section_id = SectionId(flow_data[START_SECTION])
        new_to_section_id = SectionId(flow_data[END_SECTION])
        distance = flow_data.get(DISTANCE, None)
        flow = Flow(
            id=flow_id,
            name=name,
            start=new_from_section_id,
            end=new_to_section_id,
            distance=distance,
        )
        self.__try_add_flow(flow)
        return flow

    def _show_flow_popup(
        self,
        input_values: dict | None = None,
        title: str = "Add flow",
    ) -> dict:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        position = self._treeview_flows.get_position()
        section_ids = [
            self.__to_resource(section) for section in self.get_all_sections()
        ]
        if len(section_ids) < 2:
            InfoBox(
                message="To add a flow, at least two sections are needed",
                initial_position=position,
            )
            raise CancelAddFlow()
        return self.__create_flow_data(input_values, title, position, section_ids)

    def __create_flow_data(
        self,
        input_values: dict | None,
        title: str,
        position: tuple[int, int],
        section_ids: list[ColumnResource],
    ) -> dict:
        flow_data = self.__get_flow_data(input_values, title, position, section_ids)
        while (not flow_data) or not (self.__is_flow_name_valid(flow_data)):
            new_entry_name = flow_data[FLOW_NAME]
            if (input_values is not None) and (
                new_entry_name == input_values[FLOW_NAME]
            ):
                break
            InfoBox(
                message="To add a flow, a unique name is necessary",
                initial_position=position,
            )
            flow_data[FLOW_NAME] = ""
            flow_data = self.__get_flow_data(flow_data, title, position, section_ids)
        return flow_data

    def __is_flow_name_valid(self, flow_data: dict) -> bool:
        return flow_data[FLOW_NAME] and self._application.is_flow_name_valid(
            flow_data[FLOW_NAME]
        )

    def __get_flow_data(
        self,
        input_values: dict | None,
        title: str,
        position: tuple[int, int],
        section_ids: list[ColumnResource],
    ) -> dict:
        return ToplevelFlows(
            title=title,
            initial_position=position,
            section_ids=section_ids,
            name_generator=self._name_generator,
            input_values=input_values,
            show_distance=self._show_distance(),
        ).get_data()

    def __try_add_flow(self, flow: Flow) -> None:
        try:
            self._application.add_flow(flow)
        except FlowAlreadyExists as cause:
            if self._treeview_flows is None:
                raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
            position = self._treeview_flows.get_position()
            InfoBox(message=str(cause), initial_position=position)
            raise CancelAddFlow()

    def _show_distance(self) -> bool:
        return True

    def generate_flows(self) -> None:
        self._application.generate_flows()

    def __to_resource(self, section: Section) -> ColumnResource:
        values = {COLUMN_SECTION: section.name}
        return ColumnResource(id=section.id.serialize(), values=values)

    def __update_flow_data(self, flow_data: dict) -> None:
        flow_id = FlowId(flow_data.get(FLOW_ID, ""))
        name = flow_data[FLOW_NAME]
        new_from_section_id = SectionId(flow_data[START_SECTION])
        new_to_section_id = SectionId(flow_data[END_SECTION])
        distance = flow_data.get(DISTANCE, None)
        if flow := self._application.get_flow_for(flow_id):
            flow.name = name
            flow.start = new_from_section_id
            flow.end = new_to_section_id
            flow.distance = distance
            self._application.update_flow(flow)
        self.set_selected_flow_ids([flow_id.serialize()])
        self.refresh_items_on_canvas()

    @action
    def edit_selected_flow(self) -> None:
        with contextlib.suppress(CancelAddFlow):
            if flows := self._get_selected_flows():
                if len(flows) != 1:
                    raise MultipleFlowsSelected(
                        "Multiple flows selected. Unable to edit flow!"
                        "Please select only one flow."
                    )
                self._edit_flow(flows[0])
            else:
                if self._treeview_flows is None:
                    raise MissingInjectedInstanceError(
                        type(self._treeview_flows).__name__
                    )
                position = self._treeview_flows.get_position()
                InfoBox(
                    message="Please select a flow to edit", initial_position=position
                )

    def _edit_flow(self, flow: Flow) -> None:
        input_data = {
            FLOW_ID: flow.id.serialize(),
            FLOW_NAME: flow.name,
            START_SECTION: flow.start.id,
            END_SECTION: flow.end.id,
            DISTANCE: flow.distance,
        }

        if flow_data := self._show_flow_popup(
            input_values=input_data,
            title="Edit flow",
        ):
            self.__update_flow_data(flow_data=flow_data)

    @action
    def remove_flows(self) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        if flow_ids := self._application.flow_state.selected_flows.get():
            for flow_id in flow_ids:
                self._application.remove_flow(flow_id)
                self.refresh_items_on_canvas()
        else:
            position = self._treeview_flows.get_position()
            InfoBox(message="Please select a flow to remove", initial_position=position)

    def create_events(self) -> None:
        if self._window is None:
            raise MissingInjectedInstanceError(type(self._window).__name__)

        start_msg_popup = MinimalInfoBox(
            message="Create events...",
            initial_position=self._window.get_position(),
        )
        self._application.create_events()
        start_msg_popup.update_message(message="Creating events completed")
        sleep(1)
        start_msg_popup.close()

    def save_events(self, file: str) -> None:
        self._application.save_events(Path(file))
        logger().info(f"Eventlist file saved to '{file}'")

    def export_events(self) -> None:
        default_values: dict[str, str] = {
            EXPORT_FORMAT: self.__get_default_export_format()
        }
        export_format_extensions: dict[str, str] = {
            key: exporter.get_extension()
            for key, exporter in self._event_list_export_formats.items()
        }
        try:
            event_list_exporter, file = self._configure_event_exporter(
                default_values, export_format_extensions
            )
            self._application.export_events(Path(file), event_list_exporter)
            logger().info(
                f"Exporting eventlist using {event_list_exporter.get_name()} to {file}"
            )
        except CancelExportEvents:
            logger().info("User canceled configuration of export")

    def __get_default_export_format(self) -> str:
        if self._event_list_export_formats:
            return next(iter(self._event_list_export_formats.keys()))
        return ""

    def _configure_event_exporter(
        self, default_values: dict[str, str], export_format_extensions: dict[str, str]
    ) -> tuple[EventListExporter, Path]:
        input_values = ToplevelExportEvents(
            title="Export events",
            initial_position=(50, 50),
            input_values=default_values,
            export_format_extensions=export_format_extensions,
        ).get_data()
        file = input_values[toplevel_export_events.EXPORT_FILE]
        export_format = input_values[toplevel_export_events.EXPORT_FORMAT]
        event_list_exporter = self._event_list_export_formats.get(export_format, None)
        if event_list_exporter is None:
            raise ExporterNotFoundError(
                f"{event_list_exporter} is not a valid export format"
            )
        return event_list_exporter, file

    def set_track_offset(self, offset_x: float, offset_y: float) -> None:
        if self._window is None:
            raise MissingInjectedInstanceError(type(self._window).__name__)

        start_msg_popup = MinimalInfoBox(
            message="Apply offset...",
            initial_position=self._window.get_position(),
        )
        offset = geometry.RelativeOffsetCoordinate(offset_x, offset_y)
        self._application.track_view_state.track_offset.set(offset)
        start_msg_popup.update_message(message="Apply offset completed")
        start_msg_popup.close()
        self.update_section_offset_button_state()

    def get_track_offset(self) -> Optional[tuple[float, float]]:
        if current_offset := self._application.get_current_track_offset():
            return (current_offset.x, current_offset.y)
        return None

    def _update_offset(
        self, offset: Optional[geometry.RelativeOffsetCoordinate]
    ) -> None:
        if self._frame_tracks is None:
            raise MissingInjectedInstanceError(AbstractFrameTracks.__name__)

        if offset:
            self._frame_tracks.update_offset(offset.x, offset.y)

    def change_track_offset_to_section_offset(self) -> None:
        self._application.change_track_offset_to_section_offset()
        if self._frame_tracks is None:
            raise MissingInjectedInstanceError(type(self._frame_tracks).__name__)
        self.update_section_offset_button_state()

    def next_frame(self) -> None:
        self._application.next_frame()

    def previous_frame(self) -> None:
        self._application.previous_frame()

    def next_second(self) -> None:
        self._application.next_second()

    def previous_second(self) -> None:
        self._application.previous_second()

    def next_event(self) -> None:
        self._application.next_event()

    def previous_event(self) -> None:
        self._application.previous_event()

    def validate_date(self, date: str) -> bool:
        return any(
            [validate_date(date, date_format) for date_format in SUPPORTED_FORMATS]
        )

    def validate_hour(self, hour: str) -> bool:
        try:
            return validate_hour(int(hour))
        except ValueError:
            return False

    def validate_minute(self, minute: str) -> bool:
        try:
            return validate_minute(int(minute))
        except ValueError:
            return False

    def validate_second(self, second: str) -> bool:
        try:
            return validate_second(int(second))
        except ValueError:
            return False

    def apply_filter_tracks_by_date(self, date_range: DateRange) -> None:
        self._application.update_date_range_tracks_filter(date_range)
        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.set_active_color_on_filter_by_date_button()

    def apply_filter_tracks_by_class(self, classes: list[str]) -> None:
        self._application.update_class_tracks_filter(set(classes))
        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.set_active_color_on_filter_by_class_button()

    def reset_filter_tracks_by_date(self) -> None:
        self._application.update_date_range_tracks_filter(DateRange(None, None))

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.set_inactive_color_on_filter_by_date_button()

    def reset_filter_tracks_by_class(self) -> None:
        self._application.update_class_tracks_filter(None)

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.set_inactive_color_on_filter_by_class_button()

    def get_first_detection_occurrence(self) -> Optional[datetime]:
        return self._application._tracks_metadata.first_detection_occurrence

    def get_last_detection_occurrence(self) -> Optional[datetime]:
        return self._application._tracks_metadata.last_detection_occurrence

    def get_classes(self) -> list[str]:
        return sorted(
            list(self._application._tracks_metadata.classifications), key=str.lower
        )

    def get_class_filter_selection(self) -> Optional[list[str]]:
        current_selection = (
            self._application.track_view_state.filter_element.get().classifications
        )
        if current_selection is not None:
            return list(current_selection)
        return current_selection

    def get_filter_tracks_by_date_setting(self) -> DateRange:
        filter_element = self._application.track_view_state.filter_element.get()
        return filter_element.date_range

    def change_filter_date_active(self, current: bool) -> None:
        if current:
            self.__enable_filter_track_by_date_button()
        else:
            self.__disable_filter_track_by_date_button()

    def enable_filter_track_by_date(self) -> None:
        self._application.enable_filter_track_by_date()

        self.__enable_filter_track_by_date_button()

    def __enable_filter_track_by_date_button(self) -> None:
        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)
        current_date_range = (
            self._application.track_view_state.filter_element.get().date_range
        )
        self._application.track_view_state.filter_date_active.set(True)
        self._frame_filter.enable_filter_by_date_button()
        if current_date_range != DateRange(None, None):
            self._frame_filter.set_active_color_on_filter_by_date_button()
        else:
            self._frame_filter.set_inactive_color_on_filter_by_date_button()

    def disable_filter_track_by_date(self) -> None:
        self._application.disable_filter_track_by_date()

        self.__disable_filter_track_by_date_button()

    def __disable_filter_track_by_date_button(self) -> None:
        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)
        self._application.track_view_state.filter_date_active.set(False)
        self._frame_filter.disable_filter_by_date_button()

    def switch_to_prev_date_range(self) -> None:
        self._application.switch_to_prev_date_range()

    def switch_to_next_date_range(self) -> None:
        self._application.switch_to_next_date_range()

    def enable_filter_track_by_class(self) -> None:
        self._application.enable_filter_track_by_class()

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.enable_filter_by_class_button()
        current_classes = (
            self._application.track_view_state.filter_element.get().classifications
        )
        if current_classes is not None:
            self._frame_filter.set_active_color_on_filter_by_class_button()
        else:
            self._frame_filter.set_inactive_color_on_filter_by_class_button()

    def disable_filter_track_by_class(self) -> None:
        self._application.disable_filter_track_by_class()

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.disable_filter_by_class_button()

    def export_counts(self) -> None:
        if len(self._application.get_all_flows()) == 0:
            InfoBox(
                message=(
                    "Counting needs at least one flow.\n"
                    "There is no flow configurated.\n"
                    "Please create a flow."
                ),
                initial_position=(
                    self._window.get_position() if self._window else (0, 0)
                ),
            )
            return
        export_formats: dict = {
            format.name: format.file_extension
            for format in self._application.get_supported_export_formats()
        }
        default_format = next(iter(export_formats.keys()))
        start = self._application._videos_metadata.first_video_start
        end = self._application._videos_metadata.last_video_end
        modes = list(
            self._application._tracks_metadata.filtered_detection_classifications
        )
        default_values: dict = {
            INTERVAL: DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
            START: start,
            END: end,
            EXPORT_FORMAT: default_format,
        }
        try:
            export_values: dict = ToplevelExportCounts(
                title="Export counts",
                initial_position=(50, 50),
                input_values=default_values,
                export_formats=export_formats,
                viewmodel=self,
            ).get_data()
            logger().debug(export_values)
            export_specification = CountingSpecificationDto(
                interval_in_minutes=export_values[INTERVAL],
                start=export_values[START],
                end=export_values[END],
                modes=modes,
                output_format=export_values[EXPORT_FORMAT],
                output_file=export_values[EXPORT_FILE],
            )
            self._application.export_counts(export_specification)
        except CancelExportCounts:
            logger().info("User canceled configuration of export")

    def start_new_project(self) -> None:
        proceed = InfoBox(
            message=(
                "This will start a new project. \n"
                "All configured project settings, sections, flows, tracks, and videos "
                "will be reset to the default application settings."
            ),
            initial_position=self._get_window_position(),
            show_cancel=True,
        )
        if proceed.canceled:
            return
        self._application.start_new_project()
        self._show_current_project()
        logger().info("Start new project.")

    def update_project_name(self, name: str) -> None:
        self._application.update_project_name(name)

    def update_project_start_date(self, start_date: Optional[datetime]) -> None:
        self._application.update_project_start_date(start_date)

    def on_start_new_project(self, _: None) -> None:
        self._reset_filters()
        self._reset_plotting_layer()
        self._display_preview_image()

    def _reset_filters(self) -> None:
        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)
        self._frame_filter.reset()

    def _display_preview_image(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        self._canvas.add_preview_image()

    def _reset_plotting_layer(self) -> None:
        if self._frame_track_plotting is None:
            raise MissingInjectedInstanceError(AbstractFrameTrackPlotting.__name__)
        self._frame_track_plotting.reset_layers()

    def set_frame_track_plotting(
        self, frame_track_plotting: AbstractFrameTrackPlotting
    ) -> None:
        self._frame_track_plotting = frame_track_plotting

    def on_tracks_cut(self, cut_tracks_dto: CutTracksDto) -> None:
        window_position = self._get_window_position()
        msg = (
            "Cut successful. "
            f"Cutting section '{cut_tracks_dto.section} '"
            " and original tracks deleted.\n"
            f"{len(cut_tracks_dto.original_tracks)} out of "
            f"{self._application.get_track_repository_size()} tracks successfully cut. "
        )

        logger().info(msg)
        InfoBox(msg, window_position)

    def set_analysis_frame(self, frame: AbstractFrame) -> None:
        self._frame_analysis = frame

    def update_skip_time(self, seconds: int, frames: int) -> None:
        self._application.track_view_state.skip_time.set(SkipTime(seconds, frames))

    def get_skip_seconds(self) -> int:
        return self._application.track_view_state.skip_time.get().seconds

    def get_skip_frames(self) -> int:
        return self._application.track_view_state.skip_time.get().frames

    def set_video_control_frame(self, frame: AbstractFrame) -> None:
        self._frame_video_control = frame

    def set_button_quick_save_config(
        self, button_quick_save_config: AbstractButtonQuickSaveConfig
    ) -> None:
        self._button_quick_save_config = button_quick_save_config

    def export_road_user_assignments(self) -> None:
        if len(self._application.get_all_flows()) == 0:
            InfoBox(
                message=(
                    "Counting needs at least one flow.\n"
                    "There is no flow configured.\n"
                    "Please create a flow."
                ),
                initial_position=(
                    self._window.get_position() if self._window else (0, 0)
                ),
            )
            return
        export_formats: dict = {
            export_format.name: export_format.file_extension
            for export_format in self._application.get_road_user_export_formats()
        }
        default_format = next(iter(export_formats.keys()))
        default_values: dict = {
            EXPORT_FORMAT: default_format,
        }

        try:
            export_values = ToplevelExportEvents(
                title="Export road user assignments",
                initial_position=(50, 50),
                input_values=default_values,
                export_format_extensions=export_formats,
                initial_file_stem="road_user_assignments",
            ).get_data()
            logger().debug(export_values)
            save_path = export_values[toplevel_export_events.EXPORT_FILE]
            export_format = export_values[toplevel_export_events.EXPORT_FORMAT]

            export_specification = ExportSpecification(save_path, export_format)
            self._application.export_road_user_assignments(export_specification)
            logger().info(f"Exporting road user assignments to {save_path}")
        except CancelExportEvents:
            logger().info("User canceled configuration of export")
