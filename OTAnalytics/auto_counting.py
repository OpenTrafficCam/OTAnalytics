import heapq
from tkinter import Button, Entry, Label, Toplevel, filedialog

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point, Polygon


def dic_to_detector_dataframe(detectors_dict):
    """Creates a dataframe from detector/flow dictionary, # TODO change to use
    linedetector dic that gets updated when importing flow data
    creates column with LineString-objects for the calculation of
    lineintersection with tracks.

    Args:
        detector_dic (dictionary): dictionary with detectors and movements, detector
        dictionary represents first key of flow dictioniary

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


def dic_to_object_dataframe(object_dic):
    """Creates a dataframe from object dictionary, creates column with Polygon-objects.

    Args:
        object_dict (dictionary): dictionary with information of object

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

    # better copy so apply function wont give an error msg/ is copy because coord_count
    # is filtered
    object_df_validated_copy = object_df_validated.copy()

    object_df_validated_copy["geometry"] = object_df_validated_copy.apply(
        lambda pointtuples: LineString(pointtuples["Coord"]), axis=1
    )

    # not necessary afer restructuring code
    # object_df_validated_copy["start_point_geometry"] = object_df_validated_copy.apply(
    #     lambda pointtuples: Point(pointtuples["Coord"][0]), axis=1)

    return object_df_validated_copy


# %%
def calculate_intersections(detector_df, object_validated_df):
    """Checks if tracks and detectors intersect, alters object_dataframe.

    Args:
        detector_df (dataframe): dataframe with detectors
        object_validated_df (dataframe): copy of slice of valudated objects
        (at least 3 detections)

    Returns:
        dataframe: with columnheads (detectors) and boolvalue if track(row),
        intersected detector (intersections are not ordered)
    """
    # creates a geoseries from column(geometry) with shapely object

    track_geometry = gpd.GeoSeries(object_validated_df.geometry)

    # track_start_geometry = gpd.GeoSeries(
    # object_validated_df.start_point_geometry)

    # iterates over every detectors and returns bool value for
    # intersection with every track from geoseries
    for index, detector in detector_df.iterrows():

        # distinct shapely geometry from geometry column
        detector_shapely_geometry = detector.geometry

        # columnwise comparison
        bool_intersect = track_geometry.intersects(detector_shapely_geometry)

        # returns coordinates from intersections as point object
        point_geometry = track_geometry.intersection(detector_shapely_geometry)

        object_validated_df[index + "intersectcoordinates"] = point_geometry
        object_validated_df[index] = bool_intersect

    # for index, detector in detector_df.iterrows():
    #     intersection_series = gpd.GeoSeries(
    #                         object_validated_df[index+"intersectcoordinates"])

    #     distance = track_start_geometry.distance(intersection_series, align=True)

    #     object_validated_df[index+"_distance"] = distance

    return object_validated_df


