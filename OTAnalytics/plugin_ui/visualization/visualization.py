from datetime import datetime, timezone
from functools import cached_property
from typing import Callable, Optional, Sequence

from pandas import DataFrame

from OTAnalytics.adapter_visualization.color_provider import ColorPaletteProvider
from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.plotting import (
    CachedPlotter,
    ConstantOffsetFrameNumber,
    GetCurrentFrame,
    GetCurrentVideoPath,
    LayerGroup,
    PlottingLayer,
    TrackBackgroundPlotter,
    VisualizationTimeProvider,
)
from OTAnalytics.application.state import (
    FlowState,
    Plotter,
    SectionState,
    TrackViewState,
    VideosMetadata,
)
from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
    TracksAssignedToGivenFlows,
    TracksIntersectingGivenSections,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
    TracksOverlapOccurrenceWindow,
)
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.application.use_cases.video_repository import GetVideos
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowId, FlowRepository
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackIdProvider
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_prototypes.event_visualization import PandasEventProvider
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    FRAME_OFFSET,
    EventToFlowResolver,
    FilterByClassification,
    FilterByFrame,
    FilterById,
    FilterByOccurrence,
    FilterByVideo,
    FlowLayerPlotter,
    MatplotlibPlotterImplementation,
    MatplotlibTrackPlotter,
    NonLegendTrackGeometryPlotter,
    PandasDataFrameProvider,
    PandasTrackProvider,
    PandasTracksOffsetProvider,
    PlotterPrototype,
    SectionLayerPlotter,
    TrackBoundingBoxPlotter,
    TrackGeometryPlotter,
    TrackPointPlotter,
    TrackStartEndPointPlotter,
)

LONG_IN_THE_PAST = datetime(
    year=1970,
    month=1,
    day=1,
    hour=0,
    minute=0,
    second=0,
    tzinfo=timezone.utc,
)
ALPHA_BOUNDING_BOX = 0.7
LINEWIDTH_BOUNDING_BOX = 1.5
MARKERSIZE_TRACK_POINT = 6
MARKERSIZE_EVENT_FRAME = 12
MARKERSIZE_EVENT_FILTER = 6
MARKER_EVENT_FILTER = "x"
MARKER_EVENT_FRAME = "o"


ALPHA_ALL_TRACKS_PLOTTER = 0.5
ALPHA_HIGHLIGHT_TRACKS = 1
ALPHA_HIGHLIGHT_TRACKS_NOT_ASSIGNED_TO_FLOWS = ALPHA_HIGHLIGHT_TRACKS
ALPHA_HIGHLIGHT_TRACKS_ASSIGNED_TO_FLOWS = ALPHA_HIGHLIGHT_TRACKS
ALPHA_HIGHLIGHT_TRACKS_NOT_INTERSECTING_SECTIONS = ALPHA_HIGHLIGHT_TRACKS
ALPHA_HIGHLIGHT_TRACKS_INTERSECTING_SECTIONS = ALPHA_HIGHLIGHT_TRACKS

ALPHA_HIGHLIGHT_START_END_POINTS = 1
ALPHA_HIGHLIGHT_START_END_POINTS_NOT_ASSIGNED_TO_FLOWS = (
    ALPHA_HIGHLIGHT_START_END_POINTS
)
ALPHA_HIGHLIGHT_START_END_POINTS_ASSIGNED_TO_FLOWS = ALPHA_HIGHLIGHT_START_END_POINTS
ALPHA_HIGHLIGHT_START_END_POINTS_NOT_INTERSECTING_SECTIONS = (
    ALPHA_HIGHLIGHT_START_END_POINTS
)
ALPHA_HIGHLIGHT_START_END_POINTS_INTERSECTING_SECTIONS = (
    ALPHA_HIGHLIGHT_START_END_POINTS
)


