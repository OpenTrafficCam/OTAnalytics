from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.add_tracks_form import (
    AddTracksForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.offset_slider_form import (
    OffSetSliderForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class TrackForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        add_tracks_form: AddTracksForm,
        offset_slider_form: OffSetSliderForm,
    ) -> None:
        self._resource_manager = resource_manager
        self.add_tracks_form = add_tracks_form
        self.offset_slider_form = offset_slider_form

    def build(self) -> None:
        with ui.tabs().classes("w-full") as tabs:
            one = ui.tab(
                self._resource_manager.get(ProjectKeys.LABEL_PROJECT_FORM_HEADER)
            )
            two = ui.tab(
                self._resource_manager.get(
                    SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER
                )
            )
        with ui.tab_panels(tabs, value=one).classes("w-full"):
            with ui.tab_panel(one):
                self.add_tracks_form.build()
                self.offset_slider_form.build()
            with ui.tab_panel(two):
                pass
