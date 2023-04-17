from typing import Iterable

import numpy
import pandas
import seaborn
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import Divider, Size
from pandas import DataFrame
from PIL import Image

from OTAnalytics.application.state import TrackPlotter
from OTAnalytics.domain import track
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, PilImage, Track, TrackImage

ENCODING = "UTF-8"
DPI = 100

CLASS_CAR = "car"
CLASS_MOTORCYCLE = "motorcycle"
CLASS_PERSON = "person"
CLASS_TRUCK = "truck"
CLASS_BICYCLE = "bicycle"
CLASS_TRAIN = "train"


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
            CLASS_MOTORCYCLE,
            CLASS_PERSON,
            CLASS_TRUCK,
            CLASS_BICYCLE,
            CLASS_TRAIN,
        ),
        num_min_frames: int = 30,
        start_time: str = "",
        end_time: str = "",
        start_end: bool = True,
        plot_sections: bool = True,
        alpha: float = 0.5,
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

        # % Filter times
        track_df = self._filter_tracks(
            filter_classes, num_min_frames, start_time, end_time, track_df
        )

        figure = self._create_figure()
        axes = self._create_axes(width, height, figure)
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

    def _create_axes(self, width: int, height: int, figure: Figure) -> Axes:
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
        image_width = width / DPI
        image_height = height / DPI
        h = [Size.Fixed(0.0), Size.Fixed(image_width)]
        v = [Size.Fixed(0.0), Size.Fixed(image_height)]

        divider = Divider(
            fig=figure,
            pos=(0, 0, 1, 1),
            horizontal=h,
            vertical=v,
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

    def _create_figure(self) -> Figure:
        """
        Create figure to be plotted on.

        Returns:
            Figure: figure to be plotted on
        """
        figure = Figure(figsize=(10, 10), dpi=DPI)
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
            CLASS_MOTORCYCLE: "skyblue",
            CLASS_PERSON: "salmon",
            CLASS_TRUCK: "purple",
            CLASS_BICYCLE: "lime",
            CLASS_TRAIN: "gold",
        }
        class_order = [
            CLASS_CAR,
            CLASS_TRUCK,
            CLASS_MOTORCYCLE,
            CLASS_PERSON,
            CLASS_BICYCLE,
            CLASS_TRAIN,
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
        )

    def _plot_start_end_points(self, track_df: DataFrame, axes: Axes) -> None:
        """
        Plot start and end points of given tracks on the axes.

        Args:
            track_df (DataFrame): tracks to plot start and end points of
            axes (Axes): axes to plot on
        """
        track_df_start_end = pandas.concat(
            [
                track_df.groupby(track.TRACK_ID).first().reset_index(),
                # track_df.groupby("track-id").last().reset_index(),
            ]
        ).sort_values([track.TRACK_ID, track.FRAME])
        seaborn.scatterplot(
            x="x",
            y="y",
            hue=track.CLASSIFICATION,
            data=track_df_start_end,
            legend=False,
            s=3,
            ax=axes,
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
