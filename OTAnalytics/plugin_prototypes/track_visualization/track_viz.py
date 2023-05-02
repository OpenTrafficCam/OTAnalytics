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
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, PilImage, Track, TrackImage

ENCODING = "UTF-8"
DPI = 100

CLASS_CAR = "car"
CLASS_MOTORCYCLIST = "motorcyclist"
CLASS_PEDESTRIAN = "pedestrian"
CLASS_TRUCK = "truck"
CLASS_TRUCK_TRAILER = "truck_with_trailer"
CLASS_TRUCK_SEMITRAILER = "truck_with_semitrailer"
CLASS_BICYCLIST = "bicyclist"
CLASS_DELVAN = "delivery_van"


class TrackPlotter(ABC):
    """
    Abstraction to plot the background image.
    """

    @abstractmethod
    def plot(
        self,
        tracks: Iterable[Track],
        sections: Iterable[Section],
        width: int,
        height: int,
        filter_classes: Iterable[str] = (
            "car",
            "motorcycle",
            "person",
            "truck",
            "bicycle",
            "train",
        ),
        num_min_frames: int = 30,
        start_time: str = "",
        end_time: str = "2022-09-15 07:05:00",
        start_end: bool = True,
        plot_sections: bool = True,
        alpha: float = 0.1,
        offset: Optional[RelativeOffsetCoordinate] = RelativeOffsetCoordinate(0, 0),
    ) -> TrackImage:
        pass


class PlotterPrototype(Plotter):
    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        track_plotter: TrackPlotter,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._track_plotter = track_plotter

    def plot(self) -> Optional[TrackImage]:
        if track := next(iter(self._datastore.get_all_tracks())):
            if new_image := self._datastore.get_image_of_track(track.id):
                if self._track_view_state.show_tracks.get():
                    track_image = self._track_plotter.plot(
                        self._datastore.get_all_tracks(),
                        self._datastore.get_all_sections(),
                        width=new_image.width(),
                        height=new_image.height(),
                        offset=self._track_view_state.track_offset.get(),
                    )
                    return new_image.add(track_image)
                else:
                    return new_image
        return None


