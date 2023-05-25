from dataclasses import dataclass
from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from typing import Iterable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import DISTANCES, ViewModel
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import NoSectionsToSave, SectionParser
from OTAnalytics.domain import geometry
from OTAnalytics.domain.section import (
    COORDINATES,
    ID,
    MissingSection,
    Section,
    SectionId,
    SectionListObserver,
)
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.line_section import (
    CanvasElementDeleter,
    CanvasElementPainter,
    SectionBuilder,
    SectionGeometryEditor,
)
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.style import (
    DEFAULT_SECTION_STYLE,
    EDITED_SECTION_STYLE,
    PRE_EDIT_SECTION_STYLE,
    SELECTED_KNOB_STYLE,
    SELECTED_SECTION_STYLE,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_flows import (
    DISTANCE,
    END_SECTION,
    START_SECTION,
    ToplevelFlows,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections

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


@dataclass(frozen=True)
class FlowId:
    from_section: str
    to_section: str


def parse_flow_id(id: str) -> FlowId:
    parts = id.split(" -> ")
    return FlowId(from_section=parts[0], to_section=parts[1])


class DummyViewModel(ViewModel, SectionListObserver):
    def __init__(
        self,
        application: OTAnalyticsApplication,
        section_parser: SectionParser,
    ) -> None:
        self._application = application
        self._section_parser: SectionParser = section_parser
        self._frame_tracks: Optional[AbstractFrameTracks] = None
        self._frame_canvas: Optional[AbstractFrameCanvas] = None
        self._canvas: Optional[AbstractCanvas] = None
        self._treeview_sections: Optional[AbstractTreeviewInterface]
        self._treeview_flows: Optional[AbstractTreeviewInterface]
        self._new_section: dict = {}
        self._selected_section_id: Optional[str] = None
        self.register_to_subjects()

    def register_to_subjects(self) -> None:
        self._application.register_sections_observer(self)
        self._application.register_section_changed_observer(self._on_section_changed)

        self._application.track_view_state.show_tracks.register(
            self._on_show_tracks_state_updated
        )
        self._application.section_state.selected_section.register(
            self._update_selected_section
        )
        self._application.section_state.selected_flow.register(
            self._update_selected_flow
        )
        self._application.track_view_state.background_image.register(
            self._on_background_updated
        )
        self._application.track_view_state.track_offset.register(self._update_offset)

    def _on_section_changed(self, section_id: SectionId) -> None:
        self.notify_sections([section_id])

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
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        self.refresh_sections_on_gui()
        self._treeview_sections.update_items()
        self._treeview_flows.update_items()

    def set_tracks_frame(self, tracks_frame: AbstractFrameTracks) -> None:
        self._frame_tracks = tracks_frame

    def set_canvas(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def set_tracks_canvas(self, tracks_canvas: AbstractFrameCanvas) -> None:
        self._frame_canvas = tracks_canvas

    def set_treeview_sections(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_sections = treeview

    def set_treeview_flows(self, treeview: AbstractTreeviewInterface) -> None:
        self._treeview_flows = treeview

    def _update_selected_section(self, section_id: Optional[SectionId]) -> None:
        current_id = section_id.id if section_id else None
        self._selected_section_id = current_id

        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        self.refresh_sections_on_gui()
        self._treeview_sections.update_selected_items(self._selected_section_id)

    def _update_selected_flow(self, flow_id: Optional[str]) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        self._treeview_flows.update_selected_items(flow_id)

    def get_selected_flow(self) -> Optional[str]:
        return self._application.section_state.selected_flow.get()

    def set_selected_flow_id(self, id: Optional[str]) -> None:
        self._application.section_state.selected_flow.set(id)
        self.refresh_sections_on_gui()

    def set_selected_section_id(self, id: Optional[str]) -> None:
        self._selected_section_id = id
        self._application.set_selected_section(id)

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
        self.refresh_sections_on_gui()

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
            self._application.save_sections(Path(sections_file))
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

    def set_new_section(self, section: Section) -> None:
        self._application.add_section(section)
        print(f"New line_section created: {section}")
        self._update_selected_section(section.id)

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
        updated_section_data = ToplevelSections(
            title="Edit section",
            initial_position=position,
            input_values=current_data,
        ).get_metadata()
        self._set_section_data(
            id=selected_section.id,
            data=updated_section_data,
        )
        self.refresh_sections_on_gui()
        print(f"Updated line_section Metadata: {updated_section_data}")

    def _set_section_data(self, id: SectionId, data: dict) -> None:
        section = self._section_parser.parse_section(data)
        self._application.remove_section(id)
        self._application.add_section(section)

    def remove_section(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(type(self._treeview_sections).__name__)
        if not self._selected_section_id:
            position = self._treeview_sections.get_position()
            InfoBox(
                message="Please select a section to remove", initial_position=position
            )
            return
        self._application.remove_section(SectionId(self._selected_section_id))
        self.refresh_sections_on_gui()

    def refresh_sections_on_gui(self) -> None:
        self._remove_all_sections_from_canvas()
        self._draw_all_sections_on_canvas()

    def _draw_all_sections_on_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        painter = CanvasElementPainter(canvas=self._canvas)
        for section in self._get_sections():
            if section[ID] == self._selected_section_id:
                style = SELECTED_SECTION_STYLE
            else:
                style = DEFAULT_SECTION_STYLE
            painter.draw(
                tags=[LINE_SECTION],
                id=section[ID],
                coordinates=section[COORDINATES],
                section_style=style,
            )

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

    def _remove_all_sections_from_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        CanvasElementDeleter(canvas=self._canvas).delete(tag_or_id=LINE_SECTION)

    def get_all_sections(self) -> Iterable[Section]:
        return self._application.get_all_sections()

    def get_all_flows(self) -> list[str]:
        flows: list[str] = []
        for section in self.get_all_sections():
            distances = section.plugin_data.get(DISTANCES, {})
            flows.extend(
                flow_id(section.id.id, other_section)
                for other_section in distances.keys()
            )
        return flows

    def add_flow(self) -> None:
        if flow_data := self._show_distances_window():
            self.__update_flow_data(flow_data)
            print(f"Added new flow: {flow_data}")

    def _show_distances_window(
        self,
        input_values: dict = {},
        title: str = "Add flow",
    ) -> dict | None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        position = self._treeview_flows.get_position()
        section_ids = [section.id.id for section in self.get_all_sections()]
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

    def __update_flow_data(self, new_flow: dict, old_flow: dict = {}) -> None:
        new_section_id = SectionId(new_flow[START_SECTION])
        if section := self._application.get_section_for(section_id=new_section_id):
            self.__clear_flow_data(flow=old_flow)
            self._set_new_flow_data(section=section, flow=new_flow)
        else:
            raise MissingSection(f"Could not find section for id {new_section_id}")

    def _set_new_flow_data(self, section: Section, flow: dict) -> None:
        plugin_data = section.plugin_data.copy()
        distance_data = plugin_data.get(DISTANCES, {})
        new_data = {flow[END_SECTION]: flow[DISTANCE]}
        distance_data.update(new_data)
        plugin_data[DISTANCES] = distance_data
        self._application.set_section_plugin_data(section.id, plugin_data)

    def __clear_flow_data(self, flow: dict = {}) -> None:
        if flow:
            section_id = SectionId(flow[START_SECTION])
            if section := self._application.get_section_for(section_id=section_id):
                end_section = flow[END_SECTION]
                plugin_data = section.plugin_data.copy()
                distance_data = plugin_data.get(DISTANCES, {})
                del distance_data[end_section]
                plugin_data[DISTANCES] = distance_data
                self._application.set_section_plugin_data(section_id, plugin_data)

    def edit_flow(self) -> None:
        selected_flow = self.get_selected_flow()
        if selected_flow is None:
            if self._treeview_flows is None:
                raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
            position = position = self._treeview_flows.get_position()
            InfoBox(message="Please select a flow to edit", initial_position=position)
            return
        flow = parse_flow_id(selected_flow)
        if from_section := self._application.get_section_for(
            SectionId(flow.from_section)
        ):
            self._edit_flow(flow, from_section)

    def _edit_flow(self, flow: FlowId, from_section: Section) -> None:
        distances = from_section.plugin_data.get(DISTANCES, {})
        distance: str = distances.get(flow.to_section, {})
        input_data = {
            START_SECTION: flow.from_section,
            END_SECTION: flow.to_section,
            DISTANCE: distance,
        }
        old_flow_data = input_data.copy()

        if flow_data := self._show_distances_window(
            input_values=input_data,
            title="Edit flow",
        ):
            self.__update_flow_data(new_flow=flow_data, old_flow=old_flow_data)

    def remove_flow(self) -> None:
        if self._treeview_flows is None:
            raise MissingInjectedInstanceError(type(self._treeview_flows).__name__)
        selected_flow = self.get_selected_flow()
        if not selected_flow:
            position = self._treeview_flows.get_position()
            InfoBox(message="Please select a flow to remove", initial_position=position)
            return
        flow = parse_flow_id(selected_flow)
        data = {
            START_SECTION: flow.from_section,
            END_SECTION: flow.to_section,
        }
        self.__clear_flow_data(data)

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
