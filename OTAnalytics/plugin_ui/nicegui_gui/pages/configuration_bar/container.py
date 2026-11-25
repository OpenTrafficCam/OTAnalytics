from nicegui import ui

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ConfigurationBarKeys, ResourceManager, SvzMetadataKeys)
from OTAnalytics.domain.event import EventRepositoryEvent
from OTAnalytics.domain.flow import FlowId, FlowListObserver
from OTAnalytics.domain.section import (SectionListObserver,
                                        SectionRepositoryEvent)
from OTAnalytics.domain.track_repository import (TrackListObserver,
                                                 TrackRepositoryEvent)
from OTAnalytics.domain.video import Video, VideoListObserver
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import \
    TrackForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.analysis_form.container import \
    AnalysisForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import \
    ProjectForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.static_analysis_config_form import \
    StaticAnalysisConfigForm  # noqa
from OTAnalytics.plugin_ui.nicegui_gui.pages.remarks_form.container import \
    RemarkForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import \
    FlowForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import \
    SectionsForm  # noqa
from OTAnalytics.plugin_ui.nicegui_gui.pages.svz_metadata_form.svz_metadata_form import \
    SvzMetadataForm  # noqa
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

# Test markers for the workflow groups
MARKER_GROUP_PROJECT = "marker-group-project"
MARKER_GROUP_SVZ = "marker-group-svz"
MARKER_TAB_SECTION = "marker-tab-section"
MARKER_TAB_FLOW = "marker-tab-flow"
MARKER_GROUP_ANALYSIS = "marker-group-analysis"
SVZ_STEP = "SVZ"


class ConfigurationBar(
    TrackListObserver, VideoListObserver, SectionListObserver, FlowListObserver
):
    """Workflow accordion of the left panel.

    Every group opens on its own, so sections and flows can be edited side by
    side. An empty project opens the project group; loaded tracks open the
    sections and flows. Each group header shows its workflow step, its title
    and a summary of its content, which follows the project.
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
        self._summaries: dict[str, ui.label] = {}

    def build(self) -> None:
        self._summaries = {}
        has_tracks = bool(self._view_model.get_all_track_files())
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_PROJECT,
            MARKER_GROUP_PROJECT,
            step="1",
            is_open=not has_tracks,
        ):
            self.project_form.build()
            self.track_form.build()
            self.remark_form.build()
        if self._view_model.show_svz():
            with self._group(
                SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER,
                MARKER_GROUP_SVZ,
                step=SVZ_STEP,
            ):
                self.svz_metadata_form.build()
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_SECTIONS,
            MARKER_TAB_SECTION,
            step="2",
            is_open=has_tracks,
        ) as self._sections_group:
            self.sections_form.build()
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_FLOWS,
            MARKER_TAB_FLOW,
            step="3",
            is_open=has_tracks,
        ) as self._flows_group:
            self.flow_form.build()
        with self._group(
            ConfigurationBarKeys.LABEL_GROUP_ANALYSIS, MARKER_GROUP_ANALYSIS, step="4"
        ):
            self.static_analysis_config_form.build()
            self.analysis_form.build()
        self._update_summaries()

    def _group(
        self,
        label: ConfigurationBarKeys | SvzMetadataKeys,
        marker: str,
        step: str,
        is_open: bool = False,
    ) -> ui.expansion:
        group = ui.expansion(value=is_open).classes("ota-group")
        group.mark(marker)
        group.props(f"{TEST_ID}={marker}")
        with group.add_slot("header"):
            with ui.row(wrap=False).classes("ota-group-header"):
                badge = ui.label(step).classes("ota-step-badge")
                if step == SVZ_STEP:
                    badge.classes("ota-step-badge--secondary")
                with ui.column().classes("ota-group-heading"):
                    ui.label(self._resource_manager.get(label)).classes(
                        "ota-group-title"
                    )
                    self._summaries[marker] = ui.label().classes("ota-group-summary")
        return group

    def _update_summaries(self) -> None:
        if not self._summaries:
            return
        flows = list(self._view_model.get_all_flows())
        assigned = sum(self._view_model.get_tracks_assigned_to_each_flow().values())
        summaries = {
            MARKER_GROUP_PROJECT: self._summary(
                ConfigurationBarKeys.SUMMARY_PROJECT,
                tracks=len(self._view_model.get_all_track_files()),
                videos=len(self._view_model.get_all_videos()),
            ),
            MARKER_GROUP_SVZ: self._summary(ConfigurationBarKeys.SUMMARY_SVZ),
            MARKER_TAB_SECTION: self._summary(
                ConfigurationBarKeys.SUMMARY_SECTIONS,
                sections=len(list(self._view_model.get_all_sections())),
            ),
            MARKER_TAB_FLOW: self._summary(
                ConfigurationBarKeys.SUMMARY_FLOWS,
                flows=len(flows),
                assigned=assigned,
            ),
            MARKER_GROUP_ANALYSIS: self._summary(ConfigurationBarKeys.SUMMARY_ANALYSIS),
        }
        for marker, label in self._summaries.items():
            label.set_text(summaries[marker])

    def _summary(self, key: ConfigurationBarKeys, **values: int) -> str:
        return self._resource_manager.get(key).format(**values)

    def notify_videos(self, videos: list[Video]) -> None:
        self._update_summaries()

    def notify_sections(self, sections: SectionRepositoryEvent) -> None:
        self._update_summaries()

    def notify_flows(self, flows: list[FlowId]) -> None:
        self._update_summaries()

    def notify_events(self, _: EventRepositoryEvent) -> None:
        """Assigning tracks changes the number of assigned tracks."""
        self._update_summaries()

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """Open sections and flows once tracks are loaded."""
        self._update_summaries()
        if not len(track_event.added):
            return
        for group in (self._sections_group, self._flows_group):
            if group is not None:
                group.set_value(True)
