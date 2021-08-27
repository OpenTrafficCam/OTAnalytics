#%%

from math import isnan
import geopandas as gpd
from numpy import NaN
from shapely.geometry import LineString, Point
import pandas as pd
from gui_dict import gui_dict
from tkinter import filedialog
import json
from collections import OrderedDict
from operator import getitem


# TODO: check if tracks and crossed sections belong to certain movement

#%%

linedetectors = {}
movement_dict = {}


d = {}


detector_dic = open("C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//combined.OTflow", "r")
object_dic = open("C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//object_dic.json", "r")

files = open(detector_dic.name, "r")
files = files.read()

flow_dic = json.loads(files)

linedetectors.update(flow_dic["Detectors"])
movement_dict.update(flow_dic["Movements"])

files = open(object_dic.name, "r")
files = files.read()

object_dic = json.loads(files)


# %%

def dic_to_detector_dataframe(flow_dic):
    """creates a dataframe from detector/flow dictionary, # TODO change to use linedetector dic that gets updated when importing flow data
    creates column with LineString-objects for the calculation of
    lineintersection with tracks

    Args:
        detector_dic (dictionary): dictionary with detectors and movements

    Returns:
        dataframe: dataframe with essential information
    """
    # change dic to dataframe
    detector_df = pd.DataFrame.from_dict(
        {("Detectors", j):
         flow_dic["Detectors"][j]for j in
         flow_dic["Detectors"].keys()}, orient='index')

    # drops first multilevel index
    detector_df.index = detector_df.index.droplevel(0)

    # turn coordinates into LineString parameters
    detector_df["geometry"] = detector_df.apply(
        lambda coordinates:
        LineString([(coordinates['start_x'], coordinates['start_y']),
                    (coordinates['end_x'], coordinates['end_y'])]), axis=1)


    return detector_df
# %%

detector_df = dic_to_detector_dataframe(flow_dic) 

# %%

def dic_to_object_dataframe(object_dic):
    """creates a dataframe from object dictionary, creates column with Polygon-objects.
    Args:
        object_dict ([dictionary]): dictionary with information of object

    Returns:
        dataframe: dictionary with information of object
    """

    # count number of coordinates (if the count is less then 3,
    # geopandas cant create Polygon)
    for object in object_dic:
        object_dic[object]["Coord_count"] = len(object_dic[object]["Coord"])

    object_df = pd.DataFrame.from_dict(object_dic, orient="index")

    object_df_validated = object_df.loc[object_df['Coord_count'] >= 3]

    # better copy so apply function wont give an error msg
    object_df_validated_copy = object_df_validated.copy()

    object_df_validated_copy["geometry"] = object_df_validated_copy.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1)

    object_df_validated_copy["start_point_geometry"] = object_df_validated_copy.apply(
        lambda pointtuples: Point(pointtuples["Coord"][0]), axis=1)

    print(object_df_validated_copy)

    return object_df_validated_copy
# %%

object_df_validated_copy = dic_to_object_dataframe(object_dic)

# %%

def calculate_intersections(detector_df, object_df_validated_copy):
    """checks if tracks and detectors intersect, alters object_dataframe

    Args:
        detector_df (dataframe): dataframe with detectors
        object_df_validated_copy (dataframe): copy of slice of valudated objects
        (at least 3 detections)

    Returns:
        dataframe: with columnheads (detectors) and boolvalue if track(row),
        intersected detector
    """
    # creates a geoseries from column(geometry) with shapely object
    track_geometry = gpd.GeoSeries(object_df_validated_copy.geometry)
    track_start_geometry = gpd.GeoSeries(object_df_validated_copy.start_point_geometry)
    
    # iterates over every detectors and returns bool value for
    # intersection with every track from geoseries
    for index, detector in detector_df.iterrows():

        # distinct shapely geometry
        detector_shapely_geometry = detector.geometry

        # columnwise comparison
        bool_intersect = track_geometry.intersects(detector_shapely_geometry)

        # returns coordinates from intersections
        point_geometry = track_geometry.intersection(detector_shapely_geometry)

        object_df_validated_copy[index+"intersectcoordinates"] = point_geometry
        object_df_validated_copy[index] = bool_intersect

    for index, detector in detector_df.iterrows():
        intersection_series = gpd.GeoSeries(
                            object_df_validated_copy[index+"intersectcoordinates"])

        distance = track_start_geometry.distance(intersection_series, align=True)

        object_df_validated_copy[index+"_distance"] = distance

    print(object_df_validated_copy)

    return object_df_validated_copy

# %%


object_df_validated_copy = calculate_intersections(detector_df, object_df_validated_copy)


# %% 


def assign_movement(object_df_validated_copy):

    object_df_validated_copy = object_df_validated_copy.iloc[:, 13:] # 13 or 16 very buggy and i dont know why

    object_dic = object_df_validated_copy.to_dict('index')

    for nested_dic in object_dic:

       
        calculated_movement = {k: v for k, v in object_dic[nested_dic].items() if v == v}

        sorted_calculated_movement = sorted(calculated_movement, key=calculated_movement.get)

        sorted_calculated_movement= [w.replace('_distance', '') for w in sorted_calculated_movement]

        # compare with movement dictionary

        for movement_list in movement_dict:
        
            if movement_dict[movement_list] == sorted_calculated_movement:

                print("yes")
                object_df_validated_copy.at[nested_dic,"Movement"] = movement_list
                break

    print(object_df_validated_copy)
      

    # TODO drop Nan, Sort ascending, compare if keys exist at the right index

# %%


assign_movement(object_df_validated_copy)

# %%

def safe_to_csv(process_object):
    """safe dataframe as cvs and asks for filepath

    Args:
        process_object (datafrane): dataframe with object information
    """

    autocount_csv_file = process_object.to_csv(index=True)

    file_path = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    file_path.write(autocount_csv_file)
    file_path.close


def automated_counting(flow_dic, object_dict):
    """calls previous funtions

    Args:
        detector_dict (dictionary): dictionary with detectors
        object_dict (dictionary): dictionary with obejcts (at least 3 detections)
    """

    if gui_dict["tracks_imported"] and flow_dic:
        detector_dataframe = dic_to_detector_dataframe(flow_dic)
        object_df_validated_copy = dic_to_object_dataframe(object_dict)
        processed_object = calculate_intersections(detector_dataframe,
                                                   object_df_validated_copy)

        assign_movement(flow_dic, processed_object)

        safe_to_csv(processed_object)

# %%