class MatplotlibTrackPlotter(TrackPlotter):
    """
    Implementation of the TrackPlotter interface using matplotlib.
    """

    def plot(
        self,
        tracks: Iterable[Track],
        sections: Iterable[Section],
        width: int,
        height: int,
        filter_classes: Iterable[str] = (
            CLASS_CAR,
            CLASS_MOTORCYCLIST,
            CLASS_PEDESTRIAN,
            CLASS_TRUCK,
            CLASS_TRUCK_TRAILER,
            CLASS_TRUCK_SEMITRAILER,
            CLASS_BICYCLIST,
            CLASS_DELVAN,
        ),
        num_min_frames: int = 30,
        start_time: str = "",
        end_time: str = "",
        start_end: bool = True,
        plot_sections: bool = False,
        alpha: float = 0.2,
        offset: Optional[RelativeOffsetCoordinate] = RelativeOffsetCoordinate(0, 0),
    ) -> TrackImage:
        """
        Plot the tracks and section as image.

        Args:
            tracks (Iterable[Track]): tracks to be plotted
            sections (Iterable[Section]): sections to be plotted
            width (int): width of the image
            height (int): height of the image
            filter_classes (Iterable[str], optional): classes to filter tracks.
            Defaults to ( "car", "motorcycle", "person", "truck", "bicycle", "train", ).
            num_min_frames (int, optional): minimum number of frames of a track to be
            shown. Defaults to 30.
            start_time (str, optional): start of time period to show tracks. Defaults
            to "".
            end_time (_type_, optional): end of time period to show tracks. Defaults to
            "".
            start_end (bool, optional): show start and end points. Defaults to True.
            plot_sections (bool, optional): show sections. Defaults to True.
            alpha (float, optional): transparency of tracks. Defaults to 0.1.

        Returns:
            TrackImage: image containing tracks and sections
        """
        track_df = self._convert_tracks(tracks)

        track_df = self._apply_offset(track_df, offset)

        # % Filter times
        track_df = self._filter_tracks(
            filter_classes, num_min_frames, start_time, end_time, track_df
        )

        image_width = width / DPI
        image_height = height / DPI
        figure = self._create_figure(width=image_width, height=image_height)
        axes = self._create_axes(image_width, image_height, figure)
        self._plot_tracks(track_df, alpha, axes)
        if start_end:
            self._plot_start_end_points(track_df, axes)
        if plot_sections:
            self._plot_sections(sections, axes)
        self._style_axes(width, height, axes)
        return self.convert_to_track_image(figure, axes)

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
        start_time: str,
        end_time: str,
        track_df: DataFrame,
    ) -> DataFrame:
        """
        Filter tracks by classes, time and number of images.

        Args:
            filter_classes (Iterable[str]): classes to show
            num_min_frames (int): minimum number of frames of a track to be shown
            start_time (str): start of time period of tracks to be shown
            end_time (str): end of time period of tracks to be shown
            track_df (DataFrame): dataframe of tracks

        Returns:
            DataFrame: filtered by classes, time and number of images
        """
        if start_time != "":
            track_df = track_df[track_df[track.OCCURRENCE] >= start_time]

        if end_time != "":
            track_df = track_df[track_df[track.OCCURRENCE] < end_time]

        # % Filter traffic classes
        track_df = track_df[track_df[track.CLASSIFICATION].isin(filter_classes)]

        return track_df[
            track_df[track.TRACK_ID].isin(self._min_frames(track_df, num_min_frames))
        ]

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

    def _plot_tracks(self, track_df: DataFrame, alpha: float, axes: Axes) -> None:
        """
        Plot given tracks on the given axes with the given transparency (alpha)

        Args:
            track_df (DataFrame): tracks to plot
            alpha (float): transparency of the lines
            axes (Axes): axes to plot on
        """
        color_palette = {
            CLASS_CAR: "blue",
            CLASS_MOTORCYCLIST: "skyblue",
            CLASS_PEDESTRIAN: "brown",
            CLASS_TRUCK: "red",
            CLASS_TRUCK_TRAILER: "purple",
            CLASS_TRUCK_SEMITRAILER: "pink",
            CLASS_BICYCLIST: "lime",
            CLASS_DELVAN: "yellow",
        }
        class_order = [
            CLASS_CAR,
            CLASS_MOTORCYCLIST,
            CLASS_PEDESTRIAN,
            CLASS_TRUCK,
            CLASS_TRUCK_TRAILER,
            CLASS_TRUCK_SEMITRAILER,
            CLASS_BICYCLIST,
            CLASS_DELVAN,
        ]
        seaborn.lineplot(
            x="x",
            y="y",
            hue=track.CLASSIFICATION,
            data=track_df,
            units=track.TRACK_ID,
            linewidth=0.6,
            estimator=None,
            sort=False,
            alpha=alpha,
            ax=axes,
            palette=color_palette,
            hue_order=class_order,
            zorder=1,
        )

    def _plot_start_end_points(self, track_df: DataFrame, axes: Axes) -> None:
        """
        Plot start and end points of given tracks on the axes.

        Args:
            track_df (DataFrame): tracks to plot start and end points of
            axes (Axes): axes to plot on
        """

        color_palette = {
            CLASS_CAR: "blue",
            CLASS_MOTORCYCLIST: "skyblue",
            CLASS_PEDESTRIAN: "salmon",
            CLASS_TRUCK: "red",
            CLASS_TRUCK_TRAILER: "purple",
            CLASS_TRUCK_SEMITRAILER: "pink",
            CLASS_BICYCLIST: "lime",
            CLASS_DELVAN: "yellow",
        }

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
            palette=color_palette,
            zorder=2,
        )

    def _plot_sections(self, sections: Iterable[Section], axes: Axes) -> None:
        """
        Plot sections on the given axes.

        Args:
            sections (Iterable[Section]): sections to be plotted
            axes (Axes): axes to plot on
        """
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

    def _convert_tracks(self, tracks: Iterable[Track]) -> DataFrame:
        """
        Convert tracks into a dataframe.

        Args:
            tracks (Iterable[Track]): tracks to convert

        Returns:
            DataFrame: tracks as dataframe
        """
        detections: list[Detection] = []
        for current_track in tracks:
            detections.extend(current_track.detections)
        prepared = [detection.to_dict() for detection in detections]
        converted = DataFrame(
            prepared
            # tracks[ottrk_format.DATA][ottrk_format.DETECTIONS]
        )
        return converted.sort_values([track.TRACK_ID, track.FRAME])

    def _apply_offset(
        self, tracks: DataFrame, offset: Optional[RelativeOffsetCoordinate]
    ) -> DataFrame:
        if new_offset := offset:
            tracks[track.X] = tracks[track.X] + new_offset.x * tracks[track.W]
            tracks[track.Y] = tracks[track.Y] + new_offset.y * tracks[track.H]
        return tracks

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
        return PilImage(Image.fromarray(image_array))
