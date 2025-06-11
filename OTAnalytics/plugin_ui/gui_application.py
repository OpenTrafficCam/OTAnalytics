from abc import abstractmethod
from functools import cached_property

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    FilterOutCuttingSections,
    MissingEventsSectionProvider,
    SectionProvider,
    SimpleCreateIntersectionEvents,
)
from OTAnalytics.domain.track import TrackIdProvider
from OTAnalytics.plugin_filter.pandas_track_id import PandasTrackIdProvider
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
)
from OTAnalytics.plugin_ui.base_application import BaseOtAnalyticsApplicationStarter


class OtAnalyticsGuiApplicationStarter(BaseOtAnalyticsApplicationStarter):
    def start(self) -> None:
        self.register_observers()
        self.start_ui()

    @abstractmethod
    def start_ui(self) -> None:
        raise NotImplementedError

    def register_observers(self) -> None:
        self.track_repository.register_tracks_observer(self.clear_all_intersections)
        self.section_repository.register_sections_observer(self.clear_all_intersections)
        self.section_repository.register_section_changed_observer(
            self.clear_all_intersections.on_section_changed
        )
        self.track_view_state.selected_videos.register(
            self.video_image_size_updater.notify_videos
        )
        self.track_view_state.selected_videos.register(
            self.track_image_updater.notify_video
        )
        # TODO: Should not register to tracks_metadata._classifications but to
        # TODO: ottrk metadata detection classes
        self.tracks_metadata._classifications.register(
            observer=self.color_palette_provider.update
        )
        self.section_repository.register_sections_observer(
            self.cut_tracks_intersecting_section
        )
        self.section_repository.register_section_changed_observer(
            self.cut_tracks_intersecting_section.notify_section_changed
        )
        self.cut_tracks_intersecting_section.register(
            self.clear_all_events.on_tracks_cut
        )
        self.application.connect_clear_event_repository_observer()
        self.application.register_video_observer(self.view_model)
        self.application.register_sections_observer(self.view_model)
        self.application.register_flows_observer(self.view_model)
        self.application.register_flow_changed_observer(self.view_model.on_flow_changed)
        self.track_view_state.selected_videos.register(
            self.view_model.update_selected_videos
        )
        self.section_state.selected_sections.register(
            self.view_model.update_selected_sections
        )
        self.flow_state.selected_flows.register(self.view_model.update_selected_flows)
        self.track_view_state.background_image.register(
            self.view_model.on_background_updated
        )
        self.track_view_state.track_offset.register(self.view_model.update_offset)
        self.track_view_state.filter_element.register(self.view_model.update_date_range)
        self.track_view_state.filter_element.register(
            self.view_model.update_track_statistics
        )
        self.action_state.action_running.register(
            self.view_model.notify_action_running_state
        )
        self.track_view_state.filter_date_active.register(
            self.view_model.change_filter_date_active
        )
        self.track_view_state.filter_element.register(
            self.selected_video_updater.on_filter_element_change
        )
        # TODO: Refactor observers - move registering to subjects happening in
        #   constructor dummy_viewmodel
        # cut_tracks_intersecting_section.register(
        #    cached_pandas_track_provider.on_tracks_cut
        # )
        self.cut_tracks_intersecting_section.register(self.view_model.on_tracks_cut)
        self.view_model.register_observers()
        self.application.connect_observers()
        self.datastore.register_tracks_observer(self.selected_video_updater)
        self.datastore.register_tracks_observer(self.view_model)
        self.datastore.register_tracks_observer(self.track_image_updater)
        self.datastore.register_video_observer(self.selected_video_updater)
        self.datastore.register_section_changed_observer(
            self.track_image_updater.notify_section_changed
        )
        self.start_new_project.register(self.view_model.on_start_new_project)
        self.event_repository.register_observer(self.track_image_updater.notify_events)
        self.event_repository.register_observer(self.view_model.update_track_statistics)
        self.load_otflow.register(self.file_state.last_saved_config.set)
        self.load_otconfig.register(self.file_state.last_saved_config.set)
        self.load_otconfig.register(self.view_model.update_remark_view)
        self.project_updater.register(self.view_model.update_quick_save_button)
        self.track_file_repository.register(self.view_model.update_quick_save_button)
        self.project_updater.register(self.view_model.show_current_project)
        self.project_updater.register(self.view_model.update_svz_metadata_view)
        layer_groups, layers = self.layers
        for group in layer_groups:
            group.register(self.track_image_updater.notify_layers)

        # configure observers for count plot saver
        self.track_view_state.count_plots.register(self.save_count_plots.save)

    @cached_property
    def view_model(self) -> ViewModel:
        return DummyViewModel(
            self.application,
            self.ui_factory,
            self.flow_parser,
            self.flow_name_generator,
            event_list_export_formats=AVAILABLE_EVENTLIST_EXPORTERS,
            show_svz=self.run_config.show_svz,
            add_new_section=self.add_new_section,
            update_section_coordinates=self.update_section_coordinates,
        )

    @cached_property
    def application(self) -> OTAnalyticsApplication:
        return OTAnalyticsApplication(
            self.datastore,
            self.track_state,
            self.track_view_state,
            self.section_state,
            self.flow_state,
            self.file_state,
            self.tracks_metadata,
            self.videos_metadata,
            self.action_state,
            self.filter_element_settings_restorer,
            self.get_all_track_files,
            self.flow_generator,
            self.create_intersection_events,
            self.export_counts,
            self.create_events,
            self.load_otflow,
            self.add_section,
            self.add_flow,
            self.clear_all_events,
            self.start_new_project,
            self.project_updater,
            self.save_otconfig,
            self.load_track_files,
            self.enable_filter_track_by_date,
            self.switch_to_previous,
            self.switch_to_next,
            self.switch_to_event,
            self.save_otflow,
            self.quick_save_configuration,
            self.load_otconfig,
            self.config_has_changed,
            self.export_road_user_assignments,
            self.save_path_suggester,
            self.calculate_track_statistics,
            self.number_of_tracks_assigned_to_each_flow,
            self.export_track_statistics,
            self.get_current_remark,
            self.update_count_plots,
        )

    @cached_property
    def all_filtered_track_ids(self) -> TrackIdProvider:
        return PandasTrackIdProvider(
            self.visualization_builder._get_data_provider_all_filters_with_offset()
        )

    @cached_property
    def create_events(self) -> CreateEvents:
        return self._create_use_case_create_events(
            self.section_provider_event_creation_ui,
            self.clear_all_events,
            self.get_tracks_without_single_detections,
        )

    @cached_property
    def section_provider_event_creation_ui(self) -> SectionProvider:
        return FilterOutCuttingSections(
            MissingEventsSectionProvider(self.section_repository, self.event_repository)
        )

    @cached_property
    def create_intersection_events(self) -> CreateIntersectionEvents:
        return SimpleCreateIntersectionEvents(
            self.intersect, self.section_provider_event_creation_ui, self.add_events
        )

    @property
    @abstractmethod
    def ui_factory(self) -> UiFactory:
        raise NotImplementedError
