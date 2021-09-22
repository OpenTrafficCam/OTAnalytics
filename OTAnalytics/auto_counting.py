# %%

import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon
import pandas as pd
from gui_dict import gui_dict
from tkinter import filedialog
import json
import heapq


# TODO: check if tracks and crossed sections belong to certain movement

# %%

detectors_dic = {}
movement_dic = {}


d = {}


detector_dic = open(
    "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//multiple_line_detectors.OTflow",
    "r",
)
object_dic = open(
    "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//object_dic.json",
    "r",
)

files = open(detector_dic.name, "r")
files = files.read()

flow_dic = json.loads(files)
# use this
detectors_dic.update(flow_dic["Detectors"])
movement_dic.update(flow_dic["Movements"])


files = open(object_dic.name, "r")
files = files.read()

object_dic = json.loads(files)

# print(object_dic)
# print(detectors)


# %%


def dic_to_detector_dataframe(detectors_dict):
    """creates a dataframe from detector/flow dictionary, # TODO change to use
    linedetector dic that gets updated when importing flow data
    creates column with LineString-objects for the calculation of
    lineintersection with tracks

    Args:
        detector_dic (dictionary): dictionary with detectors and movements

    Returns:
        dataframe: dataframe with essential information
    """
    # change dic to dataframe
    detector_df = pd.DataFrame.from_dict(
        {("Detectors", j): detectors_dict[j] for j in detectors_dict.keys()},
        orient="index",
    )

    # drops first multilevel index
    detector_df.index = detector_df.index.droplevel(0)

    # turn coordinates into LineString parameters
    detector_df["geometry"] = detector_df.apply(
        lambda coordinates: LineString(
            [
                (coordinates["start_x"], coordinates["start_y"]),
                (coordinates["end_x"], coordinates["end_y"]),
            ]
        )
        if coordinates["type"] == "line"
        else Polygon(coordinates["points"]),
        axis=1,
    )

    return detector_df


# %%

