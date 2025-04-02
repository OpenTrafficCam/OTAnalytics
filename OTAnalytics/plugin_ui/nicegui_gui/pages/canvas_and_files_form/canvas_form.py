from typing import Optional, Self
from nicegui import ui, events
from nicegui.elements.interactive_image import InteractiveImage
from PIL import Image

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.flow_adapter import SectionRefPointCalculator
from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    CanvasKeys,
    ResourceManager,
)

from nicegui.events import KeyEventArguments
from OTAnalytics.domain.section import SectionId, Section
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle_resources import CircleResources
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.liine_resources import LineResources
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section_resources import SectionResource
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line

from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.test_data_file import TestData


class CanvasForm(AbstractCanvas, AbstractFrameCanvas, AbstractTreeviewInterface):

    def __init__(
            self,
            viewmodel: ViewModel,
            resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._background_image: Optional[InteractiveImage] = None
        self._current_image: Optional[Image.Image] = None
        self._current_sections = TestData
        self._new_sections = self._current_sections
        self._introduce_to_viewmodel()
        self._current_section = None
        self.current_point = None
        self.add_preview_image()
        self._new_section_points = []
        self._new_section_lines = []
        self._new_section = False
        self._new_area_section = False
        self._sections: SectionResource = SectionResource({})
        self._circles: CircleResources = CircleResources({})
        self._lines: LineResources = LineResources({})
    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_canvas(self)
        self._viewmodel.set_canvas(self)
        self._viewmodel.set_treeview_videos(self)
        self._viewmodel.set_treeview_files(self)

    def add_preview_image(self) -> None:
        self._current_image = self._resource_manager.get_image(CanvasKeys.IMAGE_DEFAULT)

    def build(self) -> Self:
        self._background_image = ui.interactive_image("", on_mouse=self._on_pointer_down,
                                                      events=['mousedown', 'mouseup']).classes("w-64").on(
            'svg:pointerdown', lambda e: self.on_svg_pointer_down(e.args)).on('svg:pointermove',
                                                                              lambda e: self.on_mouse_move(e.args)).on(
            'svg:pointerup', lambda e: self.on_pointer_up(e.args))
        self._change_image()
        ui.keyboard(on_key=self.handle_key)
        return self

    def _on_pointer_down(self, e: events.MouseEventArguments):
        if self._new_section:
            self._new_section_points.append(Circle(x=int(e.image_x),  y=int(e.image_y), pointer_event="all", cursor="pointer", fill="orange", id="new_point"))
            self._new_section_lines = []
            self.draw_sections()
            for point in self._new_section_points:
                self._background_image.content += point.to_svg()
            if len(self._new_section_points) >= 2:
                for x in range(len(self._new_section_points) - 1):
                    self._new_section_lines.append(
                        Line(x1=self._new_section_points[x].x, y1=self._new_section_points[x].y, x2=self._new_section_points[x + 1].x,
                             y2=self._new_section_points[x + 1].y, stroke="red", id=id))
            if self._new_area_section and len(self._new_section_lines) >= 2:
                last_line= len(self._new_section_lines) -1
                self._new_section_lines.append(Line(x1=self._new_section_points[0].x, y1=self._new_section_points[0].y,
                     x2=self._new_section_points[last_line].x,
                     y2=self._new_section_points[last_line].y, stroke="red", id=id))
            if self._new_section_lines:
                for line in self._new_section_lines:
                    self._background_image.content += line.to_svg()

    def on_svg_pointer_down(self, e) -> None:
        if self._new_section:
            pass
        else:
            self.current_point = Circle(x=e["image_x"], y=e["image_y"],id=e["element_id"], fill="orange", pointer_event="all")
            self.draw_sections()
            self._background_image.content += self.current_point.to_svg()

    def on_mouse_move(self, e):
        if self.current_point:
            self.current_point = Circle(x=e["image_x"], y=e["image_y"], pointer_event="all", id=e["element_id"], fill="red", radius=50)
            self.draw_sections()
            self._background_image.content += self.current_point.to_svg()

    def on_pointer_up(self, e) -> None:
        if self._new_section:
            pass
        else:
            self._new_point = Circle(x=e["image_x"], y=e["image_y"], pointer_event="all", id=e["element_id"], fill="red")
            self.current_point = None
            self.draw_sections()
            self._background_image.content += self._new_point.to_svg()

    def save_new_point(self):
        if self.current_point:
            if self.current_point["x"]:
                for section in self._current_sections:
                    if section.id == self.current_point["section_id"]:
                        section.coordinates[self.current_point["place_in_coordinates"] - 1] = Coordinate(
                            self.current_point["x"], self.current_point["y"])

    def update_background(self, image: TrackImage) -> None:
        self._current_image = image.as_image()
        self._change_image()

    def _change_image(self) -> None:
        if self._current_image and self._background_image:
            self._background_image.set_source(self._current_image)
        else:
            self.clear_image()

    def clear_image(self) -> None:
        if self._background_image:
            self._background_image.set_source("")

    def load_sections(self) -> None:
        self._viewmodel.refresh_items_on_canvas()

    def add_new_section(self, is_area_section: bool = False) -> None:
        if is_area_section:
            self._new_area_section = True
        self._new_section = True
        self._current_section = [{}]
        self._background_image.on_mouse(self._on_pointer_down)

    def save_new_line(self) -> None:
        self._background_image.on_mouse(self.default_mouse_handler)

    def add_new_area(self) -> None:
        self._new_section = True
        self._new_area_section = True
        self._background_image.on_mouse(self._on_pointer_down)

    def default_mouse_handler(self):
        pass

    def draw_current_point(self) -> None:
        self._background_image.content += self.current_point.to_svg()

    def draw_section(
            self,
            id: str,
            coordinates: list[tuple[int, int]],
            is_selected_section: bool,
            is_area_section: bool = False,
            highlighted_knob_index: int | None = None,
            highlighted_knob_style: dict | None = None,
            text: str | None = None,
            tags: list[str] | None = None,
    ) -> None:
        list_of_circle = []
        list_of_lines = []
        color = "green"
        pointer_event = ""
        if self._background_image:
            if is_selected_section:
                color = "red"
                pointer_event = "all"
            for x, y in coordinates:
                list_of_circle.append(Circle(x=x, y=y, id=id, fill=color, pointer_event=pointer_event))
            for x in range(len(list_of_circle) - 1):
                list_of_lines.append(Line(x1=list_of_circle[x].x, y1=list_of_circle[x].y, x2=list_of_circle[x + 1].x,
                                          y2=list_of_circle[x + 1].y, stroke=color, id=id))
            for circle in list_of_circle:
                self._circles.add(circle)
                self._background_image.content += circle.to_svg()
            for line in list_of_lines:
                self._lines.add(line)
                self._background_image.content += line.to_svg()
            if isinstance(self.current_point, Circle):
                self.draw_current_point()

    def start_section_geometry_editor(
            self,
            section: Section,
            hovered_knob_style: dict | None = None,
            is_area_section: bool = False,
    ) -> None:
        pass

    def draw_arrow(
            self,
            start_section: Section,
            end_section: Section,
            start_refpt_calculator: SectionRefPointCalculator,
            end_refpt_calculator: SectionRefPointCalculator,
            arrow_style: dict | None = None,
            tags: list[str] | None = None,
    ) -> None:
        base = start_refpt_calculator.coordinates_from_section(start_section)
        x1, y1 = base[1]
        x2, y2 = base[2]
        xm = (x1 + x2) / 2
        ym = (y1 + y2) / 2
        base = end_refpt_calculator.coordinates_from_section(end_section)
        x1, y1 = base[1]
        x2, y2 = base[2]
        xm2 = (x1 + x2) / 2
        ym2 = (y1 + y2) / 2
        new_line = Line(x1=xm, x2=xm2, y1=ym, y2=ym2, stroke="green", id="new_line")
        self._background_image.content += new_line.to_svg()

    def delete_element(self, tag_or_id: str) -> None:
        pass

    def start_section_builder(
            self,
            is_area_section: bool = False,
            section: Optional[Section] = None,
    ) -> None:
        pass

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        pass

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def disable(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def update_items(self) -> None:
        pass

    def update_selected_items(self, item_ids: list[str]) -> None:
        pass

    def introduce_to_viewmodel(self) -> None:
        pass
