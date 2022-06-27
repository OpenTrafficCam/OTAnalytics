import json
from tkinter import filedialog
import geopandas as gpd
from shapely.geometry import LineString
import pandas as pd

from view.helpers.gui_helper import button_bool, color_dict, info_message


def load_trackfile():
    """Loads file with objects detected in OTVision.

    Returns:
        str: filepath
    """

    filepath = filedialog.askopenfile(filetypes=[("Tracks", "*.ottrk")])
    files = open(filepath.name, "r")
    return files.read()


def load_and_convert(x_factor, y_factor, autoimport=False, files=None):
    """loads detections from Track-File and converts into displayable format"""
    if button_bool["tracks_imported"]:
        info_message("Warning", "Tracks already imported")
        return

    if not autoimport:
        files = load_trackfile()

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
    button_bool["tracks_imported"] = True

    tracks_df = create_tracks_dataframe(tracks)

    tracks_geoseries = create_geoseries(tracks_df)

    return raw_detections, tracks, tracks_df, tracks_geoseries


def create_geoseries(tracks_df):

    return gpd.GeoSeries(tracks_df["geometry"])


def create_tracks_dataframe(tracks_dic):
    tracks_df = pd.DataFrame.from_dict(tracks_dic, orient="index")

    tracks_df["Coord_count"] = tracks_df.apply(
        lambda pointtuples: (len(pointtuples["Coord"])), axis=1
    )
    tracks_df = tracks_df.loc[tracks_df["Coord_count"] >= 2]

    tracks_df["geometry"] = tracks_df.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1
    )

    tracks_df["first_appearance_frame"] = tracks_df["Frame"].apply(return_first_frame)
    tracks_df["last_appearance_frame"] = tracks_df["Frame"].apply(return_last_frame)

    return tracks_df


def return_first_frame(lst):
    return lst[0]


def return_last_frame(lst):
    return lst[-1]
