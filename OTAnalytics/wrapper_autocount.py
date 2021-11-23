import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon
import pandas as pd
from tkinter import filedialog
import json
import heapq
import numpy as np


# dictionary for detectors and movements


def load_tracks(object_dic, raw_detections, class_dic):
    """loads detectors from a .Track-File and converts into displayable format"""

    filepath = (
        "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/test-data/"
        + "input/radeberg_trackfile-px.ottrk"
    )
    files = open(filepath, "r")
    files = files.read()

    track_file = json.loads(files)

    # detections = {}

    # TODO shorten
    raw_detections.update(track_file["data"])

    for frame in raw_detections:
        for detection in raw_detections[frame]:
            if "object_" + str(detection) in object_dic.keys():
                object_dic["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"],
                        raw_detections[frame][detection]["y"],
                    ]
                )

                object_dic["object_%s" % detection]["Frame"].append(int(frame))

            elif raw_detections[frame][detection]["class"] in class_dic.keys():
                object_dic["object_%s" % detection] = {}
                object_dic["object_%s" % detection]["Coord"] = []
                object_dic["object_%s" % detection]["Frame"] = [int(frame)]
                object_dic["object_%s" % detection]["Class"] = raw_detections[frame][
                    detection
                ]["class"]
                object_dic["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"],
                        raw_detections[frame][detection]["y"],
                    ]
                )

    return object_dic


def dic_to_detector_dataframe(detectors_dic):
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
        {("Detectors", j): detectors_dic[j] for j in detectors_dic.keys()},
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
        object_dic[object]["first_appearance_frame"] = object_dic[object]["Frame"][0]
        object_dic[object]["last_appearance_frame"] = object_dic[object]["Frame"][-1]

    object_df = pd.DataFrame.from_dict(object_dic, orient="index")

    object_df_validated = object_df.loc[object_df["Coord_count"] >= 2]

    # better copy so apply function wont give an error msg/ is copy
    # because coord_count is filtered
    object_df_validated_copy = object_df_validated.copy()

    object_df_validated_copy["geometry"] = object_df_validated_copy.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1
    )

    # not necessary afer restructuring code
    # object_df_validated_copy["start_point_geometry"] = object_df_validated_copy.apply(
    #     lambda pointtuples: Point(pointtuples["Coord"][0]), axis=1)

    return object_df_validated_copy


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


def find_intersection_order(object_df_validated_copy, detector_dict, fps=25):
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
            if object_df_validated_copy.loc[object_id][detector]:

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


def assign_movement(movement_dict, object_df_validated_copy):
    """Compares movements and associated detectors with sorted crossing list

    Args:
        movement_dict ([dictionary]): dictionary with movements
        object_df_validated_copy ([dataframe]): validated object dataframe

    Returns:
        object_df_validated_copy ([dataframe]):
        validated object dataframe with movements
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


def time_calculation_dataframe(fps, object_validated_df):

    object_validated_df["first_appearance_time"] = pd.to_datetime(
        (object_validated_df["first_appearance_frame"] / fps), unit="s"
    )
    object_validated_df["last_appearance_time"] = pd.to_datetime(
        (object_validated_df["last_appearance_frame"] / fps), unit="s"
    )

    object_validated_df["first_appearance_time"] = object_validated_df[
        "first_appearance_time"
    ].dt.strftime("%H:%M:%S")

    object_validated_df["last_appearance_time"] = object_validated_df[
        "last_appearance_time"
    ].dt.strftime("%H:%M:%S")

    return object_validated_df


def clean_dataframe(object_validated_df):
    """deletes unnecessary columns

    Args:
        object_validated_df (dataframe): dataframe of validated object tracking

    Returns:
        dataframe: returns cleaned dataframe

    """

    # TODO List to Tuple Movement
    object_validated_df["Movement"] = object_validated_df["Movement"].apply(str)

    print(object_validated_df)

    return object_validated_df.loc[
        :,
        [
            "Class",
            "Movement",
            "Movement_name",
            "first_appearance_frame",
            "first_appearance_time",
            "last_appearance_frame",
            "last_appearance_time",
            "Time_crossing_entrace",
            "Time_crossing_exit",
        ],
    ]


def resample_dataframe(object_validated_df):

    object_validated_df["Datetime"] = pd.to_datetime(
        object_validated_df["first_appearance_time"]
    )

    object_validated_df = object_validated_df.set_index("Datetime")

    object_validated_df = object_validated_df.replace(r"^\s*$", np.nan, regex=True)

    print(object_validated_df)

    object_validated_df = (
        object_validated_df.groupby(
            by=[pd.Grouper(freq="5T"), "Class", "Movement", "Movement_name"],
            dropna=False,
        )
        .size()
        .reset_index(name="counts")
    )

    return object_validated_df


def safe_to_exl(process_object):
    """safe dataframe as cvs and asks for filepath

    Args:
        process_object (datafrane): dataframe with object information
    """

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
    )
    process_object.to_excel(file_path)


def main():
    """Main function."""
    detectors_dic = {}
    movement_dic = {}
    object_dic = {}
    raw_detection = {}

    class_dic = {
        "car": (89, 101, 212),
        "bicycle": (73, 166, 91),
        "truck": (97, 198, 212),
        "motorcycle": (148, 52, 137),
        "person": (214, 107, 88),
        "bus": (179, 177, 68),
    }

    # open .OTflow

    flow_dic = open(
        "C:/Users/Goerner/Desktop/code/OpenTrafficCam/"
        + "OTAnalytics/tests/test-data/input/"
        + "radeberg_sectionfile-px.OTflow",
        "r",
    )

    files = open(flow_dic.name, "r")
    files = files.read()

    flow_dic = json.loads(files)

    detectors_dic.update(flow_dic["Detectors"])
    movement_dic.update(flow_dic["Movements"])

    # open object json

    # create objects from trackfile ottrk
    object_dic = load_tracks(object_dic, raw_detection, class_dic)

    detector_df = dic_to_detector_dataframe(detectors_dic)

    object_df_validated_copy = dic_to_object_dataframe(object_dic)

    object_df_validated_copy = calculate_intersections(
        detector_df, object_df_validated_copy
    )

    object_df_validated_copy = find_intersection_order(
        object_df_validated_copy, detectors_dic, fps=25
    )

    object_df_validated_copy = assign_movement(movement_dic, object_df_validated_copy)

    object_df_validated_copy = time_calculation_dataframe(25, object_df_validated_copy)

    object_df_validated_copy = clean_dataframe(object_df_validated_copy)

    object_df_validated_copy = resample_dataframe(object_df_validated_copy)

    safe_to_exl(object_df_validated_copy)


if __name__ == "__main__":
    main()
