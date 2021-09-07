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

# detectors = {}
# movement_dict = {}


# d = {}


# detector_dic = open(
#     "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//line_poly_move_test.OTflow",
#     "r",
# )
# object_dic = open(
#     "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//object_dic.json",
#     "r",
# )

# files = open(detector_dic.name, "r")
# files = files.read()

# flow_dic = json.loads(files)
# # use this
# detectors.update(flow_dic["Detectors"])
# movement_dict.update(flow_dic["Movements"])

# files = open(object_dic.name, "r")
# files = files.read()

# object_dic = json.loads(files)


# %%


def dic_to_detector_dataframe(detectors):
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
        {("Detectors", j): detectors[j] for j in detectors.keys()},
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

# detector_df = dic_to_detector_dataframe(detectors)
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

# object_df_validated_copy = dic_to_object_dataframe(object_dic)


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

        print(point_geometry)

        object_df_validated_copy[index + "intersectcoordinates"] = point_geometry
        object_df_validated_copy[index] = bool_intersect

    # for index, detector in detector_df.iterrows():
    #     intersection_series = gpd.GeoSeries(
    #                         object_df_validated_copy[index+"intersectcoordinates"])

    #     distance = track_start_geometry.distance(intersection_series, align=True)

    #     object_df_validated_copy[index+"_distance"] = distance

    return object_df_validated_copy


# %%
# object_df_validated_copy = calculate_intersections(
#     detector_df, object_df_validated_copy
# )


# %%


def find_intersection_order(fps, object_df_validated_copy, detectors):
    """First create necessary columns (Crossing_Gate/Frame; Movement; Movement_name)

    Second find nearest point (second nearest point) on Linestring compared
    with intersection

    third get index of that coordinate


    Args:
        object_df_validated_copy ([type]): [description]
        linedetectors ([type]): [description]

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
        for detector in detectors:
            # Condition if detector was crossed by objecttrack
            # Dont change to "is True"!!
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
                nearest, second_nearest = heapq.nsmallest(
                    2, line_points, key=intersection_point.distance
                )

                point_raw_coords = list(second_nearest.coords[0:][0])

                # unaltered coord from track file
                raw_coords = object_df_validated_copy.loc[object_id]["Coord"]

                # index at which the second closest points are
                index_number = raw_coords.index(point_raw_coords)

                # with the index number you can also get the second from gatecrossing
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
                del concatted_sorted_detector_list[1::2]

                object_df_validated_copy.at[object_id, "Time_crossing_entrace"] = (
                    object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"][0][1]
                    / fps
                )

                object_df_validated_copy.at[object_id, "Time_crossing_exit"] = (
                    object_df_validated_copy.at[object_id, "Crossing_Gate/Frame"][-1][1]
                    / fps
                )

                # list = Movement (only detectors not seconds)
                object_df_validated_copy.at[
                    object_id, "Movement"
                ] = concatted_sorted_detector_list

    return object_df_validated_copy

    # print(object_df_validated_copy)

    # if object_df_validated_copy.at[object_id, "Movement"]:

    #     object_df_validated_copy.at[object_id, "Movement"].append(detector)

    # else:
    #     object_df_validated_copy.at[object_id, "Movement"] = [detector]


# %%
# oject_df_validated_copy = find_intersection_order(
#     20, object_df_validated_copy, detectors
# )


# %%


def assign_movement(movement_dict, object_df_validated_copy):

    # object_df_intersections = object_df_validated_copy.iloc[:, 14:] # 13, 14 or 16
    # very buggy and i dont know why

    # object_dic = object_df_intersections.to_dict('index')

    # for nested_dic in
    #  object_dic:

    #     calculated_movement = {k: v for k, v in object_dic[
    #     nested_dic].items() if v == v}

    #     sorted_calculated_movement = sorted(calculated_movement,
    #     key=calculated_movement.get)

    #     sorted_calculated_movement= [w.replace(
    #     '_distance', '') for w in sorted_calculated_movement]

    #     # compare with movement dictionary

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
# object_df_validated_copy = assign_movement(movement_dict, object_df_validated_copy)


# %%
# def hash_crossing_second(
# object_df_validated_copy):
#     object_df_validated_copy[
#     "Second_crossing_entrace"] = object_df_validated_copy.apply(
#         lambda entrance_second:entrance_second['Crossing_Gate/Frame'])

#     #object_df_validated_copy["Second_crossing_exit"]

#     return object_df_validated_copy


# %%

# object_df_validated_copy = hash_crossing_second(object_df_validated_copy)

# print(object_df_validated_copy)


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
# %%


def automated_counting(fps, movement_dict, linedetectors_dict, object_dict):
    """calls previous funtions

    Args:
        detector_dict (dictionary): dictionary with detectors
        object_dict (dictionary): dictionary with obejcts (at least 3 detections)
    """

    if gui_dict["tracks_imported"] and linedetectors_dict and movement_dict:
        detector_dataframe = dic_to_detector_dataframe(linedetectors_dict)
        object_df_validated_copy = dic_to_object_dataframe(object_dict)
        processed_object = calculate_intersections(
            detector_dataframe, object_df_validated_copy
        )

        # TODO doesnt return right dataframe

        processed_object = find_intersection_order(
            fps, object_df_validated_copy, linedetectors_dict
        )
        processed_object = assign_movement(movement_dict, processed_object)

        safe_to_csv(processed_object)


# %%
