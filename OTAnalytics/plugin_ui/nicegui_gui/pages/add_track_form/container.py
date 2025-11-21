from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackFormKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.add_tracks_form import (
    AddTracksForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.visualization_offset_slider_form import (  # noqa
    VisualizationOffSetSliderForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
    AddVideoForm,
)

MARKER_TAB_TRACK = "marker-tab-track"
MARKER_TAB_VIDEOS = "marker-tab-videos"


class TrackForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        add_tracks_form: AddTracksForm,
        add_videos_form: AddVideoForm,
        offset_slider_form: VisualizationOffSetSliderForm,
    ) -> None:
        self._resource_manager = resource_manager
        self.add_tracks_form = add_tracks_form
        self.add_videos_form = add_videos_form
        self.offset_slider_form = offset_slider_form

    def build(self) -> None:
        with ui.tabs().classes("w-full") as tabs:
            track_tab = ui.tab(
                self._resource_manager.get(TrackFormKeys.TAB_ONE),
            )
            track_tab.mark(MARKER_TAB_TRACK)
            track_tab.props(f"test-id={MARKER_TAB_TRACK}")
            video_tab = ui.tab(
                self._resource_manager.get(
                    TrackFormKeys.TAB_TWO,
                )
            )
            video_tab.mark(MARKER_TAB_VIDEOS)
            video_tab.props(f"test-id={MARKER_TAB_VIDEOS}")
        with ui.tab_panels(tabs, value=track_tab).classes("w-full"):
            with ui.tab_panel(track_tab):
                self.add_tracks_form.build()
                self.offset_slider_form.build()
            with ui.tab_panel(video_tab):
                self.add_videos_form.build()