def find_intersection_order(fps, object_validated_df, detector_dict):
    """First create necessary columns (Crossing_Gate/Frame; Movement; Movement_name).

    Second find nearest point (second nearest point) on Linestring compared
    with intersection.

    Third get index of that coordinate and compare order.


    Args:
        object_validated_df (dataframe): Objectdataframe
        detector_dict (dictionary): dictionary with detectors
    Returns:
        Dataframe: With newly calculated columns
    """

    # create necessary columns
    object_validated_df["Crossing_Gate/Frame"] = ""
    object_validated_df["Movement"] = ""
    object_validated_df["Movement_name"] = ""
    object_validated_df["Time_crossing_entrace"] = ""
    object_validated_df["Time_crossing_exit"] = ""

    for object_id, row in object_validated_df.iterrows():
        # use dict
        for detector in detector_dict:
            # Condition if detector was crossed by objecttrack
            # Dont change to "is True"!! (True is the content of row/column)
            if object_validated_df.loc[object_id][detector] == True:

                # shapely Linestring
                track_line = object_validated_df.loc[object_id]["geometry"]

                # shapely Point from intersection
                intersection_point = object_validated_df.loc[object_id][
                    detector + "intersectcoordinates"
                ]

                line_points = map(Point, track_line.coords)

                # get second nearest point(
                # second nearest point = coordinate on linestring)
                # first point is intersection
                # nearest point is crossing on detector/ second nearest is track coord
                nearest, second_nearest = heapq.nsmallest(
                    2, line_points, key=intersection_point.distance
                )

                point_raw_coords = list(second_nearest.coords[0:][0])

                # unaltered coord from track file
                raw_coords = object_validated_df.loc[object_id]["Coord"]

                # index at which the second closest points are
                index_number = raw_coords.index(point_raw_coords)

                # with the index number you can also get the frame from gatecrossing
                crossing_frame = object_validated_df.loc[object_id]["Frame"][
                    index_number
                ]

                # find all gatecrossing detector and their crossing seconds
                if object_validated_df.at[object_id, "Crossing_Gate/Frame"]:
                    object_validated_df.at[object_id, "Crossing_Gate/Frame"].append(
                        [detector, crossing_frame]
                    )

                else:
                    object_validated_df.at[object_id, "Crossing_Gate/Frame"] = [
                        [detector, crossing_frame]
                    ]

                # sort list by seconds (first index also determines
                # which detector was crossed first)
                object_validated_df.at[object_id, "Crossing_Gate/Frame"] = sorted(
                    object_validated_df.at[object_id, "Crossing_Gate/Frame"],
                    key=lambda x: x[1],
                )

                t = object_validated_df.loc[object_id]["Crossing_Gate/Frame"]

                # concattes new list and delete seconds
                concatted_sorted_detector_list = [
                    item for sublist in t for item in sublist
                ]
                # deletes extra brackets (list)
                del concatted_sorted_detector_list[1::2]

                object_validated_df.at[object_id, "Time_crossing_entrace"] = (
                    object_validated_df.at[object_id, "Crossing_Gate/Frame"][0][1] / fps
                )

                if object_validated_df.at[object_id, "Time_crossing_entrace"] != (
                    object_validated_df.at[object_id, "Crossing_Gate/Frame"][-1][1]
                    / fps
                ):

                    object_validated_df.at[object_id, "Time_crossing_exit"] = (
                        object_validated_df.at[object_id, "Crossing_Gate/Frame"][-1][1]
                        / fps
                    )

                # list = Movement (only detectors not seconds)
                object_validated_df.at[
                    object_id, "Movement"
                ] = concatted_sorted_detector_list

    return object_validated_df


# %%


# %%


def assign_movement(movement_dict, object_validated_df):
    """Compares movements and associated detectors with sorted crossing list.

    Args:
        movement_dict ([dictionary]): dictionary with movements
        object_validated_df ([dataframe]): validated object dataframe

    Returns:
        object_validated_df ([dataframe]): validated object dataframe with movements
    """

    for object_id, j in object_validated_df.iterrows():

        print("working...on " + str(object_id))

        for movement_list in movement_dict:

            # if detector in movements and real movement crossing events are true,
            #  key of movement dictionary is value of cell
            if (
                movement_dict[movement_list]
                == object_validated_df.loc[object_id]["Movement"]
            ):

                print("yes")
                object_validated_df.at[object_id, "Movement_name"] = movement_list
                break

    return object_validated_df


# %%


# %%
def safe_to_exl(process_object):
    """Safe dataframe as cvs and asks for filepath.

    Args:
        process_object (datafrane): dataframe with object information
    """

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
    )
    process_object.to_excel(file_path)
    # file_path.write(autocount_csv_file)
    # file_path.close


# %%
def time_calculation_dataframe(timedelta_entry, fps, object_validated_df):

    entry_timedelta = timedelta_entry.get()

    # time_list = entry_timedelta.split(":", 3)

    # hour, min, second = time_list

    # print(hour, min, second)

    # print(entry_timedelta)

    object_validated_df["first_appearance_time"] = pd.to_datetime(
        (object_validated_df["first_appearance_frame"] / fps), unit="s"
    ) + pd.Timedelta(entry_timedelta)
    object_validated_df["last_appearance_time"] = pd.to_datetime(
        (object_validated_df["last_appearance_frame"] / fps), unit="s"
    ) + pd.Timedelta(entry_timedelta)

    object_validated_df["first_appearance_time"] = object_validated_df[
        "first_appearance_time"
    ].dt.strftime("%H:%M:%S")

    object_validated_df["last_appearance_time"] = object_validated_df[
        "last_appearance_time"
    ].dt.strftime("%H:%M:%S")

    return object_validated_df


