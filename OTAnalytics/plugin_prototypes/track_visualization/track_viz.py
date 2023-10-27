import random
from abc import ABC, abstractmethod
from typing import Iterable, Optional

import numpy
import pandas
import seaborn
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import Divider, Size
from pandas import DataFrame
from PIL import Image

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.plotting import DynamicLayersPlotter, EntityPlotterFactory
from OTAnalytics.application.state import (
    FlowState,
    Plotter,
    SectionState,
    TrackViewState,
)
from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.domain import track
from OTAnalytics.domain.event import Event, EventRepository, EventRepositoryEvent
from OTAnalytics.domain.flow import FlowId, FlowListObserver, FlowRepository
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import SectionId, SectionListObserver, SectionRepository
from OTAnalytics.domain.track import (
    PilImage,
    Track,
    TrackId,
    TrackIdProvider,
    TrackImage,
    TrackListObserver,
    TrackRepository,
    TrackRepositoryEvent,
)
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder

ENCODING = "UTF-8"
DPI = 100

CLASS_CAR = "car"
CLASS_CAR_TRAILER = "car_with_trailer"
CLASS_MOTORCYCLIST = "motorcyclist"
CLASS_PEDESTRIAN = "pedestrian"
CLASS_TRUCK = "truck"
CLASS_TRUCK_TRAILER = "truck_with_trailer"
CLASS_TRUCK_SEMITRAILER = "truck_with_semitrailer"
CLASS_BICYCLIST = "bicyclist"
CLASS_BICYCLIST_TRAILER = "bicyclist_with_trailer"
CLASS_CARGOBIKE = "cargobike_driver"
CLASS_SCOOTER = "scooter_driver"
CLASS_DELVAN = "delivery_van"
CLASS_DELVAN_TRAILER = "delivery_van_with_trailer"
CLASS_PRVAN = "private_van"
CLASS_PRVAN_TRAILER = "private_van_with_trailer"
CLASS_TRAIN = "train"
CLASS_BUS = "bus"

DEFAULT_COLOR_PALETTE: dict[str, str] = {
    CLASS_CAR: "blue",
    CLASS_CAR_TRAILER: "skyblue",
    CLASS_MOTORCYCLIST: "orange",
    CLASS_PEDESTRIAN: "salmon",
    CLASS_TRUCK: "red",
    CLASS_TRUCK_TRAILER: "purple",
    CLASS_TRUCK_SEMITRAILER: "pink",
    CLASS_BICYCLIST: "lime",
    CLASS_BICYCLIST_TRAILER: "lime",
    CLASS_CARGOBIKE: "green",
    CLASS_SCOOTER: "white",
    CLASS_DELVAN: "yellow",
    CLASS_DELVAN_TRAILER: "yellow",
    CLASS_PRVAN: "black",
    CLASS_PRVAN_TRAILER: "black",
    CLASS_TRAIN: "brown",
    CLASS_BUS: "beige",
}

CLASS_ORDER = [
    CLASS_PEDESTRIAN,
    CLASS_BICYCLIST,
    CLASS_BICYCLIST_TRAILER,
    CLASS_CARGOBIKE,
    CLASS_SCOOTER,
    CLASS_MOTORCYCLIST,
    CLASS_CAR,
    CLASS_CAR_TRAILER,
    CLASS_PRVAN,
    CLASS_PRVAN_TRAILER,
    CLASS_DELVAN,
    CLASS_DELVAN_TRAILER,
    CLASS_TRUCK,
    CLASS_TRUCK_TRAILER,
    CLASS_TRUCK_SEMITRAILER,
    CLASS_BUS,
    CLASS_TRAIN,
]