detector_df = dic_to_detector_dataframe(detectors_dic)
# print(detector_df)

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

    object_df_validated = object_df.loc[object_df["Coord_count"] >= 3]

    # better copy so apply function wont give an error msg
    object_df_validated_copy = object_df_validated.copy()

    object_df_validated_copy["geometry"] = object_df_validated_copy.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1
    )

    # not necessary afer restructuring code
    # object_df_validated_copy["start_point_geometry"] = object_df_validated_copy.apply(
    #     lambda pointtuples: Point(pointtuples["Coord"][0]), axis=1)

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
        intersected detector (intersections are not ordered)
    """
    # creates a geoseries from column(geometry) with shapely object

    track_geometry = gpd.GeoSeries(object_df_validated_copy.geometry)

    # track_start_geometry = gpd.GeoSeries(
    # object_df_validated_copy.start_point_geometry)

    # iterates over every detectors and returns bool value for
    # intersection with every track from geoseries
    for index, detector in detector_df.iterrows():

        # distinct shapely geometry
        detector_shapely_geometry = detector.geometry

        # columnwise comparison
        bool_intersect = track_geometry.intersects(detector_shapely_geometry)

        # returns coordinates from intersections as point object
        point_geometry = track_geometry.intersection(detector_shapely_geometry)

        object_df_validated_copy[index + "intersectcoordinates"] = point_geometry
        object_df_validated_copy[index] = bool_intersect

    # for index, detector in detector_df.iterrows():
    #     intersection_series = gpd.GeoSeries(
    #                         object_df_validated_copy[index+"intersectcoordinates"])

    #     distance = track_start_geometry.distance(intersection_series, align=True)

    #     object_df_validated_copy[index+"_distance"] = distance

    return object_df_validated_copy


# %%
object_df_validated_copy = calculate_intersections(
    detector_df, object_df_validated_copy
)


# %%


def find_intersection_order(fps, object_df_validated_copy, detector_dict):
    """First create necessary columns (Crossing_Gate/Frame; Movement; Movement_name)

    Second find nearest point (second nearest point) on Linestring compared
    with intersection

    third get index of that coordinate


    Args:
        object_df_validated_copy ([type]): dataframe
        linedetectors ([type]): dictionary
    Returns:
        [type]: [description]
    """

    # create necessary columns
    object_df_validated_copy["Crossing_Gate/Frame"] = ""
    object_df_validated_copy["Movement"] = ""
    object_df_validated_copy["Movement_name"] = ""
    object_df_validated_copy["Time_crossing_entrace"] = ""
    object_df_validated_copy["Time_crossing_exit"] = ""

    for object_id, row in object_df_validated_copy.iterrows():
        # use dict
        for detector in detector_dict:
            #         # Condition if detector was crossed by objecttrack
            #         # Dont change to "is True"!!
            if object_df_validated_copy.loc[object_id][detector] == True:

                # shapely Linestring
                track_line = object_df_validated_copy.loc[object_id]["geometry"]

                # shapely Point from intersection
                intersection_point = object_df_validated_copy.loc[object_id][
                    detector + "intersectcoordinates"
                ]

                line_points = map(Point, track_line.coords)

                # get second nearest point(
                # second nearest point = coordinate on linestring)
                # nearest point is crossing on detector/ second nearest is track coord
                nearest, second_nearest = heapq.nsmallest(
                    2, line_points, key=intersection_point.distance
                )

                point_raw_coords = list(second_nearest.coords[0:][0])

                # unaltered coord from track file
                raw_coords = object_df_validated_copy.loc[object_id]["Coord"]

                # index at which the second closest points are
                index_number = raw_coords.index(point_raw_coords)

                # with the index number you can also get the frame from gatecrossing
                crossing_frame = object_df_validated_copy.loc[object_id]["Frame"][
                    index_number
                ]

                # find all gatecrossing detector and their crossing seconds
                if object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"]:
                    object_df_validated_copy.at[
                        object_id, "Crossing_Gate/Frame"
                    ].append([detector, crossing_frame])

                else:
                    object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"] = [
                        [detector, crossing_frame]
                    ]

                # sort list by seconds (first index also determines
                # which detector was crossed first)
                object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"] = sorted(
                    object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"],
                    key=lambda x: x[1],
                )

                t = object_df_validated_copy.loc[object_id]["Crossing_Gate/Frame"]

                # concattes new list and delete seconds
                concatted_sorted_detector_list = [
                    item for sublist in t for item in sublist
                ]
                # deletes extra brackets (list)
                del concatted_sorted_detector_list[1::2]

                object_df_validated_copy.at[object_id, "Time_crossing_entrace"] = (
                    object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"][0][1]
                    / fps
                )

                if object_df_validated_copy.at[object_id, "Time_crossing_entrace"] != (
                    object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"][-1][1]
                    / fps
                ):

                    object_df_validated_copy.at[object_id, "Time_crossing_exit"] = (
                        object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"][
                            -1
                        ][1]
                        / fps
                    )

                # list = Movement (only detectors not seconds)
                object_df_validated_copy.at[
                    object_id, "Movement"
                ] = concatted_sorted_detector_list

    return object_df_validated_copy


# %%
object_df_validated_copy = find_intersection_order(
    20, object_df_validated_copy, detectors_dic
)


# %%


def assign_movement(movement_dict, object_df_validated_copy):
    """Compares movements and associated detectors with sorted crossing list

    Args:
        movement_dict ([dictionary]): dictionary with movements
        object_df_validated_copy ([dataframe]): validated object dataframe

    Returns:
        object_df_validated_copy ([dataframe]): validated object dataframe with movements
    """

    for object_id, j in object_df_validated_copy.iterrows():

        for movement_list in movement_dict:

            # if detector in movements and real movement crossing events are true,
            #  key of movement dictionary is value of cell
            if (
                movement_dict[movement_list]
                == object_df_validated_copy.loc[object_id]["Movement"]
            ):

                print("yes")
                object_df_validated_copy.at[object_id, "Movement_name"] = movement_list
                break

    return object_df_validated_copy


# %%
object_df_validated_copy = assign_movement(movement_dic, object_df_validated_copy)

# %%
def safe_to_csv(process_object):
    """safe dataframe as cvs and asks for filepath

    Args:
        process_object (datafrane): dataframe with object information
    """

    autocount_csv_file = process_object.to_csv(index=True)

    file_path = filedialog.asksaveasfile(mode="w", defaultextension=".csv")
    file_path.write(autocount_csv_file)
    file_path.close


# %%


def clean_dataframe(object_df_validated_copy):

    cleaned_automated_counting = object_df_validated_copy.loc[
        :,
        [
            "Class",
            "Movement",
            "Movement_name",
            "Time_crossing_entrace",
            "Time_crossing_exit",
        ],
    ]

    return cleaned_automated_counting


# %%


def automated_counting(fps, movement_dic, detector_dic, object_dic):
    """calls previous funtions

    Args:
        detector_dict (dictionary): dictionary with detectors
        object_dict (dictionary): dictionary with obejcts (at least 3 detections)

    """

    # if gui_dict["tracks_imported"] and detector_dic and movement_dic:
    detector_dataframe = dic_to_detector_dataframe(detector_dic)
    object_df_validated_copy = dic_to_object_dataframe(object_dic)
    processed_object = calculate_intersections(
        detector_dataframe, object_df_validated_copy
    )

    print("succesfull")

    # TODO doesnt return right dataframe

    processed_object = find_intersection_order(fps, processed_object, detector_dic)
    processed_object = assign_movement(movement_dic, processed_object)
    cleaned_object_dataframe = clean_dataframe(processed_object)

    safe_to_csv(cleaned_object_dataframe)

    return cleaned_object_dataframe


# %%

# cleaned_object_dataframe = automated_counting(
#     25, movement_dic, detectors_dic, object_dic
# )

# print(cleaned_object_dataframe)


# %%
