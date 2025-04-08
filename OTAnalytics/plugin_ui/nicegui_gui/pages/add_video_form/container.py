from typing import Iterable, Self

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

COLUMN_NAME = "name"


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:
    return [
        {
            "name": COLUMN_NAME,
            "label": resource_manager.get(AddVideoKeys.TABLE_NAME),
            "field": "name",
        },
    ]


def map_to_ui(videos: Iterable[Video]) -> list:
    list_of_videos = []
    for video in videos:
        list_of_videos.append(video.get_path())
    return list_of_videos


class AddVideoForm(ButtonForm):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self._add_video_button: ui.button | None = None
        self._remove_video_button: ui.button | None = None
        self._video_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=map_to_ui(self._view_model.get_all_videos()),
            on_select_method=lambda e: self._select_video(e.selection),
            selection="single",
        )
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_video_frame(self)

    def build(self) -> Self:
        self._video_table.build()
        self._add_video_button = ui.button(
            self._resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS),
            on_click=self._view_model.load_tracks(),
        )
        self._remove_video_button = ui.button(
            self._resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS),
        )
        return self

    def get_general_buttons(self) -> list[Button]:
        if self._add_video_button and self._remove_video_button:
            return [self._add_video_button, self._remove_video_button]
        return []

    def _select_video(self, e: dict) -> None:
        self._view_model.set_selected_videos(e[0])

    def _remove_video(self) -> None:
        self._view_model.remove_videos()