ALL: str = "All"
INTERSECTING_SECTIONS: str = "Intersecting sections"
NOT_INTERSECTING_SECTIONS: str = "Not intersecting sections"
ASSIGNED_TO_FLOWS: str = "Assigned to flows"
NOT_ASSIGNED_TO_FLOWS: str = "Not assigned to flows"


class FilterStartDateProvider(VisualizationTimeProvider):
    def __init__(self, state: TrackViewState) -> None:
        self._state = state

    def get_time(self) -> datetime:
        if start_date := self._state.filter_element.get().date_range.start_date:
            return start_date
        return LONG_IN_THE_PAST


class FilterEndDateProvider(VisualizationTimeProvider):
    def __init__(self, state: TrackViewState) -> None:
        self._state = state

    def get_time(self) -> datetime:
        if end_date := self._state.filter_element.get().date_range.end_date:
            return end_date
        return LONG_IN_THE_PAST


class TracksNotAssignedToSelection(PandasDataFrameProvider):
    def __init__(
        self,
        other: PandasDataFrameProvider,
        assigner: RoadUserAssigner,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        state: FlowState,
        track_repository: TrackRepository,
    ) -> None:
        self._other = other
        self._event_repository = event_repository
        self._flow_repository = flow_repository
        self._assigner = assigner
        self._state = state
        self._track_repository = track_repository

    def get_data(self) -> DataFrame:
        return FilterById(
            self._other,
            TracksNotIntersectingSelection(
                TracksAssignedToGivenFlows(
                    self._assigner,
                    self._event_repository,
                    self._flow_repository,
                    self._state.selected_flows.get(),
                ),
                self._track_repository,
            ),
        ).get_data()


def create_track_geometry_plotter(
    pandas_data_provider: PandasDataFrameProvider,
    color_palette_provider: ColorPaletteProvider,
    alpha: float,
    enable_legend: bool,
) -> MatplotlibPlotterImplementation:
    if enable_legend:
        return TrackGeometryPlotter(
            pandas_data_provider,
            color_palette_provider,
            alpha=alpha,
            enable_legend=enable_legend,
        )
    return NonLegendTrackGeometryPlotter(
        pandas_data_provider,
        color_palette_provider,
        alpha=alpha,
    )


