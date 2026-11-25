from nicegui import ui

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager, TrackFormKeys)
from OTAnalytics.domain.track_repository import (TrackListObserver,
                                                 TrackRepositoryEvent)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.add_tracks_form import \
    AddTracksForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import \
    AddVideoForm
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

# Mark the Track files and Videos parts of the Project group, formerly tabs.
MARKER_VIDEO_TAB = "marker-video-tab"
MARKER_TRACK_TAB = "marker-track-tab"
MARKER_TRACK_FILE = "marker-track-file"


class TrackForm(TrackListObserver):
    """Track files and videos of the project."""

    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
        add_tracks_form: AddTracksForm,
        add_videos_form: AddVideoForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._view_model = view_model
        self.add_tracks_form = add_tracks_form
        self.add_videos_form = add_videos_form
        # Created by `build()`, which runs when a browser asks for the page.
        self._track_files: ui.column | None = None

    def build(self) -> None:
        with ui.column().classes("ota-file-section"):
            self._subheading(TrackFormKeys.LABEL_TRACK_FILES, MARKER_TRACK_TAB)
            self._track_files = ui.column().classes("ota-file-list")
            self._show_track_files()
            self.add_tracks_form.build()
        with ui.column().classes("ota-file-section"):
            self._subheading(TrackFormKeys.LABEL_VIDEOS, MARKER_VIDEO_TAB)
            self.add_videos_form.build()

    def _subheading(self, key: TrackFormKeys, marker: str) -> None:
        label = ui.label(self._resource_manager.get(key)).classes("ota-subheading")
        label.mark(marker)
        label.props(f"{TEST_ID}={marker}")

    def _show_track_files(self) -> None:
        if self._track_files is None:
            return
        self._track_files.clear()
        names = sorted(path.name for path in self._view_model.get_all_track_files())
        with self._track_files:
            for name in names:
                ui.label(name).classes("ota-file").mark(MARKER_TRACK_FILE)

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        self._show_track_files()