class ColorPaletteProvider:
    """Provides a color palette for all classes known from the tracks metadata.

    Uses a default palette for known values.
    Generates random colors for unknown values.
    Updates, whenever track metadata are updated.
    """

    def __init__(self, default_palette: dict[str, str]) -> None:
        self._default_palette = default_palette
        self._palette: dict[str, str] = {}

    def update(self, classifications: set[str]) -> None:
        for classification in classifications:
            if classification in self._default_palette.keys():
                self._palette[classification] = self._default_palette[classification]
            else:
                self._palette[classification] = self._generate_random_color()

    @staticmethod
    def _generate_random_color() -> str:
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)

    def get(self) -> dict[str, str]:
        return self._palette


class EventToFlowResolver:
    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def resolve(self, events: Iterable[Event]) -> Iterable[FlowId]:
        flow_ids: set[FlowId] = set()
        for event in events:
            flow_ids.update(self._resolve_flow_id_for(event.section_id))

        return flow_ids

    def _resolve_flow_id_for(self, section_id: Optional[SectionId]) -> set[FlowId]:
        if section_id:
            return set(
                [
                    flow.id
                    for flow in self._flow_repository.flows_using_section(section_id)
                ]
            )
        return set()


class FlowLayerPlotter(DynamicLayersPlotter[FlowId], FlowListObserver):
    def __init__(
        self,
        plotter_factory: EntityPlotterFactory,
        flow_state: FlowState,
        flow_repository: FlowRepository,
        track_repository: TrackRepository,
        event_repository: EventRepository,
        flow_id_resolver: EventToFlowResolver,
    ) -> None:
        super().__init__(plotter_factory, flow_state.selected_flows, self.get_flow_ids)

        flow_repository.register_flows_observer(self)
        flow_repository.register_flow_changed_observer(self.notify_flow)
        track_repository.observers.register(self.notify_invalidate)
        event_repository.register_observer(self.notify_events)

        self._repository = flow_repository
        self._flow_id_resolver = flow_id_resolver

    def notify_flow(self, flow: FlowId) -> None:
        self.notify_layers_changed([flow])

    def notify_flows(self, flows: list[FlowId]) -> None:
        self.notify_layers_changed(flows)

    def notify_events(self, events: EventRepositoryEvent) -> None:
        flows_to_add = self._flow_id_resolver.resolve(events.added)
        self._handle_add_update(flows_to_add)
        flows_to_remove = self._flow_id_resolver.resolve(events.removed)
        self._handle_remove(flows_to_remove)

    def get_flow_ids(self) -> set[FlowId]:
        return {flow.id for flow in self._repository.get_all()}


class SectionLayerPlotter(DynamicLayersPlotter[SectionId], SectionListObserver):
    def __init__(
        self,
        plotter_factory: EntityPlotterFactory,
        section_state: SectionState,
        section_repository: SectionRepository,
        track_repository: TrackRepository,
    ) -> None:
        super().__init__(
            plotter_factory, section_state.selected_sections, self.get_section_ids
        )
        section_repository.register_sections_observer(self)
        section_repository.register_section_changed_observer(self.notify_section)
        track_repository.observers.register(self.notify_invalidate)

        self._repository = section_repository

    def notify_section(self, section: SectionId) -> None:
        self.notify_layers_changed([section])

    def notify_sections(self, sections: list[SectionId]) -> None:
        self.notify_layers_changed(sections)

    def get_section_ids(self) -> set[SectionId]:
        return {section.id for section in self._repository.get_all()}


class TrackPlotter(ABC):
    """
    Abstraction to plot the background image.
    """

    @abstractmethod
    def plot(
        self,
        width: int,
        height: int,
    ) -> TrackImage:
        pass


