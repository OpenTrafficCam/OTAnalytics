from re import MULTILINE, S
import geopandas as gpd
import geopandas.tools
from pandas.core.internals.blocks import ObjectBlock
import shapely
from shapely.geometry import Polygon, LineString,MultiLineString, multilinestring, polygon
import pandas as pd
import json
from gui_dict import *

detector_data = {
    "Detectors": {
        "dect1": {
            "type": "line",
            "start_x": 47,
            "start_y": 210,
            "end_x": 244,
            "end_y": 381,
            "color": [
                255,
                0,
                0
            ]
        },
        "dect2": {
            "type": "line",
            "start_x": 349,
            "start_y": 120,
            "end_x": 49,
            "end_y": 200,
            "color": [
                255,
                0,
                0
            ]
        },
        "dect3": {
            "type": "line",
            "start_x": 570,
            "start_y": 217,
            "end_x": 282,
            "end_y": 410,
            "color": [
                255,
                0,
                0
            ]
        },
        "dect4": {
            "type": "line",
            "start_x": 427,
            "start_y": 117,
            "end_x": 587,
            "end_y": 201,
            "color": [
                0,
                0,
                255
            ]
        }

    },
    "movements":{"test":0, "test2":15}
}


def dic_to_detector_dataframe(detector_dic):
    """creates a dataframe from detector dictionary, creates column with LineString-objects for the calculation of lineintersection with tracks

    Args:
        detector_dic (dictionary): dictionary with detectors and movements

    Returns:
        dataframe: dataframe with essential information
    """
    # change dic to dataframe
    detector_df = pd.DataFrame.from_dict({("Detectors",j): detector_dic["Detectors"][j] 
                           #for i in detector_dic.keys()
                           #only iterate thru nested dictionary of Detectors
                           for j in detector_dic["Detectors"].keys()},
                       orient='index')

    # drops first multilevel index
    detector_df.index = detector_df.index.droplevel(0) 

    # turn coordinates into LineString parameters
    detector_df["geometry"] = detector_df.apply(lambda coordinates: LineString([(coordinates['start_x'], coordinates['start_y']) , (coordinates['end_x'], coordinates['end_y'])]), axis = 1)

    return detector_df

def dic_to_object_dataframe():
    """creates a dataframe from object dictionary, creates column with Polygon-objects for the calculation of lineintersection with sections

    Args:
        object_dic (dictionary): dictionary with objects from detections

    Returns:
        dataframe: dataframe with essential information
    """
    filepath = "C:\\Users\\Goerner\\Desktop\\code\\OpenTrafficCam\\OTAnalytics\\tests\\data\\object_dic.json"

    files = open(filepath, "r")
    files = files.read()

    object_dict = json.loads(files)

    #count number of coordinates (if the count is less then 3, geopandas cant create Polygon)
    for object in object_dict:
        object_dict[object]["Coord_count"] = len(object_dict[object]["Coord"])

    object_df = pd.DataFrame.from_dict(object_dict, orient="index")


    object_df_validated = object_df.loc[object_df['Coord_count'] >= 3]

    #better copy so apply function wont give an error msg
    object_df_validated_copy = object_df_validated.copy()

    object_df_validated_copy["geometry"] = object_df_validated_copy.apply(lambda pointstuples: Polygon(pointstuples["Coord"]), axis = 1)

    return object_df_validated_copy

def calculate_intersections(detector_df, object_df_validated_copy):
    """checks if tracks and section intersect

    Args:
        detector_df (dataframe): dataframe with detectors 
        object_df_validated_copy (dataframe): copy of slice of valudated objects (at least 3 detections)

    Returns:
        dataframe: with columnheads (detectors) and boolvalue if track(row), intersected detector
    """
    #creates columns for every detector/autofill with false
    for index2, detector in detector_df.iterrows():
        object_df_validated_copy[index2] = False

    #TODO make faster
    for index1, object in object_df_validated_copy.iterrows():
        for index2, detector in detector_df.iterrows():
            s1 = gpd.GeoSeries(object_df_validated_copy.loc[index1,"geometry"])
            s2 = gpd.GeoSeries(detector_df.loc[index2,"geometry"])

            a = s1.intersects(s2)

            object_df_validated_copy.loc[index1, index2] = a[0]

    print(object_df_validated_copy)

    return object_df_validated_copy

def automated_counting(detector_data):

    if gui_dict["tracks_imported"] and detector_data:

        detector_dataframe = dic_to_detector_dataframe(detector_data)

        object_dataframe = dic_to_object_dataframe()

        processed_object = calculate_intersections(detector_dataframe,object_dataframe)

        return processed_object

automated_counting(detector_data)