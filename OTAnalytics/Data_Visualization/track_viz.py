# % Import libraries
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.otvision_parser import OttrkParser

# % Set variables
ottrk_file = Path("data/Standard_SCUEHQ_FR30_2022-09-15_07-00-00.008.ottrk")
filter_classes = ["car", "motorcycle", "person", "truck", "bicycle", "train"]
num_min_frames = 30
background_img = "data/vlcsnap-2023-03-09-11h40m22s762.png"
output_img = "data/tracks.png"
start_time = ""
end_time = "2022-09-15 07:05:00"
start_end = True

# % Import tracks
track_parser = OttrkParser()
tracks = track_parser._parse_bz2(ottrk_file)
track_df = pd.DataFrame(tracks[ottrk_format.DATA][ottrk_format.DETECTIONS]).sort_values(
    ["track-id", "frame"]
)
track_df["occurrence"] = pd.to_datetime(track_df["occurrence"])

# % Filter times
if start_time != "":
    start_time_formatted = pd.to_datetime(start_time)
    track_df = track_df[track_df["occurrence"] >= start_time]

if end_time != "":
    end_time_formatted = pd.to_datetime(end_time)
    track_df = track_df[track_df["occurrence"] < end_time]

# % Filter traffic classes
track_df = track_df[track_df["class"].isin(filter_classes)]


# % Filter length (number of frames)
def min_frames(data: pd.DataFrame, min_frames: int = 10) -> list:
    tmp = data[["frame", "track-id"]]
    tmp_min_frames = tmp.groupby("track-id").count().reset_index()
    list_min_frames = [
        tmp_min_frames.loc[i, "track-id"]
        for i in range(0, len(tmp_min_frames))
        if tmp_min_frames.loc[i, "frame"] >= min_frames
    ]
    return list_min_frames


track_df = track_df[track_df["track-id"].isin(min_frames(track_df, num_min_frames))]


# % Determine max class
# chose max class by sum of confidence
def max_class(data: pd.DataFrame) -> dict:
    tmp = data[["class", "track-id", "confidence"]]
    map_df = tmp.groupby(["track-id", "class"]).agg({"confidence": sum}).reset_index()

    class_map = {
        map_df.loc[i, "track-id"]: map_df.loc[i, "class"]
        for i in map_df.groupby("track-id")["confidence"].idxmax()
    }
    return class_map


track_df["max_class"] = track_df["track-id"].map(max_class(track_df))

# % Get start and end points only

if start_end:
    track_df_start_end = pd.concat(
        [
            track_df.groupby("track-id").first().reset_index(),
            # track_df.groupby("track-id").last().reset_index(),
        ]
    ).sort_values(["track-id", "frame"])


# % Plot the image
ottrk_name = str(ottrk_file).split("/")[-1]
sns.set(style="dark")
img = mpimg.imread(background_img)
if start_end:
    alpha = 0.1
else:
    alpha = 0.7
trkimg = sns.lineplot(
    x="x",
    y="y",
    hue="max_class",
    data=track_df,
    units="track-id",
    linewidth=0.6,
    estimator=None,
    sort=False,
    alpha=alpha,
)
trkimg.imshow(img)
if start_end:
    sns.scatterplot(
        x="x",
        y="y",
        hue="max_class",
        data=track_df_start_end,
        legend=False,
        s=3,
    )
trkimg.set(xlabel="", ylabel="", xticklabels=[], yticklabels=[])
plt.title(f"Tracks from '{ottrk_name}'", y=1.05, fontsize=12)
trkimg.legend(title="Class", loc="upper left", bbox_to_anchor=(1, 1))
plt.subplots_adjust(top=0.8)
plt.savefig(
    output_img,
    orientation="landscape",
    dpi=300,
    bbox_inches="tight",
)
