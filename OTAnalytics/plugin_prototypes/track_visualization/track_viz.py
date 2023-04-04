# % Import libraries
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import seaborn as sns
import ujson
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import Divider, Size
from pandas import DataFrame, read_json
from plugin_video_processing.video_reader import NdArrayImage

from OTAnalytics.domain import track
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, Track, TrackImage

ENCODING = "UTF-8"
DPI = 100


# % Set variables
ottrk_file = Path("data/Standard_SCUEHQ_FR30_2022-09-15_07-00-00.008.ottrk")
filter_classes = ["car", "motorcycle", "person", "truck", "bicycle", "train"]
num_min_frames = 30
background_img = "data/vlcsnap-2023-03-09-11h40m22s762.png"
output_img = "data/tracks.png"
start_time = ""
end_time = "2022-09-15 07:05:00"
start_end = True
plot_sections = True
sectionlist_json_path = Path("data/sectionlist_v2.json")


class JsonParser:
    @staticmethod
    def from_dict(f: Path) -> dict:
        with open(f, "r", encoding=ENCODING) as out:
            return ujson.load(out)


class PandasDataFrameParser:
    @staticmethod
    def from_json(f: Path) -> DataFrame:
        return read_json(f)

    @staticmethod
    def from_dict(d: dict, transpose: bool = False) -> DataFrame:
        df = DataFrame(d)
        return df.transpose() if transpose else df


# % Filter length (number of frames)
def min_frames(data: pd.DataFrame, min_frames: int = 10) -> list:
    tmp = data[[track.FRAME, track.TRACK_ID]]
    tmp_min_frames = tmp.groupby(track.TRACK_ID).count().reset_index()
    list_min_frames = [
        tmp_min_frames.loc[i, track.TRACK_ID]
        for i in range(0, len(tmp_min_frames))
        if tmp_min_frames.loc[i, track.FRAME] >= min_frames
    ]
    return list_min_frames


# % Determine max class
# chose max class by sum of confidence
def max_class(data: pd.DataFrame) -> dict:
    tmp = data[[track.CLASSIFICATION, track.TRACK_ID, track.CONFIDENCE]]
    map_df = (
        tmp.groupby([track.TRACK_ID, track.CLASSIFICATION])
        .agg({track.CONFIDENCE: sum})
        .reset_index()
    )

    class_map = {
        map_df.loc[i, track.TRACK_ID]: map_df.loc[i, track.CLASSIFICATION]
        for i in map_df.groupby(track.TRACK_ID)[track.CONFIDENCE].idxmax()
    }
    return class_map


def run(
    tracks: Iterable[Track],
    sections: Iterable[Section],
    width: int,
    height: int,
) -> TrackImage:
    # % Import tracks
    detections: list[Detection] = []
    for current_track in tracks:
        detections.extend(current_track.detections)
    prepared = [detection.to_dict() for detection in detections]
    converted = pd.DataFrame(
        prepared
        # tracks[ottrk_format.DATA][ottrk_format.DETECTIONS]
    )
    track_df = converted.sort_values([track.TRACK_ID, track.FRAME])

    # % Import sections
    # % Import Sectionlist
    sectionlist = [section.to_dict() for section in sections]
    # JsonParser.from_dict(sectionlist_json_path)["sections"]

    # % Filter times
    if start_time != "":
        track_df = track_df[track_df[track.OCCURRENCE] >= start_time]

    if end_time != "":
        track_df = track_df[track_df[track.OCCURRENCE] < end_time]

    # % Filter traffic classes
    track_df = track_df[track_df[track.CLASSIFICATION].isin(filter_classes)]

    track_df = track_df[
        track_df[track.TRACK_ID].isin(min_frames(track_df, num_min_frames))
    ]

    track_df["max_class"] = track_df[track.TRACK_ID].map(max_class(track_df))

    # % Get start and end points only

    if start_end:
        track_df_start_end = pd.concat(
            [
                track_df.groupby(track.TRACK_ID).first().reset_index(),
                # track_df.groupby("track-id").last().reset_index(),
            ]
        ).sort_values([track.TRACK_ID, track.FRAME])

    # % Plot the image
    ottrk_name = str(ottrk_file).split("/")[-1]
    if start_end:
        alpha = 1.0
    else:
        alpha = 1.0

    figure = Figure(figsize=(10, 10), dpi=DPI)
    # The first items are for padding and the second items are for the axes.
    # sizes are in inch.
    image_width = width / DPI
    h = [Size.Fixed(0.0), Size.Fixed(image_width)]
    image_height = height / DPI
    v = [Size.Fixed(0.0), Size.Fixed(image_height)]

    divider = Divider(
        fig=figure,
        pos=(0, 0, 1, 1),
        horizontal=h,
        vertical=v,
        aspect=False,
    )
    # The width and height of the rectangle are ignored.

    axes = figure.add_axes(
        divider.get_position(), axes_locator=divider.new_locator(nx=1, ny=1)
    )
    sns.lineplot(
        x="x",
        y="y",
        hue="max_class",
        data=track_df,
        units=track.TRACK_ID,
        linewidth=0.6,
        estimator=None,
        sort=False,
        alpha=alpha,
        ax=axes,
    )
    if start_end:
        sns.scatterplot(
            x="x",
            y="y",
            hue="max_class",
            data=track_df_start_end,
            legend=False,
            s=3,
            ax=axes,
        )
    if plot_sections:
        for section in range(0, len(sectionlist)):
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
    axes.set(
        xlabel="",
        ylabel="",
        xticklabels=[],
        yticklabels=[],
    )
    axes.set_title(f"Tracks from '{ottrk_name}'", y=1.05, fontsize=12)
    axes.legend(title="Class", loc="upper left", bbox_to_anchor=(1, 1))
    figure.subplots_adjust(top=0.8)
    figure.patch.set_alpha(0.0)
    axes.patch.set_alpha(0.0)
    axes.set_ylim(0, height)
    axes.set_xlim(0, width)
    axes.invert_yaxis()
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    bbox_contents = figure.canvas.copy_from_bbox(axes.bbox)
    left, bottom, right, top = bbox_contents.get_extents()

    image_array = np.frombuffer(bbox_contents.to_string(), dtype=np.uint8)
    image_array = image_array.reshape([top - bottom, right - left, 4])
    return NdArrayImage(image_array)
