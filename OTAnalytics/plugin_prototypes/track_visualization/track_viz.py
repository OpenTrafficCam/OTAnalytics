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
from OTAnalytics.application.state import Plotter, TrackViewState
from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.track import PilImage, Track, TrackImage
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder

ENCODING = "UTF-8"
DPI = 100

CLASS_CAR = "car"
CLASS_MOTORCYCLE = "motorcycle"
CLASS_PERSON = "person"
CLASS_TRUCK = "truck"
CLASS_BICYCLE = "bicycle"
CLASS_TRAIN = "train"

COLOR_PALETTE: dict[str, str] = {
    CLASS_CAR: "blue",
    CLASS_MOTORCYCLE: "skyblue",
    CLASS_PERSON: "salmon",
    CLASS_TRUCK: "purple",
    CLASS_BICYCLE: "lime",
    CLASS_TRAIN: "gold",
}

CLASS_ORDER = [
    CLASS_CAR,
    CLASS_TRUCK,
    CLASS_MOTORCYCLE,
    CLASS_PERSON,
    CLASS_BICYCLE,
    CLASS_TRAIN,
]

FILTER_CLASSES: Iterable[str] = (
    CLASS_CAR,
    CLASS_MOTORCYCLE,
    CLASS_PERSON,
    CLASS_TRUCK,
    CLASS_BICYCLE,
    CLASS_TRAIN,
)

NUM_MIN_FRAMES = 30


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
        if self._track_view_state.show_tracks.get():
            return self._track_plotter.plot(
                width=self.__get_plotting_width(),
                height=self.__get_plotting_height(),
            )
        return None

    def __get_plotting_height(self) -> int:
        return self._track_view_state.view_height.get()

    def __get_plotting_width(self) -> int:
        return self._track_view_state.view_width.get()


class PandasDataFrameProvider:
    @abstractmethod
    def get_data(self) -> DataFrame:
        pass


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

    def get_data(self) -> Optional[DataFrame]:
        offset = self._track_view_state.track_offset.get()

        tracks = self._datastore.get_all_tracks()
        if not tracks:
            return None

        data = self._convert_tracks(tracks)

        if data.empty:
            return data

        data = self._apply_offset(data, offset)
        return self._filter_tracks(FILTER_CLASSES, NUM_MIN_FRAMES, data)

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

        converted = DataFrame(prepared)
        if (track.TRACK_ID in converted.columns) and (track.FRAME in converted.columns):
            return converted.sort_values([track.TRACK_ID, track.FRAME])
        return converted

    def _apply_offset(
        self, tracks: DataFrame, offset: Optional[RelativeOffsetCoordinate]
    ) -> DataFrame:
        if new_offset := offset:
            tracks[track.X] = tracks[track.X] + new_offset.x * tracks[track.W]
            tracks[track.Y] = tracks[track.Y] + new_offset.y * tracks[track.H]
        return tracks

    # % Filter length (number of frames)
    def _min_frames(self, data: DataFrame, min_frames: int = 10) -> list:
        """
        Filter tracks by the number of frames.

        Args:
            data (DataFrame): dataframe containing tracks
            min_frames (int, optional): minimum number of frames. Defaults to 10.

        Returns:
            list: tracks with at least the minimum number of frames
        """
        tmp = data[[track.FRAME, track.TRACK_ID]]
        tmp_min_frames = tmp.groupby(track.TRACK_ID).count().reset_index()
        return [
            tmp_min_frames.loc[i, track.TRACK_ID]
            for i in range(len(tmp_min_frames))
            if tmp_min_frames.loc[i, track.FRAME] >= min_frames
        ]

    def _filter_tracks(
        self,
        filter_classes: Iterable[str],
        num_min_frames: int,
        track_df: DataFrame,
    ) -> DataFrame:
        """
        Filter tracks by classes, time and number of images.

        Args:
            filter_classes (Iterable[str]): classes to show
            num_min_frames (int): minimum number of frames of a track to be shown
            track_df (DataFrame): dataframe of tracks

        Returns:
            DataFrame: filtered by classes, time and number of images
        """
        track_df[
            track_df[track.TRACK_ID].isin(self._min_frames(track_df, num_min_frames))
        ]
        self._filter_builder.set_classification_column(track.CLASSIFICATION)
        self._filter_builder.set_occurrence_column(track.OCCURRENCE)
        filter_element = self._track_view_state.filter_element.get()
        dataframe_filter = filter_element.build_filter(self._filter_builder)

        track_df = next(iter(dataframe_filter.apply([track_df])))

        return track_df[track_df[track.CLASSIFICATION].isin(filter_classes)]


class MatplotlibPlotterImplementation(ABC):
    """Abstraction to plot on a matplotlib axes"""

    @abstractmethod
    def plot(self, axes: Axes) -> None:
        pass


class TrackGeometryPlotter(MatplotlibPlotterImplementation):
    """Plot geometry of tracks."""

    def __init__(
        self,
        data_provider: PandasTrackProvider,
        alpha: float = 0.5,
    ) -> None:
        self._data_provider = data_provider
        self._alpha = alpha

    def plot(self, axes: Axes) -> None:
        data = self._data_provider.get_data()
        if data is not None:
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
        )


class TrackStartEndPointPlotter(MatplotlibPlotterImplementation):
    """Plot start and end points of tracks"""

    def __init__(
        self,
        data_provider: PandasTrackProvider,
        alpha: float = 0.5,
    ) -> None:
        self._data_provider = data_provider
        self._alpha = alpha

    def plot(self, axes: Axes) -> None:
        data = self._data_provider.get_data()
        if data is not None:
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
            legend=False,
            s=15,
            ax=axes,
            palette=COLOR_PALETTE,
        )


class SectionGeometryPlotter(MatplotlibPlotterImplementation):
    """Plot geometry of sections."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore

    def plot(self, axes: Axes) -> None:
        """
        Plot sections on the given axes.

        Args:
            sections (Iterable[Section]): sections to be plotted
            axes (Axes): axes to plot on
        """
        sections = self._datastore.get_all_sections()
        sectionlist = [section.to_dict() for section in sections]
        for section in range(len(sectionlist)):
            x_data = [
                sectionlist[section][i]["x"]
                for i in sectionlist[section].keys()
                if i in ["start", "end"]
            ]
            y_data = [
                sectionlist[section][i]["y"]
                for i in sectionlist[section].keys()
                if i in ["start", "end"]
            ]
            seaborn.lineplot(
                x=x_data,
                y=y_data,
                linewidth=2,
                alpha=1,
                color="black",
                ax=axes,
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