class VisualizationBuilder:
    def __init__(
        self,
        datastore: Datastore,
        intersection_repository: IntersectionRepository,
        track_view_state: TrackViewState,
        videos_metadata: VideosMetadata,
        section_state: SectionState,
        color_palette_provider: ColorPaletteProvider,
        pulling_progressbar_builder: ProgressbarBuilder,
        enable_single_legend: bool = True,
        enable_multi_legend: bool = False,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._section_state = section_state
        self._color_palette_provider = color_palette_provider
        self._pulling_progressbar_builder = pulling_progressbar_builder
        self._enable_single_legend = enable_single_legend
        self._enable_multi_legend = enable_multi_legend
        self._track_repository = datastore._track_repository
        self._section_repository = datastore._section_repository
        self._flow_repository = datastore._flow_repository
        self._intersection_repository = intersection_repository
        self._event_repository = datastore._event_repository
        self._visualization_time_provider: VisualizationTimeProvider = (
            FilterEndDateProvider(track_view_state)
        )
        self._get_current_frame = GetCurrentFrame(
            self._visualization_time_provider, videos_metadata
        )
        self._get_current_video = GetCurrentVideoPath(
            self._visualization_time_provider, videos_metadata
        )
        self._get_videos = GetVideos(video_repository=self._datastore._video_repository)
        self._pandas_data_provider: Optional[PandasDataFrameProvider] = None
        self._pandas_event_data_provider: Optional[PandasDataFrameProvider] = None
        self._pandas_data_provider_with_offset: Optional[PandasDataFrameProvider] = None
        self._data_provider_all_filters: Optional[PandasDataFrameProvider] = None
        self._data_provider_all_filters_with_offset: Optional[
            PandasDataFrameProvider
        ] = None
        self._pandas_event_data_provider_all_filters: Optional[
            PandasDataFrameProvider
        ] = None
        self._data_provider_class_filter: Optional[PandasDataFrameProvider] = None
        self._event_data_provider_class_filter: Optional[PandasDataFrameProvider] = None
        self._data_provider_class_filter_with_offset: Optional[
            PandasDataFrameProvider
        ] = None
        self._tracks_intersection_selected_sections: Optional[
            TracksIntersectingSelectedSections
        ] = None
        self._tracks_not_intersecting_selection: Optional[
            TracksNotIntersectingSelection
        ] = None

    def build(
        self,
        flow_state: FlowState,
        road_user_assigner: RoadUserAssigner,
    ) -> tuple[Sequence[LayerGroup], Sequence[PlottingLayer]]:
        highlight_tracks_assigned_to_flows_plotter = (
            self._create_highlight_tracks_assigned_to_flows_plotter(
                flow_state, road_user_assigner
            )
        )
        highlight_tracks_not_assigned_to_flows_plotter = (
            self._create_highlight_tracks_not_assigned_to_flows_plotter(
                road_user_assigner, flow_state
            )
        )

        highlight_start_end_point_assigned_to_flows_plotter = (
            self._create_highlight_start_end_point_assigned_to_flows_plotter(
                flow_state, road_user_assigner
            )
        )
        highlight_start_end_point_not_assigned_to_flows_plotter = (
            self._create_highlight_start_end_point_not_assigned_to_flows_plotter(
                road_user_assigner, flow_state
            )
        )

        track_bounding_box_plotter = self._create_track_bounding_box_plotter()
        track_point_plotter = self._create_track_point_plotter()
        event_point_plotter_frame = self._create_event_point_plotter_frame()
        event_point_plotter_filter = self._create_event_point_plotter_filter()

        layer_definitions: dict[str, list[tuple]] = {
            "Background": [
                ("Background", self.background_plotter, True),
            ],
            "Show tracks": [
                (ALL, self.all_tracks_plotter, False),
                (
                    INTERSECTING_SECTIONS,
                    self._create_highlight_tracks_intersecting_sections_plotter(),
                    False,
                ),
                (
                    NOT_INTERSECTING_SECTIONS,
                    self._create_highlight_tracks_not_intersecting_sections_plotter(),
                    False,
                ),
                (
                    ASSIGNED_TO_FLOWS,
                    highlight_tracks_assigned_to_flows_plotter,
                    False,
                ),
                (
                    NOT_ASSIGNED_TO_FLOWS,
                    highlight_tracks_not_assigned_to_flows_plotter,
                    False,
                ),
            ],
            "Show start and end points": [
                (
                    ALL,
                    self.start_end_point_plotter,
                    False,
                ),
                (
                    INTERSECTING_SECTIONS,
                    self._create_start_end_point_intersecting_sections_plotter(),
                    False,
                ),
                (
                    NOT_INTERSECTING_SECTIONS,
                    self._create_start_end_point_not_intersection_sections_plotter(),
                    False,
                ),
                (
                    ASSIGNED_TO_FLOWS,
                    highlight_start_end_point_assigned_to_flows_plotter,
                    False,
                ),
                (
                    NOT_ASSIGNED_TO_FLOWS,
                    highlight_start_end_point_not_assigned_to_flows_plotter,
                    False,
                ),
            ],
            "Show detections of current frame": [
                (
                    "Bounding Box",
                    track_bounding_box_plotter,
                    False,
                ),
                (
                    "Track point",
                    track_point_plotter,
                    False,
                ),
            ],
            "Show events": [
                (
                    "Current filter",
                    event_point_plotter_filter,
                    False,
                ),
                (
                    "Current frame",
                    event_point_plotter_frame,
                    False,
                ),
            ],
        }

        plotting_layers = []
        grouped_layers = []

        for group, definition in layer_definitions.items():
            layers = [
                PlottingLayer(name, plotter, enabled)
                for name, plotter, enabled in definition
            ]
            layer_group = LayerGroup(name=group, layers=layers)
            grouped_layers.append(layer_group)
            plotting_layers.extend(layers)
        return grouped_layers, plotting_layers

    @cached_property
    def background_plotter(self) -> Plotter:
        return TrackBackgroundPlotter(
            self._track_view_state.selected_videos.get,
            self._visualization_time_provider,
        )

    @cached_property
    def all_tracks_plotter(self) -> Plotter:
        track_geometry_plotter = self._create_track_geometry_plotter(
            self._get_data_provider_all_filters_with_offset(),
            self._color_palette_provider,
            alpha=ALPHA_ALL_TRACKS_PLOTTER,
            enable_legend=self._enable_single_legend,
        )
        all_tracks_plotter = self._wrap_plotter_with_cache(track_geometry_plotter)
        return all_tracks_plotter

    def _create_highlight_tracks_intersecting_sections_plotter(self) -> Plotter:
        return self._create_cached_section_layer_plotter(
            self._create_highlight_tracks_intersecting_section_factory(
                self._get_tracks_intersecting_sections_filter(),
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_TRACKS_INTERSECTING_SECTIONS,
                enable_legend=self._enable_multi_legend,
            ),
            self._section_state,
        )

    def _create_highlight_tracks_not_intersecting_sections_plotter(self) -> Plotter:
        return self._create_cached_section_layer_plotter(
            self._create_highlight_tracks_intersecting_section_factory(
                self._get_tracks_not_intersecting_selected_sections_filter(),
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_TRACKS_NOT_INTERSECTING_SECTIONS,
                enable_legend=self._enable_multi_legend,
            ),
            self._section_state,
        )

    def _create_start_end_point_intersecting_sections_plotter(self) -> Plotter:
        start_end_points_intersecting = self._create_cached_section_layer_plotter(
            self._create_start_end_point_intersecting_section_factory(
                self._create_tracks_start_end_point_intersecting_given_sections_filter(
                    self._get_data_provider_class_filter_with_offset(),
                    self._create_tracks_intersecting_sections(),
                    self._create_get_sections_by_id(),
                ),
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_START_END_POINTS_INTERSECTING_SECTIONS,
                enable_legend=self._enable_multi_legend,
            ),
            self._section_state,
        )
        return start_end_points_intersecting

    def _create_start_end_point_not_intersection_sections_plotter(self) -> Plotter:
        section_filter = (
            self._create_tracks_start_end_point_not_intersecting_given_sections_filter(
                self._get_data_provider_class_filter_with_offset(),
                self._create_tracks_intersecting_sections(),
                self._create_get_sections_by_id(),
            )
        )
        return self._create_cached_section_layer_plotter(
            self._create_start_end_point_intersecting_section_factory(
                section_filter,
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_START_END_POINTS_NOT_INTERSECTING_SECTIONS,
                enable_legend=self._enable_multi_legend,
            ),
            self._section_state,
        )

    def _create_highlight_start_end_point_assigned_to_flows_factory(
        self,
        pandas_data_provider_factory: Callable[[FlowId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Callable[[FlowId], Plotter]:
        return lambda flow: self._create_track_start_end_point_plotter(
            pandas_data_provider_factory(flow),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_highlight_start_end_point_assigned_to_flow(
        self,
        plotter_factory: Callable[[FlowId], Plotter],
        flow_state: FlowState,
    ) -> Plotter:
        plotter = FlowLayerPlotter(
            plotter_factory,
            flow_state,
            self._flow_repository,
            self._track_repository,
            self._event_repository,
            EventToFlowResolver(self._flow_repository),
        )
        self._track_view_state.filter_element.register(plotter.notify_invalidate)
        self._track_view_state.track_offset.register(plotter.notify_invalidate)
        return plotter

    def _create_highlight_start_end_point_assigned_to_flows_plotter(
        self, flow_state: FlowState, road_user_assigner: RoadUserAssigner
    ) -> Plotter:
        return self._create_highlight_start_end_point_assigned_to_flow(
            self._create_highlight_start_end_point_assigned_to_flows_factory(
                self._create_tracks_assigned_to_flows_filter(
                    self._get_data_provider_all_filters_with_offset(),
                    road_user_assigner,
                ),
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_START_END_POINTS_ASSIGNED_TO_FLOWS,
                enable_legend=self._enable_multi_legend,
            ),
            flow_state,
        )

    def _create_highlight_start_end_point_not_assigned_to_flows_plotter(
        self, road_user_assigner: RoadUserAssigner, flow_state: FlowState
    ) -> Plotter:
        flows_filter = TracksNotAssignedToSelection(
            self._get_data_provider_all_filters_with_offset(),
            road_user_assigner,
            self._event_repository,
            self._flow_repository,
            flow_state,
            self._track_repository,
        )
        cached_plotter = CachedPlotter(
            self._create_track_start_end_point_plotter(
                flows_filter,
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_START_END_POINTS_NOT_ASSIGNED_TO_FLOWS,
                enable_legend=self._enable_multi_legend,
            ),
            [],
        )
        invalidate = cached_plotter.invalidate_cache
        self._event_repository.register_observer(invalidate)
        flow_state.selected_flows.register(invalidate)
        self._track_view_state.filter_element.register(invalidate)
        self._track_view_state.track_offset.register(invalidate)
        return cached_plotter

    @cached_property
    def start_end_point_plotter(self) -> Plotter:
        track_start_end_point_plotter = self._create_track_start_end_point_plotter(
            self._create_track_start_end_point_data_provider(
                self._get_data_provider_class_filter_with_offset()
            ),
            self._color_palette_provider,
            alpha=ALPHA_HIGHLIGHT_START_END_POINTS,
            enable_legend=self._enable_multi_legend,
        )
        start_end_point_plotter = self._wrap_plotter_with_cache(
            track_start_end_point_plotter
        )
        return start_end_point_plotter

    def _create_highlight_tracks_assigned_to_flows_plotter(
        self, flow_state: FlowState, road_user_assigner: RoadUserAssigner
    ) -> Plotter:
        return self._create_highlight_tracks_assigned_to_flow(
            self._create_highlight_tracks_assigned_to_flows_factory(
                self._create_tracks_assigned_to_flows_filter(
                    self._get_data_provider_all_filters_with_offset(),
                    road_user_assigner,
                ),
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_TRACKS_ASSIGNED_TO_FLOWS,
                enable_legend=self._enable_multi_legend,
            ),
            flow_state,
        )

    def _create_highlight_tracks_not_assigned_to_flows_plotter(
        self, road_user_assigner: RoadUserAssigner, flow_state: FlowState
    ) -> Plotter:
        flows_filter = TracksNotAssignedToSelection(
            self._get_data_provider_all_filters_with_offset(),
            road_user_assigner,
            self._event_repository,
            self._flow_repository,
            flow_state,
            self._track_repository,
        )
        cached_plotter = CachedPlotter(
            self._create_track_geometry_plotter(
                flows_filter,
                self._color_palette_provider,
                alpha=ALPHA_HIGHLIGHT_TRACKS_NOT_ASSIGNED_TO_FLOWS,
                enable_legend=self._enable_multi_legend,
            ),
            [],
        )
        invalidate = cached_plotter.invalidate_cache
        self._event_repository.register_observer(invalidate)
        flow_state.selected_flows.register(invalidate)
        self._track_view_state.filter_element.register(invalidate)
        self._track_view_state.track_offset.register(invalidate)
        return cached_plotter

    def _get_event_data_provider_class_filter(self) -> PandasDataFrameProvider:
        if not self._event_data_provider_class_filter:
            self._event_data_provider_class_filter = (
                self._build_filter_by_classification(
                    self._get_pandas_event_data_provider()
                )
            )
        return self._event_data_provider_class_filter

    def _get_event_data_provider_all_filters(self) -> PandasDataFrameProvider:
        if not self._pandas_event_data_provider_all_filters:
            self._pandas_event_data_provider_all_filters = self._create_all_filters(
                self._get_pandas_event_data_provider()
            )
        return self._pandas_event_data_provider_all_filters

    def _get_data_provider_class_filter(self) -> PandasDataFrameProvider:
        if not self._data_provider_class_filter:
            self._data_provider_class_filter = self._build_filter_by_classification(
                self._get_pandas_data_provider()
            )
        return self._data_provider_class_filter

    def _get_data_provider_class_filter_with_offset(self) -> PandasDataFrameProvider:
        if not self._data_provider_class_filter_with_offset:
            self._data_provider_class_filter_with_offset = (
                self._build_filter_by_classification(
                    self._get_pandas_data_provider_with_offset()
                )
            )
        return self._data_provider_class_filter_with_offset

    def _get_data_provider_all_filters(self) -> PandasDataFrameProvider:
        if not self._data_provider_all_filters:
            self._data_provider_all_filters = self._create_all_filters(
                self._get_pandas_data_provider()
            )
        return self._data_provider_all_filters

    def _get_data_provider_all_filters_with_offset(self) -> PandasDataFrameProvider:
        if not self._data_provider_all_filters_with_offset:
            self._data_provider_all_filters_with_offset = self._create_all_filters(
                self._get_pandas_data_provider_with_offset()
            )
        return self._data_provider_all_filters_with_offset

    def _create_all_filters(
        self, data_provider: PandasDataFrameProvider
    ) -> PandasDataFrameProvider:
        return self._build_filter_by_classification(
            self._create_filter_by_occurrence(data_provider)
        )

    def _create_filter_by_occurrence(
        self, data_provider: PandasDataFrameProvider
    ) -> PandasDataFrameProvider:
        return FilterByOccurrence(
            data_provider,
            self._track_view_state,
            self._create_dataframe_filter_builder(),
        )

    def _create_get_sections_by_id(self) -> GetSectionsById:
        return GetSectionsById(self._section_repository)

    def _get_tracks_not_intersecting_selected_sections_filter(
        self,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            self._get_data_provider_all_filters_with_offset(),
            TracksNotIntersectingSelection(
                TracksIntersectingGivenSections(
                    {section},
                    self._create_tracks_intersecting_sections(),
                    self._create_get_sections_by_id(),
                    self._intersection_repository,
                ),
                self._track_repository,
            ),
        )

    def _build_filter_by_classification(
        self, data_provider: PandasDataFrameProvider
    ) -> PandasDataFrameProvider:
        return FilterByClassification(
            data_provider,
            self._track_view_state,
            self._create_dataframe_filter_builder(),
        )

    def _get_pandas_data_provider_with_offset(self) -> PandasDataFrameProvider:
        if not self._pandas_data_provider_with_offset:
            self._pandas_data_provider_with_offset = (
                self._wrap_pandas_track_offset_provider(
                    self._get_pandas_data_provider()
                )
            )
        return self._pandas_data_provider_with_offset

    def _wrap_plotter_with_cache(self, other: Plotter) -> Plotter:
        """
        Create a caching plotter that invalidates the cache on track repository changes.
        """
        cached_plotter: CachedPlotter = CachedPlotter(other, subjects=[])
        invalidate = cached_plotter.invalidate_cache
        self._track_repository.observers.register(invalidate)
        self._track_view_state.filter_element.register(invalidate)
        self._track_view_state.track_offset.register(invalidate)
        return cached_plotter

    def _get_pandas_data_provider(self) -> PandasDataFrameProvider:
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        if not self._pandas_data_provider:
            self._pandas_data_provider = PandasTrackProvider(
                self._track_repository,
                dataframe_filter_builder,
                self._pulling_progressbar_builder,
            )
        return self._pandas_data_provider

    def _get_pandas_event_data_provider(self) -> PandasDataFrameProvider:
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        if not self._pandas_event_data_provider:
            self._pandas_event_data_provider = PandasEventProvider(
                self._event_repository,
                dataframe_filter_builder,
                self._pulling_progressbar_builder,
            )
        return self._pandas_event_data_provider

    def _wrap_pandas_track_offset_provider(
        self, other: PandasDataFrameProvider
    ) -> PandasDataFrameProvider:
        return PandasTracksOffsetProvider(other, self._track_view_state)

    def _create_track_geometry_plotter(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            create_track_geometry_plotter(
                pandas_data_provider, color_palette_provider, alpha, enable_legend
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)

    def _create_track_start_end_point_data_provider(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        id_filter: Optional[TrackIdProvider] = None,
    ) -> FilterById:
        return FilterById(
            pandas_data_provider,
            id_filter=TracksOverlapOccurrenceWindow(
                other=id_filter,
                track_repository=self._track_repository,
                track_view_state=self._track_view_state,
            ),
        )

    def _create_track_start_end_point_plotter(
        self,
        data_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(
                data_provider,
                color_palette_provider,
                enable_legend=enable_legend,
                alpha=alpha,
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)

    def _get_tracks_intersecting_sections_filter(
        self,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            self._get_data_provider_all_filters_with_offset(),
            TracksIntersectingGivenSections(
                {section},
                self._create_tracks_intersecting_sections(),
                self._create_get_sections_by_id(),
                self._intersection_repository,
            ),
        )

    def _create_highlight_tracks_intersecting_section_factory(
        self,
        pandas_data_provider_factory: Callable[[SectionId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Callable[[SectionId], Plotter]:
        return lambda section: self._create_track_geometry_plotter(
            pandas_data_provider_factory(section),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_cached_section_layer_plotter(
        self,
        plotter_factory: Callable[[SectionId], Plotter],
        section_state: SectionState,
    ) -> Plotter:
        plotter = SectionLayerPlotter(
            plotter_factory,
            section_state,
            self._section_repository,
            self._track_repository,
        )

        self._track_view_state.filter_element.register(plotter.notify_invalidate)
        self._track_view_state.track_offset.register(plotter.notify_invalidate)
        return plotter

    def _create_tracks_start_end_point_intersecting_given_sections_filter(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            pandas_data_provider,
            id_filter=TracksOverlapOccurrenceWindow(
                other=TracksIntersectingGivenSections(
                    {section},
                    tracks_intersecting_sections,
                    get_sections_by_id,
                    self._intersection_repository,
                ),
                track_repository=self._track_repository,
                track_view_state=self._track_view_state,
            ),
        )

    def _create_start_end_point_intersecting_section_factory(
        self,
        pandas_data_provider_factory: Callable[[SectionId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Callable[[SectionId], Plotter]:
        return lambda section: self._create_track_start_end_point_plotter(
            pandas_data_provider_factory(section),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_start_end_point_tracks_not_intersecting_sections_plotter(
        self,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Plotter:
        return self._create_track_start_end_point_plotter(
            self._create_track_start_end_point_data_provider(
                pandas_track_provider, tracks_not_intersecting_sections
            ),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_tracks_start_end_point_not_intersecting_given_sections_filter(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            pandas_data_provider,
            id_filter=TracksOverlapOccurrenceWindow(
                other=TracksNotIntersectingSelection(
                    TracksIntersectingGivenSections(
                        {section},
                        tracks_intersecting_sections,
                        get_sections_by_id,
                        self._intersection_repository,
                    ),
                    self._track_repository,
                ),
                track_repository=self._track_repository,
                track_view_state=self._track_view_state,
            ),
        )

    def _create_tracks_assigned_to_flows_filter(
        self, pandas_data_provider: PandasDataFrameProvider, assigner: RoadUserAssigner
    ) -> Callable[[FlowId], PandasDataFrameProvider]:
        return lambda flow: FilterById(
            pandas_data_provider,
            TracksAssignedToGivenFlows(
                assigner,
                self._event_repository,
                self._flow_repository,
                [flow],
            ),
        )

    def _create_highlight_tracks_assigned_to_flows_factory(
        self,
        pandas_data_provider_factory: Callable[[FlowId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Callable[[FlowId], Plotter]:
        return lambda flow: self._create_track_geometry_plotter(
            pandas_data_provider_factory(flow),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_highlight_tracks_assigned_to_flow(
        self,
        plotter_factory: Callable[[FlowId], Plotter],
        flow_state: FlowState,
    ) -> Plotter:
        plotter = FlowLayerPlotter(
            plotter_factory,
            flow_state,
            self._flow_repository,
            self._track_repository,
            self._event_repository,
            EventToFlowResolver(self._flow_repository),
        )
        self._track_view_state.filter_element.register(plotter.notify_invalidate)
        self._track_view_state.track_offset.register(plotter.notify_invalidate)
        return plotter

    def _create_tracks_not_assigned_to_flows_filter(
        self, pandas_data_provider: PandasDataFrameProvider, assigner: RoadUserAssigner
    ) -> Callable[[FlowId], PandasDataFrameProvider]:
        return lambda flow: FilterById(
            pandas_data_provider,
            TracksNotIntersectingSelection(
                TracksAssignedToGivenFlows(
                    assigner,
                    self._event_repository,
                    self._flow_repository,
                    [flow],
                ),
                self._track_repository,
            ),
        )

    def _create_dataframe_filter_builder(self) -> DataFrameFilterBuilder:
        return DataFrameFilterBuilder(
            current_frame=self._get_current_frame, get_videos=self._get_videos
        )

    # TODO duplicate to main_application.py
    def _create_tracks_intersecting_sections(self) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(
            GetAllTracks(self._track_repository),
        )

    def _create_track_bounding_box_plotter(
        self,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackBoundingBoxPlotter(
                FilterByFrame(
                    FilterByVideo(
                        self._get_data_provider_class_filter(),
                        self._get_current_video,
                    ),
                    ConstantOffsetFrameNumber(self._get_current_frame, FRAME_OFFSET),
                ),
                self._color_palette_provider,
                self._track_view_state,
                alpha=ALPHA_BOUNDING_BOX,
                linewidth=LINEWIDTH_BOUNDING_BOX,
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)

    def _create_track_point_plotter(self) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackPointPlotter(
                FilterByFrame(
                    FilterByVideo(
                        self._get_data_provider_class_filter_with_offset(),
                        self._get_current_video,
                    ),
                    ConstantOffsetFrameNumber(self._get_current_frame, FRAME_OFFSET),
                ),
                self._color_palette_provider,
                alpha=ALPHA_BOUNDING_BOX,
                markersize=MARKERSIZE_TRACK_POINT,
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)

    def _create_event_point_plotter_frame(self) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackPointPlotter(
                FilterByFrame(
                    FilterByVideo(
                        self._get_event_data_provider_class_filter(),
                        self._get_current_video,
                    ),
                    ConstantOffsetFrameNumber(self._get_current_frame, FRAME_OFFSET),
                ),
                self._color_palette_provider,
                alpha=ALPHA_BOUNDING_BOX,
                marker=MARKER_EVENT_FRAME,
                markersize=MARKERSIZE_EVENT_FRAME,
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)

    def _create_event_point_plotter_filter(self) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackPointPlotter(
                self._get_event_data_provider_all_filters(),
                self._color_palette_provider,
                alpha=ALPHA_BOUNDING_BOX,
                marker=MARKER_EVENT_FILTER,
                markersize=MARKERSIZE_EVENT_FILTER,
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)
