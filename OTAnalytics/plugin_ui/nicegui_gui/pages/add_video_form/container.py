from typing import Iterable, Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    AddVideoKeys,
    ResourceManager,
)
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    COLUMN_ID,
    CustomTable,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

COLUMN_NAME = "name"
MARKER_VIDEO_TABLE = "marker-video-table"
MARKER_BUTTON_ADD = "marker-button-add"
MARKER_BUTTON_REMOVE = "marker-button-remove"


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:
    return [
        {
            "name": COLUMN_NAME,
            "label": resource_manager.get(AddVideoKeys.TABLE_NAME),
            "field": "name",
        },
    ]


def map_video_to_ui(video: Video) -> dict:
    return {
        COLUMN_ID: get_column_id_for(video),
        COLUMN_NAME: str(video.get_path().name),
    }


def get_column_id_for(video: Video) -> str:
    return str(video.get_path())


def map_to_ui(videos: Iterable[Video]) -> list:
    list_of_videos = []
    for video in videos:
        list_of_videos.append(map_video_to_ui(video))
    # Ensure deterministic alphabetical order by visible filename
    list_of_videos.sort(key=lambda r: r.get(COLUMN_NAME, "").lower())
    return list_of_videos


class AddVideoForm(ButtonForm, AbstractTreeviewInterface):
    def __init__(
        self,
        viewmodel: ViewModel,
        track_view_state: TrackViewState,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._track_view_state = track_view_state
        self._resource_manager = resource_manager
        self._add_video_button: ui.button | None = None
        self._remove_video_button: ui.button | None = None
        self._video_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=[],
            on_select_method=lambda e: self._select_video(e),
            selection="multiple",
            on_row_click_method=lambda e: self._on_row_click(e),
            marker=MARKER_VIDEO_TABLE,
        )
        self.introduce_to_viewmodel()

    def _update_video_table(self) -> None:
        self._video_table.update(map_to_ui(self._viewmodel.get_all_videos()))
        selected_video_ids = [
            get_column_id_for(video)
            for video in self._track_view_state.selected_videos.get()
        ]
        self.update_selected_items(selected_video_ids)

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_video_frame(self)
        self._viewmodel.set_treeview_videos(self)

    def build(self) -> Self:
        self._video_table.build()
        self._add_video_button = ui.button(
            self._resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS),
            on_click=lambda _: self._viewmodel.add_video(),
        )
        self._add_video_button.mark(MARKER_BUTTON_ADD)
        self._add_video_button.props(f"{TEST_ID}={MARKER_BUTTON_ADD}")
        self._remove_video_button = ui.button(
            self._resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS),
            on_click=lambda _: self._remove_video(),
        )
        self._remove_video_button.mark(MARKER_BUTTON_REMOVE)
        self._remove_video_button.props(f"{TEST_ID}={MARKER_BUTTON_REMOVE}")
        self._update_video_table()
        return self

    def get_general_buttons(self) -> list[Button]:
        if self._add_video_button and self._remove_video_button:
            return [self._add_video_button, self._remove_video_button]
        return []

    def _select_video(self, e: object) -> None:
        """Handle selection events from the NiceGUI table robustly.

        Accepts either:
        - an event object with attribute `selection` (NiceGUI)
        - a dict with key "selection"
        - a list of selected row dicts directly
        """
        selection: list[dict] | None = None
        # 1) NiceGUI event with attribute
        sel_attr = getattr(e, "selection", None)
        if isinstance(sel_attr, list):
            selection = sel_attr
        # 2) Dict event shape
        if selection is None and isinstance(e, dict):
            maybe = e.get("selection")  # type: ignore[assignment]
            if isinstance(maybe, list):
                selection = maybe
        # 3) Direct list of rows
        if selection is None and isinstance(e, list):
            selection = e
        if not selection:
            return
        selected_videos = [
            element.get(COLUMN_ID, "")
            for element in selection
            if isinstance(element, dict)
        ]
        self._viewmodel.set_selected_videos([s for s in selected_videos if s])

    def _remove_video(self) -> None:
        self._viewmodel.remove_videos()

    def _on_row_click(self, e: object) -> None:
        """Handle direct row clicks to ensure selection updates.

        NiceGUI passes event args with a 'row' key containing the clicked row dict.
        We extract the COLUMN_ID from that row and set it as the single selection.
        """
        try:
            row = None
            if hasattr(e, "args"):
                if isinstance(e.args, dict):
                    row = e.args.get("row")
                elif isinstance(e.args, (list, tuple)) and len(e.args) >= 2:
                    # NiceGUI forwards Quasar's (evt, row, pageIndex)
                    row = e.args[1]
            elif isinstance(e, dict):
                row = e.get("row")
            if isinstance(row, dict):
                vid = row.get(COLUMN_ID)
                if vid:
                    self._viewmodel.set_selected_videos([vid])
        except Exception:
            # be resilient to event shape differences
            pass

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_videos(ids)

    def disable(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def update_items(self) -> None:
        self._update_video_table()

    def update_selected_items(self, item_ids: list[str]) -> None:
        self._video_table.select(item_ids)

    def _introduce_to_viewmodel(self) -> None:
        self.introduce_to_viewmodel()

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        return 0, 0
