from functools import cached_property

from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    FilterOutCuttingSections,
    SectionProvider,
)
from OTAnalytics.application.use_cases.track_repository import AllTrackIdsProvider
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.track import TrackIdProvider
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    provide_available_eventlist_exporter,
)
from OTAnalytics.plugin_ui.base_application import BaseOtAnalyticsApplicationStarter
from OTAnalytics.plugin_ui.cli import (
    OTAnalyticsBulkCli,
    OTAnalyticsCli,
    OTAnalyticsStreamCli,
)


class OtAnalyticsCliApplicationStarter(BaseOtAnalyticsApplicationStarter):
    def start(self) -> None:
        self.application.start()

    @cached_property
    def application(self) -> OTAnalyticsCli:
        if self.run_config.cli_bulk_mode:
            return self.create_bulk_cli()
        return self.create_stream_cli()

    def create_bulk_cli(self) -> OTAnalyticsCli:
        track_parser = self._create_track_parser()
        cli = OTAnalyticsBulkCli(
            self.run_config,
            self.event_repository,
            self.add_section,
            self.get_all_sections,
            self.add_flow,
            self.create_events,
            self.export_counts,
            provide_available_eventlist_exporter,
            self.apply_cli_cuts,
            self.add_all_tracks,
            self.get_all_track_ids,
            self.clear_all_tracks,
            self.tracks_metadata,
            self.videos_metadata,
            self.csv_track_export,
            self.export_road_user_assignments,
            self.export_track_statistics,
            track_parser,
            progressbar=TqdmBuilder(),
        )
        return cli

    def create_stream_cli(self) -> OTAnalyticsCli:
        stream_track_parser = self._create_stream_track_parser()
        cli = OTAnalyticsStreamCli(
            self.run_config,
            self.event_repository,
            self.add_section,
            self.get_all_sections,
            self.add_flow,
            self.create_events,
            self.export_counts,
            self.export_track_statistics,
            provide_available_eventlist_exporter,
            self.apply_cli_cuts,
            self.add_all_tracks,
            self.get_all_track_ids,
            self.clear_all_tracks,
            self.tracks_metadata,
            self.videos_metadata,
            self.csv_track_export,
            self.export_road_user_assignments,
            stream_track_parser,
        )
        return cli

    @cached_property
    def all_filtered_track_ids(self) -> TrackIdProvider:
        return AllTrackIdsProvider(self.track_repository)

    @cached_property
    def create_events(self) -> CreateEvents:
        return self._create_use_case_create_events(
            self.section_provider_event_creation_cli,
            self.clear_all_events,
            self.get_tracks_without_single_detections,
        )

    @cached_property
    def section_provider_event_creation_cli(self) -> SectionProvider:
        return FilterOutCuttingSections(self.section_repository.get_all)

    @cached_property
    def progressbar_builder(self) -> ProgressbarBuilder:
        return TqdmBuilder()
