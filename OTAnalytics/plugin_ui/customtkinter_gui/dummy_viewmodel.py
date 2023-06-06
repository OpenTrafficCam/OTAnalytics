from datetime import datetime
from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from typing import Iterable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.default_values import DATE_FORMAT
from OTAnalytics.adapter_ui.view_model import MissingCoordinate, ViewModel
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import FlowParser, NoSectionsToSave
from OTAnalytics.domain import geometry
from OTAnalytics.domain.date import (
    DateRange,
    validate_date,
    validate_hour,
    validate_minute,
    validate_second,
)
from OTAnalytics.domain.flow import Flow, FlowId, FlowListObserver
from OTAnalytics.domain.section import (
    COORDINATES,
    ID,
    NAME,
    RELATIVE_OFFSET_COORDINATES,
    LineSection,
    MissingSection,
    Section,
    SectionId,
    SectionListObserver,
)
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.line_section import (
    ArrowPainter,
    CanvasElementDeleter,
    SectionBuilder,
    SectionGeometryEditor,
    SectionPainter,
)
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.style import (
    ARROW_STYLE,
    DEFAULT_SECTION_STYLE,
    EDITED_SECTION_STYLE,
    PRE_EDIT_SECTION_STYLE,
    SELECTED_KNOB_STYLE,
    SELECTED_SECTION_STYLE,
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
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import IdResource

LINE_SECTION: str = "line_section"
TO_SECTION = "to_section"
FROM_SECTION = "from_section"
OTFLOW = "otflow"


class MissingInjectedInstanceError(Exception):
    """Raise when no instance of an object was injected before referencing it"""

    def __init__(self, injected_object: str):
        message = (
            f"An instance of {injected_object} has to be injected before referencing it"
        )
        super().__init__(message)


def flow_id(from_section: str, to_section: str) -> str:
    return f"{from_section} -> {to_section}"


class DummyViewModel(ViewModel, SectionListObserver, FlowListObserver):
    def __init__(
        self,
        application: OTAnalyticsApplication,
        flow_parser: FlowParser,
    ) -> None:
        self._application = application
        self._flow_parser: FlowParser = flow_parser
        self._frame_tracks: Optional[AbstractFrameTracks] = None
        self._frame_canvas: Optional[AbstractFrameCanvas] = None
        self._frame_filter: Optional[AbstractFrameFilter] = None
        self._canvas: Optional[AbstractCanvas] = None
        self._treeview_sections: Optional[AbstractTreeviewInterface]
        self._treeview_flows: Optional[AbstractTreeviewInterface]
        self._new_section: dict = {}
        self._selected_section_id: Optional[str] = None
        self._selected_flow_id: Optional[str] = None
        self.register_to_subjects()

    def register_to_subjects(self) -> None:
        self._application.register_sections_observer(self)
        self._application.register_section_changed_observer(self._on_section_changed)
        self._application.register_flows_observer(self)
        self._application.register_flow_changed_observer(self._on_flow_changed)
        self._application.track_view_state.show_tracks.register(
            self._on_show_tracks_state_updated
        )
        self._application.section_state.selected_section.register(
            self._update_selected_section
        )
        self._application.flow_state.selected_flow.register(self._update_selected_flow)
        self._application.track_view_state.background_image.register(
            self._on_background_updated
        )
        self._application.track_view_state.track_offset.register(self._update_offset)

    def _on_section_changed(self, section_id: SectionId) -> None:
        self.notify_sections([section_id])

    def _on_flow_changed(self, flow_id: FlowId) -> None:
        self.notify_flows([flow_id])

    def _on_show_tracks_state_updated(self, value: Optional[bool]) -> None:
        if self._frame_canvas is None:
            raise MissingInjectedInstanceError(AbstractFrameCanvas.__name__)

        new_value = value or False
        self._frame_canvas.update_show_tracks(new_value)

    def _on_background_updated(self, image: Optional[TrackImage]) -> None:
        if self._frame_canvas is None:
            raise MissingInjectedInstanceError(AbstractFrameCanvas.__name__)

        if image:
            self._frame_canvas.update_background(image)

    def update_show_tracks_state(self, value: bool) -> None:
        self._application.track_view_state.show_tracks.set(value)

    def notify_sections(self, sections: list[SectionId]) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        self.refresh_items_on_canvas()
        self._treeview_sections.update_items()

    def notify_flows(self, flows: list[FlowId]) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        self.refresh_items_on_canvas()
        self._treeview_flows.update_items()

    def set_tracks_frame(self, tracks_frame: AbstractFrameTracks) -> None:
        self._frame_tracks = tracks_frame

    def set_canvas(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def set_tracks_canvas(self, tracks_canvas: AbstractFrameCanvas) -> None:
        self._frame_canvas = tracks_canvas

    def set_filter_frame(self, filter_frame: AbstractFrameFilter) -> None:
        self._frame_filter = filter_frame

    def set_treeview_sections(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_sections = treeview

    def set_treeview_flows(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_flows = treeview

    def _update_selected_section(self, section_id: Optional[SectionId]) -> None:
        current_id = section_id.serialize() if section_id else None
        self._selected_section_id = current_id

        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        self.refresh_items_on_canvas()
        self._treeview_sections.update_selected_items(self._selected_section_id)

    def _update_selected_flow(self, flow_id: Optional[FlowId]) -> None:
        current_id = flow_id.id if flow_id else None
        self._selected_flow_id = current_id

        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        self.refresh_items_on_canvas()
        self._treeview_flows.update_selected_items(self._selected_flow_id)

    def set_selected_flow_id(self, id: Optional[str]) -> None:
        self._selected_flow_id = id
        self._application.set_selected_flow(id)
        if id is not None:
            self._application.set_selected_section(None)

        print(f"New flow selected in treeview: id={id}")

    def set_selected_section_id(self, id: Optional[str]) -> None:
        self._selected_section_id = id
        self._application.set_selected_section(id)
        if id is not None:
            self._application.set_selected_flow(None)

        print(f"New line section selected in treeview: id={id}")

    def load_tracks(self) -> None:
        track_files = askopenfilenames(
            title="Load track files", filetypes=[("tracks file", "*.ottrk")]
        )
        if not track_files:
            return
        print(f"Tracks files to load: {track_files}")
        track_paths = [Path(file) for file in track_files]
        self._application.add_tracks_of_files(track_files=track_paths)

    def load_sections(self) -> None:  # sourcery skip: avoid-builtin-shadow
        # INFO: Current behavior: Overwrites existing sections
        sections_file = askopenfilename(
            title="Load sections file",
            filetypes=[(f"{OTFLOW} file", f"*.{OTFLOW}")],
            defaultextension=f".{OTFLOW}",
        )
        if not sections_file:
            return
        print(f"Sections file to load: {sections_file}")
        self._application.add_sections_of_file(sections_file=Path(sections_file))
        self.refresh_items_on_canvas()

    def save_sections(self) -> None:
        sections_file = asksaveasfilename(
            title="Save sections file as",
            filetypes=[(f"{OTFLOW} file", f"*.{OTFLOW}")],
            defaultextension=f".{OTFLOW}",
        )
        if not sections_file:
            return
        print(f"Sections file to save: {sections_file}")
        try:
            self._application.save_flows(Path(sections_file))
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

    def add_section(self) -> None:
        self.set_selected_section_id(None)
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        SectionBuilder(viewmodel=self, canvas=self._canvas, style=EDITED_SECTION_STYLE)

    def get_section_metadata(
        self,
        title: str,
        initial_position: tuple[int, int],
        input_values: dict | None = None,
    ) -> dict:
        return ToplevelSections(
            title=title,
            initial_position=initial_position,
            input_values=input_values,
            show_offset=self._show_offset(),
        ).get_metadata()

    def _show_offset(self) -> bool:
        return True

    def set_new_section(self, data: dict, coordinates: list[tuple[int, int]]) -> None:
        self.__validate_section_information(data, coordinates)
        relative_offset_coordinates_enter = data[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ]
        line_section = LineSection(
            id=self._application.get_section_id(),
            name=data[NAME],
            relative_offset_coordinates={
                EventType.SECTION_ENTER: geometry.RelativeOffsetCoordinate(
                    **relative_offset_coordinates_enter
                )
            },
            plugin_data={},
            coordinates=[self._to_coordinate(coordinate) for coordinate in coordinates],
        )
        self._application.add_section(line_section)
        print(f"New line_section created: {line_section.id}")
        self._update_selected_section(line_section.id)

    def __validate_section_information(
        self, data: dict, coordinates: list[tuple[int, int]]
    ) -> None:
        if not coordinates:
            raise MissingCoordinate("First coordinate is missing")
        elif len(coordinates) == 1:
            raise MissingCoordinate("Second coordinate is missing")
        if not data:
            raise ValueError("Metadata of line_section are not defined")

    def update_section_coordinates(
        self, data: dict, coordinates: list[tuple[int, int]]
    ) -> None:
        self.__validate_section_information(data, coordinates)
        section_id = SectionId(data[ID])
        if not (section := self._application.get_section_for(section_id)):
            raise MissingSection(
                f"Could not update section '{section_id.serialize()}' after editing"
            )
        section.update_coordinates(
            [self._to_coordinate(coordinate) for coordinate in coordinates]
        )
        self._application.update_section(section)
        print(f"Update section: {section.id}")
        self._update_selected_section(section.id)

    def _to_coordinate(self, coordinate: tuple[int, int]) -> geometry.Coordinate:
        return geometry.Coordinate(coordinate[0], coordinate[1])

    def edit_section_geometry(self) -> None:
        if self._selected_section_id is None:
            return
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        CanvasElementDeleter(canvas=self._canvas).delete(
            tag_or_id=self._selected_section_id
        )
        if self._selected_section_id:
            if current_section := self._application.get_section_for(
                SectionId(self._selected_section_id)
            ):
                SectionGeometryEditor(
                    viewmodel=self,
                    canvas=self._canvas,
                    section=current_section,
                    edited_section_style=EDITED_SECTION_STYLE,
                    pre_edit_section_style=PRE_EDIT_SECTION_STYLE,
                    selected_knob_style=SELECTED_KNOB_STYLE,
                )

    def edit_section_metadata(self) -> None:
        if self._selected_section_id is None:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(
                    type(self._treeview_sections).__name__
                )
            position = self._treeview_sections.get_position()
            InfoBox(
                message="Please select a section to edit", initial_position=position
            )
            return
        if self._selected_section_id:
            section_id = SectionId(self._selected_section_id)
            if selected_section := self._application.get_section_for(section_id):
                self._update_metadata(selected_section)

    def _update_metadata(self, selected_section: Section) -> None:
        current_data = selected_section.to_dict()
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        position = get_widget_position(widget=self._canvas)
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
        print(f"Updated line_section Metadata: {updated_section_data}")

    def _set_section_data(self, id: SectionId, data: dict) -> None:
        section = self._flow_parser.parse_section(data)
        self._application.update_section(section)

    def remove_section(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        if not self._selected_section_id:
            position = self._treeview_sections.get_position()
            InfoBox(
                message="Please select a section to remove", initial_position=position
            )
            return
        section_id = SectionId(self._selected_section_id)
        if self._application.is_flow_using_section(section_id):
            message = (
                "The section you want to remove is being used in flows.\n"
                "Please remove the following flows before removing the section.\n"
            )
            for flow_id in self._application.flows_using_section(section_id):
                message += flow_id.serialize() + "\n"
            position = self._treeview_sections.get_position()
            InfoBox(
                message=message,
                initial_position=position,
            )
            return
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
        if self._application.flow_state.selected_flow.get():
            self._draw_arrow_for_selected_flow()

    def _get_sections_to_highlight(self) -> list[str]:
        sections_to_highlight: list[str] = []
        if self._selected_section_id is not None:
            sections_to_highlight = [self._selected_section_id]
        elif selected_flow := self._get_selected_flow():
            if selected_flow is None:
                return []
            start_section_id, end_section_id = (
                selected_flow.start.id,
                selected_flow.end.id,
            )
            sections_to_highlight = [start_section_id, end_section_id]
        return sections_to_highlight

    def _draw_sections(self, sections_to_highlight: list[str]) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        section_painter = SectionPainter(canvas=self._canvas)
        for section in self._get_sections():
            style = (
                SELECTED_SECTION_STYLE
                if section[ID] in sections_to_highlight
                else DEFAULT_SECTION_STYLE
            )
            section_painter.draw(
                tags=[LINE_SECTION],
                id=section[ID],
                coordinates=section[COORDINATES],
                section_style=style,
            )

    def _draw_arrow_for_selected_flow(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        selected_flow = self._get_selected_flow()
        if selected_flow is not None:
            if start_section := self._application.get_section_for(selected_flow.start):
                if end_section := self._application.get_section_for(selected_flow.end):
                    ArrowPainter(self._canvas).draw(
                        start_section=start_section,
                        end_section=end_section,
                        tags=[LINE_SECTION],
                        arrow_style=ARROW_STYLE,
                    )

    def _get_selected_flow(self) -> Optional[Flow]:
        if flow_id := self._application.flow_state.selected_flow.get():
            return self._application.get_flow_for(flow_id)
        return None

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

    def add_flow(self) -> None:
        if flow_data := self._show_distances_window():
            flow_id = self._application.get_flow_id()
            name = flow_data[FLOW_NAME]
            new_from_section_id = SectionId(flow_data[START_SECTION])
            new_to_section_id = SectionId(flow_data[END_SECTION])
            distance = float(flow_data[DISTANCE])
            flow = Flow(
                id=flow_id,
                name=name,
                start=new_from_section_id,
                end=new_to_section_id,
                distance=distance,
            )
            self._application.add_flow(flow)
            self.set_selected_flow_id(flow_id.serialize())
            print(f"Added new flow: {flow_data}")

    def _show_distances_window(
        self,
        input_values: dict = {},
        title: str = "Add flow",
    ) -> dict | None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        position = self._treeview_flows.get_position()
        section_ids = [
            self.__to_id_resource(section) for section in self.get_all_sections()
        ]
        if len(section_ids) < 2:
            InfoBox(
                message="To add a flow, at least two sections are needed",
                initial_position=position,
            )
            return {}
        return ToplevelFlows(
            title=title,
            initial_position=position,
            section_ids=section_ids,
            input_values=input_values,
        ).get_data()

    def __to_id_resource(self, section: Section) -> IdResource:
        return IdResource(id=section.id.serialize(), name=section.name)

    def __update_flow_data(self, flow_data: dict) -> None:
        flow_id = FlowId(flow_data.get(FLOW_ID, ""))
        name = flow_data[FLOW_NAME]
        new_from_section_id = SectionId(flow_data[START_SECTION])
        new_to_section_id = SectionId(flow_data[END_SECTION])
        distance = float(flow_data[DISTANCE])
        if flow := self._application.get_flow_for(flow_id):
            flow.name = name
            flow.start = new_from_section_id
            flow.end = new_to_section_id
            flow.distance = distance
            self._application.update_flow(flow)
        self.set_selected_flow_id(flow_id.serialize())
        self.refresh_items_on_canvas()

    def edit_flow(self) -> None:
        if flow := self._get_selected_flow():
            self._edit_flow(flow)
        else:
            if self._treeview_flows is None:
                raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
            position = self._treeview_flows.get_position()
            InfoBox(message="Please select a flow to edit", initial_position=position)
            return

    def _edit_flow(self, flow: Flow) -> None:
        input_data = {
            FLOW_ID: flow.id.serialize(),
            FLOW_NAME: flow.name,
            START_SECTION: flow.start.id,
            END_SECTION: flow.end.id,
            DISTANCE: flow.distance,
        }

        if flow_data := self._show_distances_window(
            input_values=input_data,
            title="Edit flow",
        ):
            self.__update_flow_data(flow_data=flow_data)

    def remove_flow(self) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        if flow_id := self._application.flow_state.selected_flow.get():
            self._application.remove_flow(flow_id)
            self.refresh_items_on_canvas()
        else:
            position = self._treeview_flows.get_position()
            InfoBox(message="Please select a flow to remove", initial_position=position)

    def start_analysis(self) -> None:
        self._application.start_analysis()

    def save_events(self, file: str) -> None:
        print(f"Eventlist file to save: {file}")
        self._application.save_events(Path(file))

    def set_track_offset(self, offset_x: float, offset_y: float) -> None:
        offset = geometry.RelativeOffsetCoordinate(offset_x, offset_y)
        self._application.track_view_state.track_offset.set(offset)

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
        return self._application.change_track_offset_to_section_offset()

    def validate_date(self, date: str) -> bool:
        return validate_date(date, DATE_FORMAT)

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

    def reset_filter_tracks_by_date(self) -> None:
        self._application.update_date_range_tracks_filter(DateRange(None, None))

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.set_inactive_color_on_filter_by_date_button()

    def get_first_detection_occurrence(self) -> Optional[datetime]:
        return self._application._tracks_metadata.first_detection_occurrence

    def get_last_detection_occurrence(self) -> Optional[datetime]:
        return self._application._tracks_metadata.last_detection_occurrence

    def get_filter_tracks_by_date_setting(self) -> DateRange:
        filter_element = self._application.track_view_state.filter_element.get()
        return filter_element.date_range

    def enable_filter_track_by_date(self) -> None:
        self._application.enable_filter_track_by_date()

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.enable_filter_by_date_button()
        current_date_range = (
            self._application.track_view_state.filter_element.get().date_range
        )
        if current_date_range != DateRange(None, None):
            self._frame_filter.set_active_color_on_filter_by_date_button()
        else:
            self._frame_filter.set_inactive_color_on_filter_by_date_button()

    def disable_filter_track_by_date(self) -> None:
        self._application.disable_filter_track_by_date()

        if self._frame_filter is None:
            raise MissingInjectedInstanceError(AbstractFrameFilter.__name__)

        self._frame_filter.disable_filter_by_date_button()