class TrackBackgroundPlotter(Plotter):
    """Plot video frame as background."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore

    def plot(self) -> Optional[TrackImage]:
        if track := next(iter(self._datastore.get_all_tracks()), None):
            return self._datastore.get_image_of_track(track.id)
        return None


class PlotterPrototype(Plotter):
    """Convenience Class to add prototype plotters to the layer structure."""

    def __init__(
        self,
        track_view_state: TrackViewState,
        track_plotter: TrackPlotter,
    ) -> None:
        self._track_view_state = track_view_state
        self._track_plotter = track_plotter

    def plot(self) -> Optional[TrackImage]:
        return self._track_plotter.plot(
            width=self.__get_plotting_width(),
            height=self.__get_plotting_height(),
        )

    def __get_plotting_height(self) -> int:
        return self._track_view_state.view_height.get()

    def __get_plotting_width(self) -> int:
        return self._track_view_state.view_width.get()


class PandasDataFrameProvider:
    @abstractmethod
    def get_data(self) -> DataFrame:
        pass


class FilterById(PandasDataFrameProvider):
    """Filter tracks by id before providing tracks as pandas DataFrame."""

    def __init__(
        self, other: PandasDataFrameProvider, id_filter: TrackIdProvider
    ) -> None:
        self._other = other
        self._filter = id_filter

    def get_data(self) -> DataFrame:
        data = self._other.get_data()
        if data.empty:
            return data
        ids: set[str] = {track_id.id for track_id in self._filter.get_ids()}
        return data.loc[data[track.TRACK_ID].isin(ids)]


class FilterByClassification(PandasDataFrameProvider):
    def __init__(
        self,
        other: PandasDataFrameProvider,
        track_view_state: TrackViewState,
        filter_builder: DataFrameFilterBuilder,
    ) -> None:
        self._other = other
        self._track_view_state = track_view_state
        self._filter_builder = filter_builder

    def get_data(self) -> DataFrame:
        tracks_df = self._other.get_data()
        if tracks_df.empty:
            return tracks_df
        return self._filter(tracks_df)

    def _filter(
        self,
        track_df: DataFrame,
    ) -> DataFrame:
        """
        Filter tracks by classifications.

        Args:
            track_df (DataFrame): dataframe of tracks.

        Returns:
            DataFrame: filtered by classifications.
        """
        self._filter_builder.set_classification_column(track.TRACK_CLASSIFICATION)
        filter_element = self._track_view_state.filter_element.get()
        dataframe_filter = filter_element.build_filter(self._filter_builder)

        return next(iter(dataframe_filter.apply([track_df])))


class FilterByOccurrence(PandasDataFrameProvider):
    def __init__(
        self,
        other: PandasDataFrameProvider,
        track_view_state: TrackViewState,
        filter_builder: DataFrameFilterBuilder,
    ) -> None:
        self._other = other
        self._track_view_state = track_view_state
        self._filter_builder = filter_builder

    def get_data(self) -> DataFrame:
        tracks_df = self._other.get_data()
        if tracks_df.empty:
            return tracks_df
        return self._filter(tracks_df)

    def _filter(
        self,
        track_df: DataFrame,
    ) -> DataFrame:
        """
        Filter tracks by occurrence.

        Args:
            track_df (DataFrame): dataframe of tracks.

        Returns:
            DataFrame: filtered by occurrence.
        """
        self._filter_builder.set_occurrence_column(track.OCCURRENCE)
        filter_element = self._track_view_state.filter_element.get()
        dataframe_filter = filter_element.build_filter(self._filter_builder)

        return next(iter(dataframe_filter.apply([track_df])))


class PandasTrackProvider(PandasDataFrameProvider):
    """Provides tracks as pandas DataFrame."""

    def __init__(
        self,
        track_repository: TrackRepository,
        track_view_state: TrackViewState,
        filter_builder: DataFrameFilterBuilder,
        progressbar: ProgressbarBuilder,
    ) -> None:
        self._track_repository = track_repository
        self._track_view_state = track_view_state
        self._filter_builder = filter_builder
        self._progressbar = progressbar

    def get_data(self) -> DataFrame:
        tracks = self._track_repository.get_all()
        if isinstance(tracks, PandasTrackDataset):
            return tracks.as_dataframe()
        track_list = tracks.as_list()
        if not track_list:
            return DataFrame()

        return self._convert_tracks(track_list)

    def _convert_tracks(self, tracks: Iterable[Track]) -> DataFrame:
        """
        Convert tracks into a dataframe.

        Args:
            tracks (Iterable[Track]): tracks to convert.

        Returns:
            DataFrame: tracks as dataframe.
        """
        prepared: list[dict] = []
        for current_track in self._progressbar(
            list(tracks), "Tracks to be converted to DataFrame", "tracks"
        ):
            for detection in current_track.detections:
                detection_dict = detection.to_dict()
                detection_dict[
                    track.TRACK_CLASSIFICATION
                ] = current_track.classification
                prepared.append(detection_dict)

        return self._sort_tracks(DataFrame(prepared))

    def _sort_tracks(self, track_df: DataFrame) -> DataFrame:
        """Sort the given dataframe by trackId and frame,
        if both collumns are available.

        Args:
            track_df (DataFrame): dataframe of tracks

        Returns:
            DataFrame: sorted dataframe by track id and frame
        """
        if (track.TRACK_ID in track_df.columns) and (track.FRAME in track_df.columns):
            return track_df.sort_values([track.TRACK_ID, track.FRAME])
        else:
            return track_df


class PandasTracksOffsetProvider(PandasDataFrameProvider):
    def __init__(
        self, other: PandasDataFrameProvider, track_view_state: TrackViewState
    ) -> None:
        super().__init__()
        self._other = other
        self._track_view_state = track_view_state

    def get_data(self) -> DataFrame:
        offset = self._track_view_state.track_offset.get()
        data = self._other.get_data()
        if data.empty:
            return data
        return self._apply_offset(data.copy(), offset)

    def _apply_offset(
        self, tracks: DataFrame, offset: Optional[RelativeOffsetCoordinate]
    ) -> DataFrame:
        if new_offset := offset:
            tracks[track.X] = tracks[track.X] + new_offset.x * tracks[track.W]
            tracks[track.Y] = tracks[track.Y] + new_offset.y * tracks[track.H]
        return tracks


class CachedPandasTrackProvider(PandasTrackProvider, TrackListObserver):
    """Provides and caches tracks as pandas DataFrame."""

    def __init__(
        self,
        track_repository: TrackRepository,
        track_view_state: TrackViewState,
        filter_builder: DataFrameFilterBuilder,
        progressbar: ProgressbarBuilder,
    ) -> None:
        super().__init__(
            track_repository, track_view_state, filter_builder, progressbar
        )
        track_repository.register_tracks_observer(self)
        self._cache_df: DataFrame = DataFrame()

    def _convert_tracks(self, tracks: Iterable[Track]) -> DataFrame:
        """Converts the given tracks to dataframe.
        Returns the cached dataframe if conversion was already computed earlier.

        Args:
            tracks (Iterable[Track]): the tracks to be converted to dataframe.

        Returns:
            DataFrame: a dataframe containing the detections of the given tracks.
        """
        if self._cache_df.empty:
            self._cache_df = self.__do_convert_tracks(tracks)

        return self._cache_df

    def __do_convert_tracks(self, tracks: Iterable[Track]) -> DataFrame:
        """Internal method to convert the given tracks to dataframe format without
        caching.

        Args:
            tracks (Iterable[Track]): the tracks to be converted.

        Returns:
            DataFrame: the dataframe representation of the given tracks.
        """
        return super()._convert_tracks(tracks)

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """Take notice of some change in the track repository.

        Update cached tracks matching any given id.
        Add tracks of ids not yet present in cache.
        Remove from cache if not present anymore in repository.
        Clear cache if no ids are given.

        Args:
            track_event (TrackRepositoryEvent): the ids of added or removed tracks.
        """
        # TODO: Refactor observers - Distinguish between added tracks and removed tracks
        if track_event.removed:
            self._cache_df = self._remove_tracks(track_event.removed)

        if track_event.added:
            # filter existing tracks from cache
            filtered_cache = self._cache_without_existing_tracks(
                track_ids=track_event.added
            )

            # convert tracks not yet in cache
            new_df = self.__do_convert_tracks(
                self._fetch_new_track_data(track_ids=track_event.added)
            )

            # concat remaining tracks and new tracks
            if filtered_cache.empty:
                df = new_df
            else:
                df = pandas.concat([filtered_cache, new_df])
            self._cache_df = self._sort_tracks(df)

    def _reset_cache(self) -> None:
        self._cache_df = DataFrame()

    def _fetch_new_track_data(self, track_ids: list[TrackId]) -> list[Track]:
        return [
            track
            for t_id in track_ids
            if (track := self._track_repository.get_for(t_id))
        ]

    def _cache_without_existing_tracks(self, track_ids: list[TrackId]) -> DataFrame:
        """Filter cached tracks.

        Only keep those not matching the ids in the given list of track_ids.

        Args:
            track_ids (list[TrackId]): ids of tracks to be removed from cache.

        Returns:
            DataFrame : filtered cache.
        """
        if self._cache_df.empty:
            return self._cache_df

        return self._remove_tracks(track_ids)

    def _remove_tracks(self, track_ids: Iterable[TrackId]) -> DataFrame:
        track_id_nums = [t.id for t in track_ids]
        cache_without_removed_tracks = self._cache_df.drop(
            self._cache_df.index[self._cache_df[track.TRACK_ID].isin(track_id_nums)]
        )
        return cache_without_removed_tracks

    def on_tracks_cut(self, cut_tracks_dto: CutTracksDto) -> None:
        cache_without_cut_tracks = self._remove_tracks(cut_tracks_dto.original_tracks)
        self._cache_df = self._sort_tracks(cache_without_cut_tracks)


class MatplotlibPlotterImplementation(ABC):
    """Abstraction to plot on a matplotlib axes"""

    @abstractmethod
    def plot(self, axes: Axes) -> None:
        pass


class TrackGeometryPlotter(MatplotlibPlotterImplementation):
    """Plot geometry of tracks."""

    def __init__(
        self,
        data_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
        alpha: float = 0.5,
    ) -> None:
        self._data_provider = data_provider
        self._color_palette_provider = color_palette_provider
        self._enable_legend = enable_legend
        self._alpha = alpha

    def plot(self, axes: Axes) -> None:
        data = self._data_provider.get_data()
        if not data.empty:
            self._plot_dataframe(data, axes)

    def _plot_dataframe(self, track_df: DataFrame, axes: Axes) -> None:
        """
        Plot given tracks on the given axes with the given transparency (alpha)

        Args:
            track_df (DataFrame): tracks to plot
            axes (Axes): axes to plot on
        """
        seaborn.lineplot(
            x="x",
            y="y",
            hue=track.TRACK_CLASSIFICATION,
            data=track_df,
            units=track.TRACK_ID,
            linewidth=0.6,
            estimator=None,
            sort=False,
            alpha=self._alpha,
            ax=axes,
            palette=self._color_palette_provider.get(),
        )
        if self._enable_legend:
            legend = axes.legend(loc="upper right")
            legend.set_alpha(1)
        else:
            # Somehow enabling a legend from previous call to this method persists.
            # Need to manually remove it, if legend exists.
            if existing_legend := axes.legend_:
                existing_legend.remove()


class TrackStartEndPointPlotter(MatplotlibPlotterImplementation):
    """Plot start and end points of tracks"""

    def __init__(
        self,
        data_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
        alpha: float = 0.5,
    ) -> None:
        self._data_provider = data_provider
        self._color_palette_provider = color_palette_provider
        self._enable_legend = enable_legend
        self._alpha = alpha

    def plot(self, axes: Axes) -> None:
        data = self._data_provider.get_data()
        if not data.empty:
            self._plot_dataframe(data, axes)

    def _plot_dataframe(self, track_df: DataFrame, axes: Axes) -> None:
        """
        Plot start and end points of given tracks on the axes.

        Args:
            track_df (DataFrame): tracks to plot start and end points of
            axes (Axes): axes to plot on
        """
        track_df_start = track_df.groupby(track.TRACK_ID).first().reset_index()
        track_df_start["type"] = "start"

        track_df_end = track_df.groupby(track.TRACK_ID).last().reset_index()
        track_df_end["type"] = "end"

        track_df_start_end = pandas.concat([track_df_start, track_df_end]).sort_values(
            [track.TRACK_ID, track.FRAME]
        )

        seaborn.scatterplot(
            x="x",
            y="y",
            hue=track.TRACK_CLASSIFICATION,
            data=track_df_start_end,
            style="type",
            markers=[">", "$x$"],
            legend=self._enable_legend,
            s=15,
            ax=axes,
            palette=self._color_palette_provider.get(),
        )


class MatplotlibTrackPlotter(TrackPlotter):
    """
    Implementation of the TrackPlotter interface using matplotlib.
    """

    def __init__(
        self,
        plotter: MatplotlibPlotterImplementation,
    ) -> None:
        self._plotter = plotter

    def plot(
        self,
        width: int,
        height: int,
    ) -> TrackImage:
        """
        Plot the tracks and section as image.

        Args:
            width (int): width of the image
            height (int): height of the image

        Returns:
            TrackImage: image containing tracks and sections
        """
        image_width = width / DPI
        image_height = height / DPI
        figure = self._create_figure(width=image_width, height=image_height)
        axes = self._create_axes(image_width, image_height, figure)
        self._plotter.plot(axes)
        self._style_axes(width, height, axes)
        return self.convert_to_track_image(figure, axes)

    def _create_axes(self, width: float, height: float, figure: Figure) -> Axes:
        """
        Create axes to plot on.

        Args:
            width (int): width of the axes
            height (int): height of the axes
            figure (Figure): figure object to add the axis to

        Returns:
            Axes: axes object with the given width and heigt
        """
        # The first items are for padding and the second items are for the axes.
        # sizes are in inch.
        horizontal = [Size.Fixed(0.0), Size.Fixed(width)]
        vertical = [Size.Fixed(0.0), Size.Fixed(height)]

        divider = Divider(
            fig=figure,
            pos=(0, 0, 1, 1),
            horizontal=horizontal,
            vertical=vertical,
            aspect=False,
        )
        # The width and height of the rectangle are ignored.
        return figure.add_axes(
            divider.get_position(), axes_locator=divider.new_locator(nx=1, ny=1)
        )

    def _style_axes(self, width: int, height: int, axes: Axes) -> None:
        """
        Style axes object to show the image and tracks correctly.

        Args:
            width (int): width of the axes
            height (int): height of the axes
            axes (Axes): axes object to be styled
        """
        axes.set(
            xlabel="",
            ylabel="",
            xticklabels=[],
            yticklabels=[],
        )
        axes.set_ylim(0, height)
        axes.set_xlim(0, width)
        axes.patch.set_alpha(0.0)
        axes.invert_yaxis()

    def _create_figure(self, width: float, height: float) -> Figure:
        """
        Create figure to be plotted on.

        Returns:
            Figure: figure to be plotted on
        """
        figure = Figure(figsize=(width, height), dpi=DPI)
        figure.patch.set_alpha(0.0)
        return figure

    def convert_to_track_image(self, figure: Figure, axes: Axes) -> TrackImage:
        """
        Convert the content of the axes into an image.

        Args:
            figure (Figure): figure containing the axes object
            axes (Axes): axes object to convert

        Returns:
            TrackImage: image containing the content of the axes object
        """
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        bbox_contents = canvas.copy_from_bbox(axes.bbox)
        left, bottom, right, top = bbox_contents.get_extents()

        image_array = numpy.frombuffer(bbox_contents.to_string(), dtype=numpy.uint8)
        image_array = image_array.reshape([top - bottom, right - left, 4])
        return PilImage(Image.fromarray(image_array, mode="RGBA"))
