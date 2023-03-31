import json
import time
from tkinter import filedialog

import geopandas as gpd
import helpers.file_helper as file_helper
import pandas as pd
from helpers.config import bbox_factor_reference
from shapely.geometry import LineString
import os
from view.helpers.gui_helper import (button_bool, color_dict, info_message,
                                     reset_buttons_tracks)


def load_trackfile():
    """Loads file with objects detected in OTVision.

    Returns:
        str: filepath
    """

    filepath = filedialog.askopenfile(filetypes=[("Tracks", "*.ottrk")])

    #set the of the trackfile manuel

    return filepath.read(), os.path.basename(filepath.name).split('/')[-1]

def deload_trackfile():
    if file_helper.list_of_analyses:
        file_helper.list_of_analyses[file_helper.list_of_analyses_index].re_initialize()
        # resets Button dictionary t everything buttonrelated to false
        reset_buttons_tracks()


def load_and_convert(x_resize_factor, y_resize_factor,autoimport=False, files=None):

    """_summary_
    Args:
        x_resize_factor (int): x factor for changed width
        y_resize_factor (int): x factor for changed width
        autoimport (bool, optional): if autoimport, trackfile is file found in folder else ask for filepath. Defaults to False.
        files (_type_, optional): _description_. Defaults to None.

    Returns:
        dataframes, dictionary, tracks as geoseries: raw_detections, tracks_dic, tracks_df, tracks_geoseries
    """

    start_time = time.time()
    
    # if button_bool["tracks_imported"]:
    #     info_message("Warning", "Tracks already imported")
    #     return

    if not autoimport:
        files, filename = load_trackfile()
        file_helper.list_of_analyses[file_helper.list_of_analyses_index].track_file = filename
        

    tracks_dic = {}
    loaded_dict = json.loads(files)


    # raw detections from OTVision
    raw_detections = loaded_dict["data"]

    for frame in raw_detections:
        for detection in raw_detections[frame]:

            if detection in tracks_dic:   
                                  
                if tracks_dic[detection]["Max_confidence"] < raw_detections[frame][detection]["conf"]:
                    tracks_dic[detection]["Max_confidence"] = raw_detections[frame][detection]["conf"]
                    vehicle_class = raw_detections[frame][detection]["class"]
                else:
                    vehicle_class = tracks_dic[detection]["Class"]                                  
                
                if vehicle_class not in bbox_factor_reference.keys():
                    vehicle_class = "unclear"

                tracks_dic[detection]["Coord"].append(
                    [
                        ((raw_detections[frame][detection]["x"]-0.5*raw_detections[frame][detection]["w"]) + (raw_detections[frame][detection]["w"]*bbox_factor_reference[vehicle_class][0]))*x_resize_factor,
                        ((raw_detections[frame][detection]["y"]-0.5*raw_detections[frame][detection]["h"]) + (raw_detections[frame][detection]["h"]*bbox_factor_reference[vehicle_class][1]))*y_resize_factor
                    ]
                )
                tracks_dic[detection]["Class"] = vehicle_class
                tracks_dic[detection]["Frame"].append(int(frame))
                tracks_dic[detection]["Width"].append(raw_detections[frame][detection]["w"]*x_resize_factor)
                tracks_dic[detection]["Height"].append(raw_detections[frame][detection]["h"]*y_resize_factor)
                tracks_dic[detection]["Confidence"].append(raw_detections[frame][detection]["conf"])
                

            elif raw_detections[frame][detection]["class"] in color_dict.keys():

                vehicle_class = raw_detections[frame][detection]["class"]

                if vehicle_class not in bbox_factor_reference.keys():
                    vehicle_class = "unclear"

                tracks_dic[detection] = {
                    "Coord": [],
                    "Frame": [int(frame)],
                    "Class": vehicle_class,
                    "Width": [raw_detections[frame][detection]["w"]*x_resize_factor],
                    "Height":[raw_detections[frame][detection]["h"]*y_resize_factor],
                    "Confidence": [raw_detections[frame][detection]["conf"]],
                    "Max_confidence": raw_detections[frame][detection]["conf"]
                }

                tracks_dic[detection]["Coord"].append(
                    [
                        ((raw_detections[frame][detection]["x"]-0.5*raw_detections[frame][detection]["w"]) + (raw_detections[frame][detection]["w"]*bbox_factor_reference[vehicle_class][0]))*x_resize_factor,
                        ((raw_detections[frame][detection]["y"]-0.5*raw_detections[frame][detection]["h"]) + (raw_detections[frame][detection]["h"]*bbox_factor_reference[vehicle_class][1]))*y_resize_factor
                    ]
                )

    if not tracks_dic:
        #TODO ABORT MESSAGE
        return None, None, None, None

    # only valid track when more than one detection
    # only for drawing on canvas due to better df-loc with frames
    tracks_df = create_tracks_dataframe(tracks_dic)

    # creates dataframe only with geoseries
    tracks_geoseries = create_geoseries(tracks_df)

    print("--- %s seconds ---" % (time.time() - start_time))


    #change when using autoload and evaluation
    # button_bool["tracks_imported"] = True

    #TODO raw dictionary not necessarry
    tracks_df.to_csv("dataframe.csv")


    return raw_detections, tracks_dic, tracks_df, tracks_geoseries


def create_geoseries(tracks_df):

    return gpd.GeoSeries(tracks_df["geometry"])
    


def create_tracks_dataframe(tracks_dic):
    """Creates dataframe from tracksdictionary 

    Args:
        tracks_dic (dictionary): dictionary with trackinformation

    Returns:
        dataframe: from dictionary with keys as columns
    """
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

    tracks_df.reset_index()


    return tracks_df


def return_first_frame(lst):
    return lst[0]


def return_last_frame(lst):
    return lst[-1]