def clean_dataframe(object_validated_df):
    """Deletes unnecessary columns.

    Args:
        object_validated_df (dataframe): dataframe of validated object tracking

    Returns:
        dataframe: returns cleaned dataframe
    """
    # List hast to be tuple or string in order to be groupby
    object_validated_df["Movement"] = object_validated_df["Movement"].apply(str)

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


def resample_dataframe(entry_intervall, object_validated_df):
    """Groups and timeresamples dataframe.

    Args:
        entry_intervall (integer): timeinterval in which grouped data is summed up
        object_validated_df (dataframe): Dataframe

    Returns:
        dataframe: Returns grouped and resampled dataframe
    """
    entry_intervall_time = str(entry_intervall.get())

    if entry_intervall_time not in ["0", "None"]:

        object_validated_df["Datetime"] = pd.to_datetime(
            object_validated_df["first_appearance_time"]
        )

        object_validated_df = object_validated_df.set_index("Datetime")

        object_validated_df = (
            object_validated_df.groupby(
                by=[
                    pd.Grouper(freq=str(entry_intervall_time) + "T"),
                    "Class",
                    "Movement",
                    "Movement_name",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="counts")
        )

        object_validated_df["Datetime"] = object_validated_df["Datetime"].dt.strftime(
            "%H:%M:%S"
        )

    return object_validated_df


def automated_counting(
    entry_timedelta, entry_intervall, fps, movement_dic, detector_dic, object_dic
):
    """Calls previous funtions for better readability.

    Args:
        detector_dict (dictionary): dictionary with detectors
        object_dict (dictionary): dictionary with objects (at least 3 detections)

    """

    # if gui_dict["tracks_imported"] and detector_dic and movement_dic:
    detector_dataframe = dic_to_detector_dataframe(detector_dic)
    object_validated_df = dic_to_object_dataframe(object_dic)
    processed_object = calculate_intersections(detector_dataframe, object_validated_df)

    print("succesfull")

    # TODO doesnt return right dataframe

    processed_object = find_intersection_order(fps, processed_object, detector_dic)
    processed_object = assign_movement(movement_dic, processed_object)

    processed_object = time_calculation_dataframe(
        entry_timedelta, fps, processed_object
    )

    cleaned_object_dataframe = clean_dataframe(processed_object)

    cleaned_resampled_object_df = resample_dataframe(
        entry_intervall, cleaned_object_dataframe
    )

    safe_to_exl(cleaned_resampled_object_df)

    return cleaned_resampled_object_df


def create_setting_window(fps, movement_dic, detector_dic, object_dic):
    """Creates window with button to resample dataframe and two
    inputfields to enter starting time and timeintervall.

    Args:
        fps (int): Videoframes per seconds
        movement_dic (dictionary): dictionary with movements
        detector_dic (dictionary): dictionary with detectors
        object_dic (dictionary): dictionary with objects
    """
    # creates window to insert autocount time and groupby time
    toplevelwindow = Toplevel()

    toplevelwindow.title("Settings for autocount")

    time_entry_header = Label(toplevelwindow, text="Record start time")
    time_entry_header.grid(row=0, column=0, columnspan=5, sticky="w")

    time_entry = Entry(toplevelwindow, width=8)

    time_entry.grid(row=1, column=0, sticky="w", pady=5, padx=5)
    time_entry.focus()
    time_entry.insert(0, "00:00:00")

    timeintervall_entry_header = Label(toplevelwindow, text="Timeintervall (min)")
    timeintervall_entry_header.grid(row=2, column=0, columnspan=5, sticky="w")

    timeintervall_entry = Entry(toplevelwindow, width=8)
    timeintervall_entry.grid(row=3, column=0, sticky="w", pady=5, padx=5)
    timeintervall_entry.insert(0, "None")

    toplevelwindow_button = Button(
        toplevelwindow,
        text="Save file",
        command=lambda: automated_counting(
            time_entry, timeintervall_entry, fps, movement_dic, detector_dic, object_dic
        ),
    )
    toplevelwindow_button.grid(
        row=4, columnspan=5, column=0, sticky="w", pady=5, padx=5
    )

    toplevelwindow.protocol("WM_DELETE_WINDOW")
    # makes the background window unavailable
    toplevelwindow.grab_set()
