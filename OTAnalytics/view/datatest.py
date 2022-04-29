import json
import geopandas as gpd
from shapely.geometry import LineString, Point
import pandas as pd


color_dict = {
    "car": (89, 101, 212),
    "bicycle": (73, 166, 91),
    "truck": (97, 198, 212),
    "motorcycle": (148, 52, 137),
    "person": (214, 107, 88),
    "bus": (179, 177, 68),
}


def load_and_convert(x_factor=1, y_factor=1, filepath=None):
    """loads detections from Track-File and converts into displayable format"""

    filepath = "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data/input/radeberg_FR20_2020-02-20_12-00-00.ottrk"
    files = open(filepath, "r")
    files = files.read()

    tracks = {}

    loaded_dict = json.loads(files)

    # raw detections from OTVision
    raw_detections = loaded_dict["data"]

    for frame in raw_detections:
        for detection in raw_detections[frame]:
            if detection in tracks:
                tracks[detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"] * x_factor,
                        raw_detections[frame][detection]["y"] * y_factor,
                    ]
                )

                tracks[detection]["Frame"].append(int(frame))

            elif raw_detections[frame][detection]["class"] in color_dict.keys():
                tracks[detection] = {
                    "Coord": [],
                    "Frame": [int(frame)],
                    "Class": raw_detections[frame][detection]["class"],
                }

                tracks[detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"] * x_factor,
                        raw_detections[frame][detection]["y"] * y_factor,
                    ]
                )

    tracks_df = pd.DataFrame.from_dict(tracks, orient="index")

    tracks_df["Coord_count"] = tracks_df.apply(
        lambda pointtuples: (len(pointtuples["Coord"])), axis=1
    )
    tracks_df = tracks_df.loc[tracks_df["Coord_count"] >= 2]

    tracks_df["geometry"] = tracks_df.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1
    )
    for coordinate in tracks_df["Coord"]:

        print(coordinate)
        print(tracks_df.Class)

    return raw_detections, tracks


load_and_convert()