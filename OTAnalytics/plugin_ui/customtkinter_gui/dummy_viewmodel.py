from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from typing import Iterable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame import AbstractTracksCanvas
from OTAnalytics.adapter_ui.abstract_tracks_frame import AbstractTracksFrame
from OTAnalytics.adapter_ui.abstract_treeview import AbstractTreeviewSections
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import NoSectionsToSave, SectionParser
from OTAnalytics.domain import geometry
from OTAnalytics.domain.section import (
    END,
    ID,
    START,
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
)
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections

LINE_SECTION: str = "line_section"


class MissingInjectedInstanceError(Exception):
    """Raise when no instance of an object was injected before referencing it"""

    def __init__(self, injected_object: str):
        message = (
            f"An instance of {injected_object} has to be injected before referencing it"
        )
        super().__init__(message)


class DummyViewModel(ViewModel, SectionListObserver):
    def __init__(
        self,
        application: OTAnalyticsApplication,
        section_parser: SectionParser,
    ) -> None:
        self._application = application
        self._section_parser: SectionParser = section_parser
        self._tracks_frame: Optional[AbstractTracksFrame] = None
        self._tracks_canvas: Optional[AbstractTracksCanvas] = None
        self._canvas: Optional[AbstractCanvas] = None
        self._treeview_sections: Optional[AbstractTreeviewSections]
        self._new_section: dict = {}
        self._selected_section_id: Optional[str] = None
        self.register_to_subjects()

    def register_to_subjects(self) -> None:
        self._application.register_sections_observer(self)

        self._application.track_view_state.show_tracks.register(
            self._on_show_tracks_state_updated
        )
        self._application.section_state.selected_section.register(
            self._update_selected_section
        )
        self._application.track_view_state.background_image.register(
            self._on_background_updated
        )
        self._application.track_view_state.track_offset.register(self._update_offset)

    def _on_show_tracks_state_updated(self, value: Optional[bool]) -> None:
        if self._tracks_canvas is None:
            raise MissingInjectedInstanceError(AbstractTracksCanvas.__name__)

        new_value = value or False
        self._tracks_canvas.update_show_tracks(new_value)

    def _on_background_updated(self, image: Optional[TrackImage]) -> None:
        if self._tracks_canvas is None:
            raise MissingInjectedInstanceError(AbstractTracksCanvas.__name__)

        if image:
            self._tracks_canvas.update_background(image)

    def update_show_tracks_state(self, value: bool) -> None:
        self._application.track_view_state.show_tracks.set(value)

    def notify_sections(self, sections: list[SectionId]) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(AbstractTreeviewSections.__name__)
        self._treeview_sections.update_sections()

    def set_tracks_frame(self, tracks_frame: AbstractTracksFrame) -> None:
        self._tracks_frame = tracks_frame

    def set_canvas(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def set_tracks_canvas(self, tracks_canvas: AbstractTracksCanvas) -> None:
        self._tracks_canvas = tracks_canvas

    def set_treeview_sections(self, treeview: AbstractTreeviewSections) -> None:
        self._treeview_sections = treeview

    def _update_selected_section(self, section_id: Optional[SectionId]) -> None:
        current_id = section_id.id if section_id else None
        self._selected_section_id = current_id

        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(AbstractTreeviewSections.__name__)
        self._treeview_sections.update_selection(current_id)

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
            title="Load sections file", filetypes=[("otflow file", "*.otflow")]
        )
        if not sections_file:
            return
        print(f"Sections file to load: {sections_file}")
        self._application.add_sections_of_file(sections_file=Path(sections_file))
        self.refresh_sections_on_gui()

    def save_sections(self) -> None:
        sections_file = asksaveasfilename(
            title="Save sections file as", filetypes=[("sections file", "*.otflow")]
        )
        if not sections_file:
            return
        print(f"Sections file to save: {sections_file}")
        try:
            self._application.save_sections(Path(sections_file))
        except NoSectionsToSave as cause:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(
                    AbstractTreeviewSections.__name__
                ) from cause
            position = get_widget_position(widget=self._treeview_sections)
            InfoBox(
                message="No sections to save, please add new sections first",
                initial_position=position,
            )
            return

    def add_section(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        SectionBuilder(viewmodel=self, canvas=self._canvas)

    def set_new_section(self, section: Section) -> None:
        self._application.add_section(section)
        print(f"New line_section created: {section}")
        self.refresh_sections_on_gui()

    def edit_section_geometry(self) -> None:
        if self._selected_section_id is None:
            return
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        CanvasElementDeleter(canvas=self._canvas).delete(
            tag_or_id=self._selected_section_id
        )
        current_section = None
        if self._selected_section_id:
            current_section = self._application.get_section_for(
                SectionId(self._selected_section_id)
            )
        SectionBuilder(viewmodel=self, canvas=self._canvas, section=current_section)
        self.refresh_sections_on_gui()

    def edit_section_metadata(self) -> None:
        if self._selected_section_id is None:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(AbstractTreeviewSections.__name__)
            position = get_widget_position(self._treeview_sections)
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
            raise MissingInjectedInstanceError(AbstractTreeviewSections.__name__)
        if not self._selected_section_id:
            position = get_widget_position(widget=self._treeview_sections)
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
        for line_section in self._get_sections():
            painter.draw(
                tags=[LINE_SECTION],
                id=line_section[ID],
                start=line_section[START],
                end=line_section[END],
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
        section[START] = self._to_coordinate_tuple(section[START])
        section[END] = self._to_coordinate_tuple(section[END])
        return section

    def _to_coordinate_tuple(self, coordinate: dict) -> tuple[int, int]:
        return (coordinate[geometry.X], coordinate[geometry.Y])

    def _remove_all_sections_from_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(AbstractCanvas.__name__)
        CanvasElementDeleter(canvas=self._canvas).delete(tag_or_id=LINE_SECTION)

    def get_all_sections(self) -> Iterable[Section]:
        return self._application.get_all_sections()

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
        if self._tracks_frame is None:
            raise MissingInjectedInstanceError(AbstractTracksFrame.__name__)

        if offset:
            self._tracks_frame.update_offset(offset.x, offset.y)

    def change_track_offset_to_section_offset(self) -> None:
        return self._application.change_track_offset_to_section_offset()
