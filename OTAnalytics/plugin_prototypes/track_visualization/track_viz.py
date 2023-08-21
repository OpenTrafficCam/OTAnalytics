from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Optional, TypeVar

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
from OTAnalytics.application.state import (
    ObservableOptionalProperty,
    ObservableProperty,
    Plotter,
    TrackViewState,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.track import (
    PilImage,
    Track,
    TrackId,
    TrackIdProvider,
    TrackImage,
    TrackListObserver,
)
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

COLOR_PALETTE: dict[str, str] = {
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


class CachedPlotter(Plotter):
    def __init__(
        self,
        other: Plotter,
        subjects: list[ObservableProperty | ObservableOptionalProperty],
    ) -> None:
        self._other = other
        self._cache: Optional[TrackImage] = None

        for subject in subjects:
            subject.register(self.invalidate_cache)

    def plot(self) -> Optional[TrackImage]:
        if self._cache is None:
            self._cache = super().plot()

        return self._cache

    def invalidate_cache(self, _: Any) -> None:
        self._cache = None


ENTITY = TypeVar("ENTITY")


class DynamicLayersPlotter(Plotter, Generic[ENTITY]):
    def __init__(
        self,
        other: Plotter,
        visibility_indicator: ObservableProperty[list[ENTITY]],
    ) -> None:
        self._other = other
        visibility_indicator.register(self.notify_visibility)

    def notify_visibility(self, visible_entities: list[ENTITY]) -> None:
        # Callable[[VALUE], None]
        pass

    def notify_layers(self, entities: list[ENTITY]) -> None:
        pass

    # section list notifications
    # -> add section: notify([new_id])
    # -> add all sections -> notify([new_id_1, new_id_2,...])
    # -> remove section -> notify([])
    # -> clear -> notify([])
    #
    # section content notification
    # -> update section -> notify(exist_id)
    # -> set plugin data -> notify(exist_id)
    #
    # flow list notifications
    # -> clear -> notify([])
    # -> add flow -> notify([new_id])
    # -> add all flows -> notify([new_id_1, new_id_2,...])
    # -> remove -> notify([])
    #
    # flow content notifications:
    # -> update -> notify(exist.id)

    #

    # def notify_sections(self, sections: list[SectionId]) -> None:
    #    pass

    # def notify_flows(self, flows: list[FlowId]) -> None:
    #    pass


class DummyObservableWrapper(ObservableOptionalProperty[Any], TrackListObserver):
    def __init__(self, default: Any | None = None) -> None:
        super().__init__(default)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        self._subject.notify(None)


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
        ids: set[int] = {track_id.id for track_id in self._filter.get_ids()}
        return data.loc[data[track.TRACK_ID].isin(ids)]


class PandasTrackProvider(PandasDataFrameProvider):
    """Provides tracks as pandas DataFrame."""

    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        filter_builder: DataFrameFilterBuilder,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._filter_builder = filter_builder

    def get_data(self) -> DataFrame:
        tracks = self._datastore.get_all_tracks()
        if not tracks:
            return DataFrame()

        data = self._convert_tracks(tracks)

        if data.empty:
            return data

        return self._filter_tracks(data)

    def _convert_tracks(self, tracks: Iterable[Track]) -> DataFrame:
        """
        Convert tracks into a dataframe.

        Args:
            tracks (Iterable[Track]): tracks to convert

        Returns:
            DataFrame: tracks as dataframe
        """
        prepared: list[dict] = []
        for current_track in tracks:
            for detection in current_track.detections:
                detection_dict = detection.to_dict()
                detection_dict[track.CLASSIFICATION] = current_track.classification
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

    def _filter_tracks(
        self,
        track_df: DataFrame,
    ) -> DataFrame:
        """
        Filter tracks by classes, time and number of images.

        Args:
            filter_classes (Iterable[str]): classes to show
            track_df (DataFrame): dataframe of tracks

        Returns:
            DataFrame: filtered by classes, time and number of images
        """
        self._filter_builder.set_classification_column(track.CLASSIFICATION)
        self._filter_builder.set_occurrence_column(track.OCCURRENCE)
        filter_element = self._track_view_state.filter_element.get()
        dataframe_filter = filter_element.build_filter(self._filter_builder)

        return next(iter(dataframe_filter.apply([track_df])))


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
        datastore: Datastore,
        track_view_state: TrackViewState,
        filter_builder: DataFrameFilterBuilder,
    ) -> None:
        super().__init__(datastore, track_view_state, filter_builder)
        datastore.register_tracks_observer(self)
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
        """Internal method to convert the given tracks
            to dataframe format without caching.

        Args:
            tracks (Iterable[Track]): the tracks to be converted.

        Returns:
            DataFrame: the dataframe representation of the given tracks.
        """
        return super()._convert_tracks(tracks)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """Take notice of some change in the track repository.
        Remove cached tracks matching any given id.
        Add tracks of ids not yet present in cache.
        Clear cache if no ids are given.

        Args:
            tracks (list[TrackId]): the ids of changed tracks
        """
        match (tracks):
            case []:
                self._cache_df = DataFrame()
            case _:
                # filter existing tracks from cache
                filtered_cache = self._cache_without_existing_tracks(track_ids=tracks)

                # convert tracks not yet in cache
                new_df = self.__do_convert_tracks(
                    self._fetch_new_track_data(track_ids=tracks)
                )

                # concat remaining tracks and new tracks
                if filtered_cache is not None:
                    df = pandas.concat([filtered_cache, new_df])
                else:
                    df = new_df

                self._cache_df = self._sort_tracks(df)

    def _fetch_new_track_data(self, track_ids: list[TrackId]) -> list[Track]:
        existing_tracks: list[int] = []

        if not self._cache_df.empty:
            existing_tracks = self._cache_df[track.TRACK_ID].unique().tolist()

        return [
            t
            for t_id in track_ids
            if t_id.id not in existing_tracks
            and (t := self._datastore._track_repository.get_for(t_id)) is not None
        ]

    def _cache_without_existing_tracks(
        self, track_ids: list[TrackId]
    ) -> DataFrame | None:
        """Filter cached tracks.
        Only keep those not matching the ids in the given list of track_ids.
        Return None if the current cache is empty.

        Args:
            track_ids (list[TrackId]): ids of tracks to be removed from cache.

        Returns:
            DataFrame | None: filtered cache or None if it is already empty.
        """
        if self._cache_df.empty:
            return None

        track_id_nums = [t.id for t in track_ids]
        df = self._cache_df
        return df[~df[track.TRACK_ID].isin(track_id_nums)]


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
        enable_legend: bool,
        alpha: float = 0.5,
    ) -> None:
        self._data_provider = data_provider
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
            alpha (float): transparency of the lines
            axes (Axes): axes to plot on
        """
        seaborn.lineplot(
            x="x",
            y="y",
            hue=track.CLASSIFICATION,
            data=track_df,
            units=track.TRACK_ID,
            linewidth=0.6,
            estimator=None,
            sort=False,
            alpha=self._alpha,
            ax=axes,
            palette=COLOR_PALETTE,
            hue_order=CLASS_ORDER,
            legend=self._enable_legend,
        )


class TrackStartEndPointPlotter(MatplotlibPlotterImplementation):
    """Plot start and end points of tracks"""

    def __init__(
        self,
        data_provider: PandasDataFrameProvider,
        enable_legend: bool,
        alpha: float = 0.5,
    ) -> None:
        self._data_provider = data_provider
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
            hue=track.CLASSIFICATION,
            data=track_df_start_end,
            style="type",
            markers=[">", "$x$"],
            legend=self._enable_legend,
            s=15,
            ax=axes,
            palette=COLOR_PALETTE,
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
        bbox_contents = figure.canvas.copy_from_bbox(axes.bbox)
        left, bottom, right, top = bbox_contents.get_extents()

        image_array = numpy.frombuffer(bbox_contents.to_string(), dtype=numpy.uint8)
        image_array = image_array.reshape([top - bottom, right - left, 4])
        return PilImage(Image.fromarray(image_array, mode="RGBA"))
