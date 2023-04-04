from typing import Iterable

import numpy as np
import pandas
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import Divider, Size
from pandas import DataFrame

from OTAnalytics.domain import track
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, Track, TrackImage
from OTAnalytics.plugin_video_processing.video_reader import NdArrayImage

ENCODING = "UTF-8"
DPI = 100


class TrackPlotter:
    def plot(
        self,
        tracks: Iterable[Track],
        sections: Iterable[Section],
        width: int,
        height: int,
        filter_classes: list[str] = [
            "car",
            "motorcycle",
            "person",
            "truck",
            "bicycle",
            "train",
        ],
        num_min_frames: int = 30,
        start_time: str = "",
        end_time: str = "2022-09-15 07:05:00",
        start_end: bool = True,
        plot_sections: bool = True,
        alpha: float = 0.1,
    ) -> TrackImage:
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
        tmp = data[[track.FRAME, track.TRACK_ID]]
        tmp_min_frames = tmp.groupby(track.TRACK_ID).count().reset_index()
        return [
            tmp_min_frames.loc[i, track.TRACK_ID]
            for i in range(len(tmp_min_frames))
            if tmp_min_frames.loc[i, track.FRAME] >= min_frames
        ]

    def _filter_tracks(
        self,
        filter_classes: list[str],
        num_min_frames: int,
        start_time: str,
        end_time: str,
        track_df: DataFrame,
    ) -> DataFrame:
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
        figure = Figure(figsize=(10, 10), dpi=DPI)
        figure.patch.set_alpha(0.0)
        return figure

    def _plot_tracks(self, track_df: DataFrame, alpha: float, axes: Axes) -> None:
        sns.lineplot(
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
        )

    def _plot_start_end_points(self, track_df: DataFrame, axes: Axes) -> None:
        track_df_start_end = pandas.concat(
            [
                track_df.groupby(track.TRACK_ID).first().reset_index(),
                # track_df.groupby("track-id").last().reset_index(),
            ]
        ).sort_values([track.TRACK_ID, track.FRAME])
        sns.scatterplot(
            x="x",
            y="y",
            hue=track.CLASSIFICATION,
            data=track_df_start_end,
            legend=False,
            s=3,
            ax=axes,
        )

    def _plot_sections(self, sections: Iterable[Section], axes: Axes) -> None:
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
            sns.lineplot(
                x=x_data,
                y=y_data,
                linewidth=2,
                alpha=1,
                color="black",
                ax=axes,
            )

    def _convert_tracks(self, tracks: Iterable[Track]) -> DataFrame:
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
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        bbox_contents = figure.canvas.copy_from_bbox(axes.bbox)
        left, bottom, right, top = bbox_contents.get_extents()

        image_array = np.frombuffer(bbox_contents.to_string(), dtype=np.uint8)
        image_array = image_array.reshape([top - bottom, right - left, 4])
        return NdArrayImage(image_array)
