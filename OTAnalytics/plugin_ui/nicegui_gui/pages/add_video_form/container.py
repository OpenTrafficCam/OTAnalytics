from typing import Iterable, Self

from adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    AddVideoKeys,
    ResourceManager,
)
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import CustomTable

COLUMN_ID = "id"
COLUMN_NAME = "name"


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
        COLUMN_ID: str(video.get_path()),
        COLUMN_NAME: str(video.get_path().name),
    }


def map_to_ui(videos: Iterable[Video]) -> list:
    list_of_videos = []
    for video in videos:
        list_of_videos.append(map_video_to_ui(video))
    return list_of_videos


class AddVideoForm(ButtonForm, AbstractTreeviewInterface):
    def __init__(
        self,
        viewmodel: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._add_video_button: ui.button | None = None
        self._remove_video_button: ui.button | None = None
        self._video_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=[],
            on_select_method=lambda e: self._select_video(e.selection),
            selection="single",
        )
        self.introduce_to_viewmodel()

    def _update_video_table(self) -> None:
        if self._video_table:
            self._video_table.update(map_to_ui(self._viewmodel.get_all_videos()))

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_video_frame(self)
        self._viewmodel.set_treeview_videos(self)

    def build(self) -> Self:
        self._video_table.build()
        self._add_video_button = ui.button(
            self._resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS),
            on_click=lambda _: self._viewmodel.add_video(),
        )
        self._remove_video_button = ui.button(
            self._resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS),
        )
        self._update_video_table()
        return self

    def get_general_buttons(self) -> list[Button]:
        if self._add_video_button and self._remove_video_button:
            return [self._add_video_button, self._remove_video_button]
        return []

    def _select_video(self, e: dict) -> None:
        if len(e) > 0:
            self._viewmodel.set_selected_videos(e[0][COLUMN_ID])
        else:
            self._viewmodel.set_selected_videos([])

    def _remove_video(self) -> None:
        self._viewmodel.remove_videos()

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_videos(ids)

    def disable(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def update_items(self) -> None:
        self._update_video_table()

    def update_selected_items(self, item_ids: list[str]) -> None:
        self._update_video_table()

    def _introduce_to_viewmodel(self) -> None:
        self.introduce_to_viewmodel()

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        return 0, 0
