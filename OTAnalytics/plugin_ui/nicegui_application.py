from functools import cached_property
from pathlib import Path
from typing import Protocol

from OTAnalytics.adapter_ui.local_file_providers import (
    LocalTrackFileProvider,
    LocalVideoFileProvider,
)
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.application.use_cases.provide_input_files import (
    ProvideTrackFiles,
    ProvideVideoFiles,
)
from OTAnalytics.application.use_cases.reset_application import ResetApplication
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.transfer_mode import TransferMode
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PilImageFactory,
    TrackImageFactory,
)
from OTAnalytics.plugin_s3.cleanup import WipeUserSource, WipeUserSourceOnReset
from OTAnalytics.plugin_s3.config.env_vars import S3Env, transfer_mode_from_env
from OTAnalytics.plugin_s3.config.parsing import parse_s3_config
from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_s3.connect import S3Connection
from OTAnalytics.plugin_s3.download import S3Download
from OTAnalytics.plugin_s3.download_objects import DownloadObjects
from OTAnalytics.plugin_s3.list_objects import S3ListObjects
from OTAnalytics.plugin_s3.s3_file_providers import (
    AskForLoadWindow,
    S3TrackFileProvider,
    S3VideoFileProvider,
)
from OTAnalytics.plugin_ui.gui_application import OtAnalyticsGuiApplicationStarter
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.progressbar import (
    NiceguiProgressbarBuilder,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.add_tracks_form import (
    AddTracksForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import TrackForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.visualization_offset_slider_form import (  # noqa
    VisualizationOffSetSliderForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
    AddVideoForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.analysis_form.container import AnalysisForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    CanvasForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.container import (
    CanvasAndFilesForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.files_form import (
    FilesForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.remarks_form.container import RemarkForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.container import (
    SectionsAndFlowForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    FlowForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    SectionsForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.svz_metadata_form.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.track_statistics_form.container import (
    TrackStatisticForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters import (
    VisualizationFilters,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    VisualizationFiltersForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers import (
    VisualizationLayers,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    LayersForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.workspace import Workspace
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory

DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT = 5000


class Webserver(Protocol):
    def run(self) -> None: ...

    def stop(self) -> None: ...

    def build_pages(self) -> None: ...


class OtAnalyticsNiceGuiApplicationStarter(OtAnalyticsGuiApplicationStarter):

    def start_ui(self) -> None:
        self.webserver.run()

    @cached_property
    def webserver(self) -> Webserver:
        from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
        from OTAnalytics.plugin_ui.nicegui_gui.nicegui.nicegui_webserver import (
            NiceguiWebserver,
        )
        from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.nicegui_layout_components import (  # noqa
            NiceguiLayoutComponents,
        )
        from OTAnalytics.plugin_ui.nicegui_gui.page_builders.main_page_builder import (
            MainPageBuilder,
        )

        main_page_builder = MainPageBuilder(
            ENDPOINT_MAIN_PAGE,
            configuration_bar=self.configuration_bar,
            workspace=self.workspace,
            visualization_filters=self.visualization_filters,
            visualization_layers=self.visualization_layers,
        )
        # Before anything is preloaded: reclaims whatever a crash, an OOM kill
        # or a docker kill left staged from the previous run.
        if wipe := self.wipe_user_source:
            wipe.wipe()
        self.preload_input_files.load(self.run_config)
        return NiceguiWebserver(
            page_builders=[main_page_builder],
            layout_components=NiceguiLayoutComponents(),
            hostname=DEFAULT_HOSTNAME,
            port=DEFAULT_PORT,
        )

    @cached_property
    def analysis_form(self) -> AnalysisForm:
        return AnalysisForm(self.resource_manager, self.view_model)

    @cached_property
    def configuration_bar(self) -> ConfigurationBar:
        return ConfigurationBar(
            resource_manager=self.resource_manager,
            project_form=self.project_form,
            svz_metadata_form=self.svz_metadata_form,
            track_form=self.track_form,
            sections_and_flow_form=self.sections_and_flow_form,
            analysis_form=self.analysis_form,
        )

    @cached_property
    def canvas_and_files_form(self) -> CanvasAndFilesForm:
        return CanvasAndFilesForm(
            self.resource_manager, self.canvas_form, self.files_form
        )

    @cached_property
    def remarks_form(self) -> RemarkForm:
        return RemarkForm(self.resource_manager, self.view_model)

    @cached_property
    def sections_and_flow_form(self) -> SectionsAndFlowForm:
        return SectionsAndFlowForm(
            self.resource_manager,
            self.section_form,
            self.flow_form,
        )

    @cached_property
    def track_form(self) -> TrackForm:
        return TrackForm(
            self.resource_manager,
            self.add_track_form,
            self.add_video_form,
            self.visualization_offset_slider_form,
        )

    @cached_property
    def add_track_form(self) -> AddTracksForm:
        return AddTracksForm(self.view_model, self.resource_manager)

    @cached_property
    def add_video_form(self) -> AddVideoForm:
        return AddVideoForm(
            self.view_model, self.track_view_state, self.resource_manager
        )

    @cached_property
    def flow_form(self) -> FlowForm:
        return FlowForm(self.view_model, self.flow_state, self.resource_manager)

    @cached_property
    def canvas_form(self) -> CanvasForm:
        return CanvasForm(self.view_model, self.resource_manager)

    @cached_property
    def files_form(self) -> FilesForm:
        return FilesForm(self.view_model, self.resource_manager)

    @cached_property
    def section_form(self) -> SectionsForm:
        return SectionsForm(
            self.view_model,
            self.section_state,
            self.resource_manager,
        )

    @cached_property
    def visualization_offset_slider_form(self) -> VisualizationOffSetSliderForm:
        return VisualizationOffSetSliderForm(self.view_model, self.resource_manager)

    @cached_property
    def project_form(self) -> ProjectForm:
        return ProjectForm(self.view_model, self.resource_manager)

    @cached_property
    def layers_form(self) -> LayersForm:
        layer_groups, layers = self.layers
        return LayersForm(self.view_model, self.resource_manager, layer_groups)

    @cached_property
    def svz_metadata_form(self) -> SvzMetadataForm:
        return SvzMetadataForm(self.view_model, self.resource_manager)

    @cached_property
    def workspace(self) -> Workspace:
        return Workspace(self.resource_manager, self.canvas_and_files_form)

    @cached_property
    def visualization_filter_form(self) -> VisualizationFiltersForm:
        return VisualizationFiltersForm(self.resource_manager, self.view_model)

    @cached_property
    def visualization_filters(self) -> VisualizationFilters:
        return VisualizationFilters(
            self.resource_manager,
            self.visualization_filter_form,
            self.remarks_form,
            self.track_statistic_form,
        )

    @cached_property
    def visualization_layers(self) -> VisualizationLayers:
        return VisualizationLayers(self.resource_manager, self.layers_form)

    @cached_property
    def track_statistic_form(self) -> TrackStatisticForm:
        return TrackStatisticForm(self.resource_manager, self.view_model)

    @cached_property
    def ui_factory(self) -> UiFactory:
        return NiceGuiUiFactory(
            self.resource_manager, self.run_config.file_picker_directory
        )

    @cached_property
    def progressbar_builder(self) -> ProgressbarBuilder:
        return NiceguiProgressbarBuilder(self.resource_manager)

    @cached_property
    def transfer_mode(self) -> TransferMode:
        return transfer_mode_from_env()

    @cached_property
    def s3_config(self) -> S3Config | None:
        """The S3 settings, or None when not running in S3 mode."""
        if self.transfer_mode != TransferMode.S3:
            return None
        return parse_s3_config(S3Env())

    @cached_property
    def provide_track_files(self) -> ProvideTrackFiles:
        if config := self.s3_config:
            return S3TrackFileProvider(
                dialog=self.ask_for_load_window,
                list_objects=self.s3_list_objects,
                download_objects=self.download_objects,
                config=config,
            )
        return LocalTrackFileProvider(self.ui_factory)

    @cached_property
    def provide_video_files(self) -> ProvideVideoFiles:
        if config := self.s3_config:
            return S3VideoFileProvider(
                dialog=self.ask_for_load_window,
                list_objects=self.s3_list_objects,
                download_objects=self.download_objects,
                config=config,
            )
        return LocalVideoFileProvider(self.ui_factory)

    @cached_property
    def reset_application(self) -> ResetApplication:
        """Resetting a project also frees the staged downloads it used.

        Safe only in this order: the repositories drop every `Video` reference
        before the files behind them are removed.
        """
        if wipe := self.wipe_user_source:
            return WipeUserSourceOnReset(
                self.clear_all_repositories, self.reset_state, wipe
            )
        return ResetApplication(self.clear_all_repositories, self.reset_state)

    @cached_property
    def wipe_user_source(self) -> WipeUserSource | None:
        if config := self.s3_config:
            return WipeUserSource(Path(config.user_source))
        return None

    @cached_property
    def ask_for_load_window(self) -> AskForLoadWindow:
        from OTAnalytics.plugin_ui.nicegui_gui.dialogs.load_window_dialog import (
            LoadWindowDialog,
        )

        return LoadWindowDialog(self.resource_manager)

    @cached_property
    def s3_connection(self) -> S3Connection:
        return S3Connection()

    @cached_property
    def s3_list_objects(self) -> S3ListObjects:
        return S3ListObjects(self.s3_connection, self._required_s3_config())

    @cached_property
    def download_objects(self) -> DownloadObjects:
        config = self._required_s3_config()
        return DownloadObjects(
            download=S3Download(self.s3_connection, config),
            user_source=Path(config.user_source),
            concurrency=config.download_concurrency,
            progressbar_builder=NiceguiProgressbarBuilder(self.resource_manager),
        )

    def _required_s3_config(self) -> S3Config:
        if config := self.s3_config:
            return config
        raise ValueError("S3 is not configured; this is only reachable in s3 mode.")

    @cached_property
    def track_image_factory(self) -> TrackImageFactory:
        return PilImageFactory()
