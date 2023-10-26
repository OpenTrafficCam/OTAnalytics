from typing import Callable, Optional, Sequence

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.plotting import CachedPlotter, PlottingLayer
from OTAnalytics.application.state import (
    FlowState,
    Plotter,
    SectionState,
    TrackViewState,
)
from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToGivenFlows,
    TracksAssignedToSelectedFlows,
    TracksIntersectingGivenSections,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
    TracksOverlapOccurrenceWindow,
)
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.application.use_cases.track_repository import (
    GetTracksWithoutSingleDetections,
)
from OTAnalytics.domain.flow import FlowId
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import SectionId, SectionRepository
from OTAnalytics.domain.track import TrackIdProvider
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    ColorPaletteProvider,
    FilterByClassification,
    FilterById,
    FilterByOccurrence,
    FlowLayerPlotter,
    FlowListObserverWrapper,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTrackProvider,
    PandasTracksOffsetProvider,
    PlotterPrototype,
    SectionLayerPlotter,
    SectionListObserverWrapper,
    TrackBackgroundPlotter,
    TrackGeometryPlotter,
    TrackStartEndPointPlotter,
)


class VisualizationBuilder:
    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._track_repository = datastore._track_repository
        self._section_repository = datastore._section_repository
        self._flow_repository = datastore._flow_repository
        self._event_repository = datastore._event_repository

    def build(
        self,
        flow_state: FlowState,
        section_state: SectionState,
        pulling_progressbar_builder: ProgressbarBuilder,
        road_user_assigner: RoadUserAssigner,
        color_palette_provider: ColorPaletteProvider,
    ) -> Sequence[PlottingLayer]:
        background_image_plotter = TrackBackgroundPlotter(self._datastore)
        pandas_data_provider = self._build_pandas_data_provider(
            pulling_progressbar_builder
        )
        occurrence_data_provider = FilterByOccurrence(
            pandas_data_provider,
            self._track_view_state,
            self._create_dataframe_filter_builder(),
        )
        data_provider_all_filters = self._build_filter_by_classification(
            occurrence_data_provider
        )
        data_provider_class_filter = self._build_filter_by_classification(
            pandas_data_provider
        )
        track_geometry_plotter = self._create_track_geometry_plotter(
            data_provider_all_filters,
            color_palette_provider,
            alpha=0.5,
            enable_legend=True,
        )

        tracks_intersecting_sections = self._create_tracks_intersecting_sections()
        tracks_intersecting_selected_sections = (
            self._create_tracks_intersecting_selected_sections(
                section_state,
                tracks_intersecting_sections,
                self._section_repository,
            )
        )
        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_selected_sections, self._track_repository
        )

        get_sections_by_id = GetSectionsById(self._section_repository)
        tracks_intersecting_sections_filter = (
            self._create_tracks_intersecting_sections_filter(
                data_provider_all_filters,
                tracks_intersecting_sections,
                get_sections_by_id,
            )
        )

        highlight_tracks_intersecting_sections = (
            self._create_cached_section_layer_plotter(
                self._create_highlight_tracks_intersecting_section_factory(
                    tracks_intersecting_sections_filter,
                    color_palette_provider,
                    alpha=1,
                    enable_legend=False,
                ),
                section_state,
            )
        )
        highlight_tracks_not_intersecting_sections = (
            self._create_track_highlight_geometry_plotter_not_intersecting(
                tracks_not_intersecting_sections,
                data_provider_all_filters,
                color_palette_provider,
                enable_legend=False,
            )
        )
        start_end_points_intersecting = self._create_cached_section_layer_plotter(
            self._create_start_end_point_intersecting_section_factory(
                self._create_tracks_start_end_point_intersecting_given_sections_filter(
                    data_provider_class_filter,
                    tracks_intersecting_sections,
                    get_sections_by_id,
                ),
                color_palette_provider,
                enable_legend=False,
            ),
            section_state,
        )

        start_end_points_tracks_not_intersecting_sections = (
            self._create_start_end_point_tracks_not_intersecting_sections_plotter(
                tracks_not_intersecting_sections,
                data_provider_class_filter,
                color_palette_provider,
                enable_legend=False,
            )
        )
        track_start_end_point_plotter = self._create_track_start_end_point_plotter(
            self._create_track_start_end_point_data_provider(
                data_provider_class_filter
            ),
            color_palette_provider,
            enable_legend=False,
        )
        tracks_assigned_to_flow = TracksAssignedToSelectedFlows(
            road_user_assigner,
            self._event_repository,
            self._flow_repository,
            flow_state,
        )

        highlight_tracks_assigned_to_flow = (
            self._create_highlight_tracks_assigned_to_flow(
                self._create_highlight_tracks_assigned_to_flows_factory(
                    self._create_tracks_assigned_to_flows_filter(
                        data_provider_all_filters, road_user_assigner
                    ),
                    color_palette_provider,
                    alpha=1,
                    enable_legend=False,
                ),
                flow_state,
            )
        )
        highlight_tracks_not_assigned_to_flow = (
            self._create_highlight_tracks_not_assigned_to_flow(
                data_provider_all_filters,
                color_palette_provider,
                tracks_assigned_to_flow,
                enable_legend=False,
            )
        )
        background = PlottingLayer("Background", background_image_plotter, enabled=True)
        all_tracks_layer = PlottingLayer(
            "Show all tracks",
            self._wrap_plotter_with_cache(
                track_geometry_plotter,
                tracks=True,
                sections=False,
                flows=False,
                events=False,
            ),
            enabled=False,
        )
        highlight_tracks_intersecting_sections_layer = PlottingLayer(
            "Highlight tracks intersecting sections",
            highlight_tracks_intersecting_sections,
            enabled=False,
        )
        highlight_tracks_not_intersecting_sections_layer = PlottingLayer(
            "Highlight tracks not intersecting sections",
            self._wrap_plotter_with_cache(
                highlight_tracks_not_intersecting_sections,
                tracks=True,
                sections=True,
                flows=False,
                events=False,
            ),
            enabled=False,
        )
        start_end_points_tracks_intersecting_sections_layer = PlottingLayer(
            "Show start and end point of tracks intersecting sections",
            start_end_points_intersecting,
            enabled=False,
        )
        start_end_points_tracks_not_intersecting_sections_layer = PlottingLayer(
            "Show start and end point of tracks not intersecting sections",
            self._wrap_plotter_with_cache(
                start_end_points_tracks_not_intersecting_sections,
                tracks=True,
                sections=True,
                flows=False,
                events=False,
            ),
            enabled=False,
        )
        start_end_point_layer = PlottingLayer(
            "Show start and end point",
            self._wrap_plotter_with_cache(
                track_start_end_point_plotter,
                tracks=True,
                sections=True,
                flows=False,
                events=False,
            ),
            enabled=False,
        )
        highlight_tracks_assigned_to_flow_layer = PlottingLayer(
            "Highlight tracks assigned to flow",
            highlight_tracks_assigned_to_flow,
            enabled=False,
        )
        highlight_tracks_not_assigned_to_flow_layer = PlottingLayer(
            "Highlight tracks not assigned to flow",
            self._wrap_plotter_with_cache(
                highlight_tracks_not_assigned_to_flow,
                tracks=True,
                sections=True,
                flows=True,
                events=True,
            ),
            enabled=False,
        )

        return [
            background,
            all_tracks_layer,
            highlight_tracks_intersecting_sections_layer,
            highlight_tracks_not_intersecting_sections_layer,
            start_end_point_layer,
            start_end_points_tracks_intersecting_sections_layer,
            start_end_points_tracks_not_intersecting_sections_layer,
            highlight_tracks_assigned_to_flow_layer,
            highlight_tracks_not_assigned_to_flow_layer,
        ]

    def _build_filter_by_classification(
        self, data_provider: PandasDataFrameProvider
    ) -> PandasDataFrameProvider:
        return FilterByClassification(
            data_provider,
            self._track_view_state,
            self._create_dataframe_filter_builder(),
        )

    def _build_pandas_data_provider(
        self, pulling_progressbar_builder: ProgressbarBuilder
    ) -> PandasDataFrameProvider:
        cached_pandas_track_provider = self._create_pandas_track_provider(
            pulling_progressbar_builder
        )
        pandas_data_provider = self._wrap_pandas_track_offset_provider(
            cached_pandas_track_provider
        )
        return pandas_data_provider

    def _wrap_plotter_with_cache(
        self, other: Plotter, tracks: bool, sections: bool, flows: bool, events: bool
    ) -> Plotter:
        cached_plotter: CachedPlotter = CachedPlotter(other, subjects=[])
        invalidate = cached_plotter.invalidate_cache

        if tracks:
            self._track_repository.observers.register(invalidate)

        if sections:
            self._section_repository.register_sections_observer(
                SectionListObserverWrapper(invalidate)
            )
            self._section_repository._section_content_observers.register(invalidate)

        if flows:
            self._flow_repository.register_flows_observer(
                FlowListObserverWrapper(invalidate)
            )
            self._flow_repository._flow_content_observers.register(invalidate)

        # if events:
        #     event_repository = datastore._event_repository
        #     event_repository.register_observer(invalidate)

        return cached_plotter

    def _create_pandas_track_provider(
        self, progressbar: ProgressbarBuilder
    ) -> PandasTrackProvider:
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        # return PandasTrackProvider(
        #     datastore, self._track_view_state, dataframe_filter_builder, progressbar
        # )
        return CachedPandasTrackProvider(
            self._track_repository,
            self._track_view_state,
            dataframe_filter_builder,
            progressbar,
        )

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
            TrackGeometryPlotter(
                pandas_data_provider,
                color_palette_provider,
                alpha=alpha,
                enable_legend=enable_legend,
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
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(
                data_provider,
                color_palette_provider,
                enable_legend=enable_legend,
            ),
        )
        return PlotterPrototype(self._track_view_state, track_plotter)

    def _create_tracks_intersecting_selected_sections(
        self,
        section_state: SectionState,
        tracks_intersecting_sections: TracksIntersectingSections,
        section_repository: SectionRepository,
    ) -> TracksIntersectingSelectedSections:
        return TracksIntersectingSelectedSections(
            section_state,
            tracks_intersecting_sections,
            GetSectionsById(section_repository),
        )

    def _create_tracks_intersecting_sections_filter(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            pandas_data_provider,
            TracksIntersectingGivenSections(
                [section], tracks_intersecting_sections, get_sections_by_id
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
        return SectionLayerPlotter(
            plotter_factory,
            section_state,
            self._section_repository,
            self._track_repository,
        )

    def _create_track_highlight_geometry_plotter_not_intersecting(
        self,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_not_intersecting_sections
        )
        return self._create_track_geometry_plotter(
            filter_by_id, color_palette_provider, alpha=1, enable_legend=enable_legend
        )

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
                    [section],
                    tracks_intersecting_sections,
                    get_sections_by_id,
                ),
                track_repository=self._track_repository,
                track_view_state=self._track_view_state,
            ),
        )

    def _create_start_end_point_intersecting_section_factory(
        self,
        pandas_data_provider_factory: Callable[[SectionId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Callable[[SectionId], Plotter]:
        return lambda section: self._create_track_start_end_point_plotter(
            pandas_data_provider_factory(section), color_palette_provider, enable_legend
        )

    def _create_start_end_point_tracks_not_intersecting_sections_plotter(
        self,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        return self._create_track_start_end_point_plotter(
            self._create_track_start_end_point_data_provider(
                pandas_track_provider, tracks_not_intersecting_sections
            ),
            color_palette_provider,
            enable_legend,
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
        return FlowLayerPlotter(
            plotter_factory, flow_state, self._flow_repository, self._track_repository
        )

    def _create_highlight_tracks_not_assigned_to_flow(
        self,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        tracks_assigned_to_flow: TracksAssignedToSelectedFlows,
        enable_legend: bool,
    ) -> Plotter:
        tracks_not_assigned_to_flow = TracksNotIntersectingSelection(
            tracks_assigned_to_flow, self._track_repository
        )
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_not_assigned_to_flow
        )
        return self._create_track_geometry_plotter(
            filter_by_id, color_palette_provider, alpha=1, enable_legend=enable_legend
        )

    def _create_dataframe_filter_builder(self) -> DataFrameFilterBuilder:
        return DataFrameFilterBuilder()

    # TODO duplicate to main_application.py
    def _create_tracks_intersecting_sections(self) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(
            GetTracksWithoutSingleDetections(self._track_repository),
            ShapelyIntersector(),
        )
