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
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackIdProvider
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    ColorPaletteProvider,
    EventToFlowResolver,
    FilterByClassification,
    FilterById,
    FilterByOccurrence,
    FlowLayerPlotter,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTrackProvider,
    PandasTracksOffsetProvider,
    PlotterPrototype,
    SectionLayerPlotter,
    TrackBackgroundPlotter,
    TrackGeometryPlotter,
    TrackStartEndPointPlotter,
)


class VisualizationBuilder:
    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        section_state: SectionState,
        color_palette_provider: ColorPaletteProvider,
        pulling_progressbar_builder: ProgressbarBuilder,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._section_state = section_state
        self._color_palette_provider = color_palette_provider
        self._pulling_progressbar_builder = pulling_progressbar_builder
        self._track_repository = datastore._track_repository
        self._section_repository = datastore._section_repository
        self._flow_repository = datastore._flow_repository
        self._event_repository = datastore._event_repository
        self._pandas_data_provider: Optional[PandasDataFrameProvider] = None
        self._data_provider_all_filters: Optional[PandasDataFrameProvider] = None
        self._data_provider_class_filter: Optional[PandasDataFrameProvider] = None
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
    ) -> Sequence[PlottingLayer]:
        background_image_plotter = TrackBackgroundPlotter(self._datastore)
        all_tracks_plotter = self._create_all_tracks_plotter()
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
        layer_definitions = [
            ("Background", background_image_plotter, True),
            ("Show all tracks", all_tracks_plotter, False),
            (
                "Highlight tracks intersecting sections",
                self._create_highlight_tracks_intersecting_sections_plotter(),
                False,
            ),
            (
                "Highlight tracks not intersecting sections",
                self._create_highlight_tracks_not_intersecting_sections_plotter(),
                False,
            ),
            (
                "Show start and end point of tracks intersecting sections",
                self._create_start_end_point_intersecting_sections_plotter(),
                False,
            ),
            (
                "Show start and end point of tracks not intersecting sections",
                self._create_start_end_point_not_intersection_sections_plotter(),
                False,
            ),
            (
                "Show start and end point",
                self._create_start_end_point_plotter(),
                False,
            ),
            (
                "Highlight tracks assigned to flows",
                highlight_tracks_assigned_to_flows_plotter,
                False,
            ),
            (
                "Highlight tracks not assigned to flows",
                highlight_tracks_not_assigned_to_flows_plotter,
                False,
            ),
        ]

        return [
            PlottingLayer(name, plotter, enabled)
            for name, plotter, enabled in layer_definitions
        ]

    def _create_all_tracks_plotter(self) -> Plotter:
        track_geometry_plotter = self._create_track_geometry_plotter(
            self._get_data_provider_all_filters(),
            self._color_palette_provider,
            alpha=0.5,
            enable_legend=True,
        )
        all_tracks_plotter = self._wrap_plotter_with_cache(track_geometry_plotter)
        return all_tracks_plotter

    def _create_highlight_tracks_intersecting_sections_plotter(self) -> Plotter:
        return self._create_cached_section_layer_plotter(
            self._create_highlight_tracks_intersecting_section_factory(
                self._get_tracks_intersecting_sections_filter(),
                self._color_palette_provider,
                alpha=1,
                enable_legend=False,
            ),
            self._section_state,
        )

    def _create_highlight_tracks_not_intersecting_sections_plotter(self) -> Plotter:
        return self._create_cached_section_layer_plotter(
            self._create_highlight_tracks_intersecting_section_factory(
                self._get_tracks_not_intersecting_selected_sections_filter(),
                self._color_palette_provider,
                alpha=1,
                enable_legend=False,
            ),
            self._section_state,
        )

    def _create_start_end_point_intersecting_sections_plotter(self) -> Plotter:
        start_end_points_intersecting = self._create_cached_section_layer_plotter(
            self._create_start_end_point_intersecting_section_factory(
                self._create_tracks_start_end_point_intersecting_given_sections_filter(
                    self._get_data_provider_class_filter(),
                    self._create_tracks_intersecting_sections(),
                    self._create_get_sections_by_id(),
                ),
                self._color_palette_provider,
                enable_legend=False,
            ),
            self._section_state,
        )
        return start_end_points_intersecting

    def _create_start_end_point_not_intersection_sections_plotter(self) -> Plotter:
        section_filter = (
            self._create_tracks_start_end_point_not_intersecting_given_sections_filter(
                self._get_data_provider_class_filter(),
                self._create_tracks_intersecting_sections(),
                self._create_get_sections_by_id(),
            )
        )
        return self._create_cached_section_layer_plotter(
            self._create_start_end_point_intersecting_section_factory(
                section_filter,
                self._color_palette_provider,
                enable_legend=False,
            ),
            self._section_state,
        )

    def _create_start_end_point_plotter(self) -> Plotter:
        track_start_end_point_plotter = self._create_track_start_end_point_plotter(
            self._create_track_start_end_point_data_provider(
                self._get_data_provider_class_filter()
            ),
            self._color_palette_provider,
            enable_legend=False,
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
                    self._get_data_provider_all_filters(), road_user_assigner
                ),
                self._color_palette_provider,
                alpha=1,
                enable_legend=False,
            ),
            flow_state,
        )

    def _create_highlight_tracks_not_assigned_to_flows_plotter(
        self, road_user_assigner: RoadUserAssigner, flow_state: FlowState
    ) -> Plotter:
        return self._create_highlight_tracks_assigned_to_flow(
            self._create_highlight_tracks_assigned_to_flows_factory(
                self._create_tracks_not_assigned_to_flows_filter(
                    self._get_data_provider_all_filters(), road_user_assigner
                ),
                self._color_palette_provider,
                alpha=1,
                enable_legend=False,
            ),
            flow_state,
        )

    def _get_data_provider_class_filter(self) -> PandasDataFrameProvider:
        if not self._data_provider_class_filter:
            self._data_provider_class_filter = self._build_filter_by_classification(
                self._get_pandas_data_provider()
            )
        return self._data_provider_class_filter

    def _get_data_provider_all_filters(self) -> PandasDataFrameProvider:
        if not self._data_provider_all_filters:
            self._data_provider_all_filters = self._build_filter_by_classification(
                self._create_filter_by_occurrence()
            )
        return self._data_provider_all_filters

    def _create_filter_by_occurrence(self) -> PandasDataFrameProvider:
        return FilterByOccurrence(
            self._get_pandas_data_provider(),
            self._track_view_state,
            self._create_dataframe_filter_builder(),
        )

    def _create_get_sections_by_id(self) -> GetSectionsById:
        return GetSectionsById(self._section_repository)

    def _get_tracks_not_intersecting_selected_sections_filter(
        self,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            self._get_data_provider_all_filters(),
            TracksNotIntersectingSelection(
                TracksIntersectingGivenSections(
                    [section],
                    self._create_tracks_intersecting_sections(),
                    self._create_get_sections_by_id(),
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

    def _get_pandas_data_provider(self) -> PandasDataFrameProvider:
        if not self._pandas_data_provider:
            cached_pandas_track_provider = self._create_pandas_track_provider(
                self._pulling_progressbar_builder
            )
            self._pandas_data_provider = self._wrap_pandas_track_offset_provider(
                cached_pandas_track_provider
            )
        return self._pandas_data_provider

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

    def _get_tracks_intersecting_sections_filter(
        self,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            self._get_data_provider_all_filters(),
            TracksIntersectingGivenSections(
                [section],
                self._create_tracks_intersecting_sections(),
                self._create_get_sections_by_id(),
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
                        [section],
                        tracks_intersecting_sections,
                        get_sections_by_id,
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
        return DataFrameFilterBuilder()

    # TODO duplicate to main_application.py
    def _create_tracks_intersecting_sections(self) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(
            GetTracksWithoutSingleDetections(self._track_repository),
            ShapelyIntersector(),
        )
