# % Import libraries
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import seaborn as sns
import ujson
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from numpy import ndarray
from pandas import DataFrame, read_json

from OTAnalytics.domain import track
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, Track, TrackImage

ENCODING = "UTF-8"


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


@dataclass(frozen=True)
class PlottedImage(TrackImage):
    image: ndarray

    def as_array(self) -> Any:
        return self.image


def run(
    track_list: Iterable[Track],
    sections: Iterable[Section],
    image: TrackImage,
) -> TrackImage:
    # % Import tracks
    detections: list[Detection] = []
    for current_track in track_list:
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
    # sns.set(style="dark")
    img = image.as_array()
    if start_end:
        alpha = 0.1
    else:
        alpha = 0.7

    figure = Figure(figsize=(6, 4), dpi=100)
    axes = figure.add_subplot()
    axes.imshow(img)
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
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
    new_image = data.reshape(canvas.get_width_height()[::-1] + (3,))
    return PlottedImage(new_image)
