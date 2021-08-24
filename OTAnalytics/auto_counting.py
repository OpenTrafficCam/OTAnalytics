import geopandas as gpd
from shapely.geometry import LineString
import pandas as pd
from gui_dict import gui_dict
from tkinter import filedialog

# TODO: check if tracks and crossed sections belong to certain movement


def dic_to_detector_dataframe(detector_dic):
    """creates a dataframe from detector dictionary,
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
         detector_dic["Detectors"][j]for j in
         detector_dic["Detectors"].keys()}, orient='index')

    # drops first multilevel index
    detector_df.index = detector_df.index.droplevel(0)

    # turn coordinates into LineString parameters
    detector_df["geometry"] = detector_df.apply(
        lambda coordinates:
        LineString([(coordinates['start_x'], coordinates['start_y']),
                    (coordinates['end_x'], coordinates['end_y'])]), axis=1)

    return detector_df


def dic_to_object_dataframe(object_dict):
    """creates a dataframe from object dictionary, creates column with Polygon-objects.
    Args:
        object_dict ([dictionary]): dictionary with information of object

    Returns:
        dataframe: dictionary with information of object
    """

    # count number of coordinates (if the count is less then 3,
    # geopandas cant create Polygon)
    for object in object_dict:
        object_dict[object]["Coord_count"] = len(object_dict[object]["Coord"])

    object_df = pd.DataFrame.from_dict(object_dict, orient="index")

    object_df_validated = object_df.loc[object_df['Coord_count'] >= 3]

    # better copy so apply function wont give an error msg
    object_df_validated_copy = object_df_validated.copy()

    object_df_validated_copy["geometry"] = object_df_validated_copy.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1)

    return object_df_validated_copy


def calculate_intersections(detector_df, object_df_validated_copy):
    """checks if tracks and section intersect

    Args:
        detector_df (dataframe): dataframe with detectors
        object_df_validated_copy (dataframe): copy of slice of valudated objects
        (at least 3 detections)

    Returns:
        dataframe: with columnheads (detectors) and boolvalue if track(row),
        intersected detector
    """
    # creates a geoseries from column(geometry) with shapely obeject
    track_geometry = gpd.GeoSeries(object_df_validated_copy.geometry)

    # iterrates over every detectors and returns bool value for
    # intersection with every track from geoseries
    for index2, detector in detector_df.iterrows():

        # distinct shapely geometry
        detector_shapely_geometry = detector.geometry

        bool_intersect = track_geometry.intersects(detector_shapely_geometry)

        object_df_validated_copy[index2] = bool_intersect

    return object_df_validated_copy


def safe_to_csv(process_object):
    """safe dataframe as cvs and asks for filepath

    Args:
        process_object (datafrane): dataframe with object information
    """

    autocount_csv_file = process_object.to_csv(index=True)

    file_path = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    file_path.write(autocount_csv_file)
    file_path.close


def automated_counting(detector_dict, object_dict):
    """calls previous funtions

    Args:
        detector_dict (dictionary): dictionary with detectors
        object_dict (dictionary): dictionary with obejcts (at least 3 detections)
    """

    if gui_dict["tracks_imported"] and detector_dict:
        detector_dataframe = dic_to_detector_dataframe(detector_dict)
        object_dataframe = dic_to_object_dataframe(object_dict)
        processed_object = calculate_intersections(detector_dataframe, object_dataframe)

        safe_to_csv(processed_object)
