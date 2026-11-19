from nicegui import ui

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ConfigurationBarKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import TrackForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.analysis_form.container import AnalysisForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.static_analysis_config_form import (  # noqa
    StaticAnalysisConfigForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.remarks_form.container import RemarkForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    FlowForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    SectionsForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.svz_metadata_form.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

# Test markers for the workflow groups
MARKER_GROUP_PROJECT = "marker-group-project"
MARKER_GROUP_SVZ = "marker-group-svz"
MARKER_TAB_SECTION = "marker-tab-section"
MARKER_TAB_FLOW = "marker-tab-flow"
MARKER_GROUP_ANALYSIS = "marker-group-analysis"


class ConfigurationBar(TrackListObserver):
    """Workflow accordion of the left panel.

    Every group opens on its own, so sections and flows can be edited side by
    side. An empty project opens the project group; loaded tracks open the
    sections and flows.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
        project_form: ProjectForm,
        static_analysis_config_form: StaticAnalysisConfigForm,
        svz_metadata_form: SvzMetadataForm,
        track_form: TrackForm,
        remark_form: RemarkForm,
        sections_form: SectionsForm,
        flow_form: FlowForm,
        analysis_form: AnalysisForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._view_model = view_model
        self.project_form = project_form
        self.static_analysis_config_form = static_analysis_config_form
        self.svz_metadata_form = svz_metadata_form
        self.track_form = track_form
        self.remark_form = remark_form
        self.sections_form = sections_form
        self.flow_form = flow_form
        self.analysis_form = analysis_form
        # Created by `build()`, which runs when a browser asks for the page.
        self._sections_group: ui.expansion | None = None
        self._flows_group: ui.expansion | None = None

    def build(self) -> None:
        has_tracks = bool(self._view_model.get_all_track_files())
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_PROJECT,
            MARKER_GROUP_PROJECT,
            is_open=not has_tracks,
        ):
            self.project_form.build()
            self.track_form.build()
            self.remark_form.build()
        if self._view_model.show_svz():
            with self._group(
                SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER, MARKER_GROUP_SVZ
            ):
                self.svz_metadata_form.build()
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_SECTIONS,
            MARKER_TAB_SECTION,
            is_open=has_tracks,
        ) as self._sections_group:
            self.sections_form.build()
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_FLOWS,
            MARKER_TAB_FLOW,
            is_open=has_tracks,
        ) as self._flows_group:
            self.flow_form.build()
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_ANALYSIS, MARKER_GROUP_ANALYSIS
        ):
            self.static_analysis_config_form.build()
            self.analysis_form.build()

    def _group(
        self,
        label: ConfigurationBarKeys | SvzMetadataKeys,
        marker: str,
        is_open: bool = False,
    ) -> ui.expansion:
        group = ui.expansion(self._resource_manager.get(label), value=is_open).classes(
            "ota-group"
        )
        group.mark(marker)
        group.props(f"{TEST_ID}={marker}")
        return group

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """Open sections and flows once tracks are loaded."""
        if not len(track_event.added):
            return
        for group in (self._sections_group, self._flows_group):
            if group is not None:
                group.set_value(True)
