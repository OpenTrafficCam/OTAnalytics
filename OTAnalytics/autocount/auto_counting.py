import heapq
from tkinter import Button, Entry, Label, Toplevel, filedialog

import geopandas as gpd
import itertools
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import helpers.file_helper as file_helper
import view.objectstorage
from view.helpers.gui_helper import info_message
from view.helpers.gui_helper import button_bool


def dic_to_detector_dataframe():
    """Creates a dataframe from detector/flow dictionary, #TODO change to use
    linedetector dic that gets updated when importing flow data
    creates column with LineString-objects for the calculation of
    lineintersection with tracks.

    Args:
        flowdictionary (dictionary): Dictionary with sections and movements.

    Returns:
        detector_df: Dataframe with sections.
    """
    # change dic to dataframe
    detector_df = pd.DataFrame.from_dict(
        {
            ("Detectors", j): file_helper.flow_dict["Detectors"][j]
            for j in file_helper.flow_dict["Detectors"].keys()
        },
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
def calculate_intersections(detector_df, tracks_df):
    """Checks if tracks and detectors intersect, alters object_dataframe.

    Args:
        detector_df (dataframe): dataframe with detectors
        object_validated_df (dataframe): copy of slice of valuedated objects
        (at least 3 detections)

    Returns:
        dataframe: with columnheads (detectors) and boolvalue if track(row),
        intersected detector (intersections are not ordered)
    """
    # creates a geoseries from column(geometry) with shapely object

    track_geometry = gpd.GeoSeries(tracks_df.geometry)

    # iterates over every detectors and returns bool value for
    # intersection with every track from geoseries
    for index, detector in detector_df.iterrows():

        # distinct shapely geometry from geometry column
        detector_shapely_geometry = detector.geometry

        # columnwise comparison
        bool_intersect = track_geometry.intersects(detector_shapely_geometry)

        # returns coordinates from intersections as point object
        point_geometry = track_geometry.intersection(detector_shapely_geometry)

        tracks_df[f"{index}intersectcoordinates"] = point_geometry
        tracks_df[index] = bool_intersect



    return tracks_df


def find_intersection_order(track_df):
    """First create necessary columns (Crossing_Gate/Frame; Movement; Movement_name).

    Second find nearest point (second nearest point) on Linestring compared
    with intersection.

    Third get index of that coordinate and compare order.


    Args:
        object_validated_df (dataframe): Tracks with at least two coordinates.
        detector_dict (dictionary): Dictionary with detectors.
    Returns:
        Dataframe: With newly calculated columns.
    """

    eventbased_dictionary = {}

    # create necessary columns
    track_df["Crossing_Gate/Frame"] = ""
    track_df["Crossed_Section"] = ""
    track_df["Movement_name"] = ""
    track_df["Time_crossing_entrance"] = ""
    track_df["Time_crossing_exit"] = ""

    #ID for event
    i=0

    for (object_id, row), detector in itertools.product(
        track_df.iterrows(), file_helper.flow_dict["Detectors"]
    ):
        # Condition if detector was crossed by objecttrack
        # Don't change to "is True"!! (True is the content of row/column)
        # TODO: Vorfiltern des Dataframe (wo Detector ==> True), dafür loops aufsplitten
        if track_df.loc[object_id][detector]:
            i+=1

            # shapely Linestring
            track_line = track_df.loc[object_id]["geometry"]

            # shapely Point from intersection
            intersection_point = track_df.loc[object_id][
                f"{detector}intersectcoordinates"
            ]

            line_points = map(Point, track_line.coords)

            # get second nearest point(
            # second nearest point = coordinate on linestring)
            # first point is intersection
            # nearest point is crossing on detector/ second nearest is track coord
            nearest, second_nearest = heapq.nsmallest(
                2, line_points, key=intersection_point.distance
            )

            point_raw_coords = list(second_nearest.coords[:][0])


            # unaltered coord from track file
            raw_coords = track_df.loc[object_id]["Coord"]

            # index at which the second closest points are
            index_number = raw_coords.index(point_raw_coords)

            # with the index number you can also get the frame from gatecrossing
            crossing_frame = track_df.loc[object_id]["Frame"][index_number]

            # find all gatecrossing detector and their crossing seconds
            if track_df.at[object_id, "Crossing_Gate/Frame"]:
                track_df.at[object_id, "Crossing_Gate/Frame"].append(
                    [detector, crossing_frame]
                )

            else:
                track_df.at[object_id, "Crossing_Gate/Frame"] = [
                    [detector, crossing_frame]
                ]

            # sort list by seconds (first index also determines
            # which detector was crossed first)
            track_df.at[object_id, "Crossing_Gate/Frame"] = sorted(
                track_df.at[object_id, "Crossing_Gate/Frame"],
                key=lambda x: x[1],
            )

            t = track_df.loc[object_id]["Crossing_Gate/Frame"]

            # concates new list and delete seconds
            concatted_sorted_detector_list = [item for sublist in t for item in sublist]
            # deletes extra brackets (list)
            del concatted_sorted_detector_list[1::2]

            track_df.at[object_id, "Time_crossing_entrance"] = (
                track_df.at[object_id, "Crossing_Gate/Frame"][0][1]
                / view.objectstorage.videoobject.fps
            )

            if track_df.at[object_id, "Time_crossing_entrance"] != (
                track_df.at[object_id, "Crossing_Gate/Frame"][-1][1]
                / view.objectstorage.videoobject.fps
            ):

                track_df.at[object_id, "Time_crossing_exit"] = (
                    track_df.at[object_id, "Crossing_Gate/Frame"][-1][1]
                    / view.objectstorage.videoobject.fps
                )

            # list = Movement (only detectors not seconds)
            track_df.at[
                object_id, "Crossed_Section"
            ] = concatted_sorted_detector_list

            # start nested dictionary
            eventbased_dictionary[i] = {}

            eventbased_dictionary[i]["SectionID"] = detector
            eventbased_dictionary[i]["TrackID"] = object_id
            eventbased_dictionary[i]["Class"] = track_df.loc[object_id]["Class"]
            eventbased_dictionary[i]["Frame"] = int(crossing_frame)
            eventbased_dictionary[i]["X"] = int(nearest.x)
            eventbased_dictionary[i]["Y"] = int(nearest.y)



            # if object_id not in eventbased_dictionary[int(crossing_frame)]:
            #     eventbased_dictionary[int(crossing_frame)][f"Road_user_ID_{detector}"] = object_id
            #     eventbased_dictionary[int(crossing_frame)][f"Road_user_ID_{detector}_Class"] = track_df.loc[object_id]["Class"]


    return track_df, eventbased_dictionary


# %%

def assign_movement(object_validated_df):
    """Compares movements and associated detectors with sorted crossing list.

    Args:
        flowdictionary (dictionary): Dictionary with sections and movements.
        object_validated_df (dataframe): Dateframe with valuedated tracks.

    Returns:
        dataframe: Dataframe wth assigned movement to tracks.
    """
    # TODO delete iteration ==> jupyter nb
    for object_id, j in object_validated_df.iterrows():

        for movement_list in file_helper.flow_dict["Movements"]:

            # if detector in movements and real movement crossing events are true,
            #  key of movement dictionary is value of cell
            if (
                file_helper.flow_dict["Movements"][movement_list]
                == object_validated_df.loc[object_id]["Crossed_Section"]
            ):

                object_validated_df.at[object_id, "Movement_name"] = movement_list
                break

    return object_validated_df


# %%
def safe_to_exl(dataframe_autocount, dataframe_eventbased):
    """Safe dataframe as cvs and asks for filepath.


    Args:
        process_object (dataframe): Dataframe with object information.
    """

    dataframe_list = [dataframe_autocount, dataframe_eventbased]
    
    for dataframe in dataframe_list:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        dataframe.to_csv(file_path)




# %%
def time_calculation_dataframe(object_validated_df):
    """Creates columns with time, calculated from frame and fps.

    Args:
        timedelta_entry (int): Start time of video
        fps (int): Frames per seconds.
        object_validated_df (dataframe): Dataframe with tracks.

    Returns:
        dataframe: Dataframe with tracks and new created columns with
        information in timeformat.
    """
    # if timedelta_entry is None:

    #     entry_timedelta = "00:00:00"

    # else:

    #     entry_timedelta = timedelta_entry.get()

    object_validated_df["first_appearance_time"] = pd.to_timedelta(
            (
                object_validated_df["first_appearance_frame"]
                / view.objectstorage.videoobject.fps
            ),
            unit="s",
        )+view.objectstorage.videoobject.datetime_obj
    
    object_validated_df["last_appearance_time"] = pd.to_timedelta(
            (
                object_validated_df["last_appearance_frame"]
                / view.objectstorage.videoobject.fps
            ),
            unit="s",
        ) + view.objectstorage.videoobject.datetime_obj

    object_validated_df["first_appearance_time"] = object_validated_df["first_appearance_time"].astype('datetime64[s]')
    object_validated_df["last_appearance_time"] = object_validated_df["last_appearance_time"].astype('datetime64[s]')   

    # object_validated_df["first_appearance_time"] = object_validated_df[
    #     "first_appearance_time"
    # ].dt.strftime("%H:%M:%S")

    # object_validated_df["last_appearance_time"] = object_validated_df[
    #     "last_appearance_time"
    # ].dt.strftime("%H:%M:%S")

    return object_validated_df


def clean_dataframe(object_validated_df):
    """Deletes unnecessary columns.

    Args:
        object_validated_df (dataframe): dataframe of validated object tracking

    Returns:
        dataframe: returns cleaned dataframe
    """
    # List hast to be tuple or string in order to be groupby
    object_validated_df["Crossed_Section"] = object_validated_df["Crossed_Section"].apply(str)
 
    return object_validated_df.loc[
        :,
        [
            "Class",
            "Crossed_Section",
            "Movement_name",
            "first_appearance_frame",
            "first_appearance_time",
            "last_appearance_frame",
            "last_appearance_time",
            "Time_crossing_entrance",
            "Time_crossing_exit",
        ], ]


def resample_dataframe(entry_interval, object_validated_df):
    """Groups and timeresamples dataframe.

    Args:
        entry_interval (integer): timeinterval in which grouped data is summed up
        object_validated_df (dataframe): Dataframe

    Returns:
        dataframe: Returns grouped and resampled dataframe
    """
    entry_interval_time = str(entry_interval.get())

    if entry_interval_time not in ["0", "None"]:
        print("Dataframe gets resampled")

        object_validated_df["Datetime"] = pd.to_datetime(
            object_validated_df["first_appearance_time"]
        )

        object_validated_df = object_validated_df.set_index("Datetime")

        object_validated_df = (
            object_validated_df.groupby(
                by=[
                    pd.Grouper(freq=f"{entry_interval_time}T"),
                    "Class",
                    "Crossed_Section",
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

def eventased_dictionary_to_dataframe(eventbased_dictionary):
    """_summary_

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events

    Returns:
        dataframe: dataframe with events and belonging datetime
    """

    eventbased_dataframe = pd.DataFrame.from_dict(eventbased_dictionary, orient='index')
    eventbased_dataframe.index.set_names(["EventID"], inplace=True)
    eventbased_dataframe["seconds"] = (eventbased_dataframe["Frame"] /view.objectstorage.videoobject.fps)
    eventbased_dataframe["seconds"] = eventbased_dataframe["seconds"].astype('int')  
    eventbased_dataframe["DateTime"] = pd.to_timedelta(eventbased_dataframe["seconds"], unit='seconds')
    eventbased_dataframe["DateTime"] = eventbased_dataframe["DateTime"] + view.objectstorage.videoobject.datetime_obj
#    eventbased_dataframe = eventbased_dataframe.set_index("EventID")
    eventbased_dataframe.drop('seconds', axis=1, inplace=True)
    return eventbased_dataframe




def automated_counting(entry_interval=None, entry_timedelta=None, for_drawing=False):
    """Calls previous functions for better readability.

    Args:
        timedelta_entry (int): Time between two  frames.
        fps (int): Frames per seconds.
        flowdictionary (dictionary): Dictionary with sections and movements.
        tracks (dictionary): Dictionary with tracks.
    Returns:
        (dataframe): Dateframe with counted vehicles and further information.
    """
    # TODO: Reduce unnecessary calculation but do calculation if 
        # detectorfile changes
    #if not button_bool["dataframe_cleaned"]:

    # if gui_dict["tracks_imported"] and detector_dic and movement_dic:
    detector_df = dic_to_detector_dataframe()
    # object_validated_df = dic_to_object_dataframe()
    object_with_intersection_df = calculate_intersections(detector_df, file_helper.tracks_df)

    print(" successful ")

    object_with_intersection_df, file_helper.eventbased_dictionary = find_intersection_order(object_with_intersection_df)
    object_with_intersection_df = assign_movement(object_with_intersection_df)

    object_with_intersection_df = time_calculation_dataframe(object_with_intersection_df)

    file_helper.cleaned_object_dataframe = clean_dataframe(object_with_intersection_df)

    #button_bool["dataframe_cleaned"] = True

    file_helper.cleaned_object_dataframe["Datetime"] = pd.to_datetime(
        file_helper.cleaned_object_dataframe["first_appearance_time"]
    )
    file_helper.cleaned_object_dataframe.index.set_names(['Object_ID'], inplace=True)
    file_helper.cleaned_object_dataframe.reset_index(inplace=True)

    file_helper.cleaned_object_dataframe.set_index("Datetime" ,inplace=True)
    
    eventbased_dataframe = eventased_dictionary_to_dataframe(file_helper.eventbased_dictionary)

    if for_drawing:

        return file_helper.cleaned_object_dataframe

    cleaned_resampled_object_df = resample_dataframe(
        entry_interval, file_helper.cleaned_object_dataframe
    )


    safe_to_exl(cleaned_resampled_object_df, eventbased_dataframe)

    # return cleaned_resampled_object_df


def create_setting_window():
    """Creates window with button to resample dataframe and two
    inputfields to enter starting time and timeinterval.

    Args:
        fps (int): Frames per second.
        flowdictionary (dictionary): Dictionary with sections and movements.
        tracks (dictionary): Dictionary with tracks.
    """

    if not button_bool["tracks_imported"]:
        info_message("Warning", "Please import tracks first!")

        return

    # creates window to insert autocount time and groupby time
    toplevelwindow = Toplevel()

    toplevelwindow.title("Settings for autocount")

    time_entry_header = Label(toplevelwindow, text="Record start time")
    time_entry_header.grid(row=0, column=0, columnspan=5, sticky="w")

    time_entry = Entry(toplevelwindow, width=8)

    time_entry.grid(row=1, column=0, sticky="w", pady=5, padx=5)
    time_entry.focus()
    time_entry.insert(0, "UNUSED")

    timeinterval_entry_header = Label(toplevelwindow, text="Timeinterval (min)")
    timeinterval_entry_header.grid(row=2, column=0, columnspan=5, sticky="w")

    timeinterval_entry = Entry(toplevelwindow, width=8)
    timeinterval_entry.grid(row=3, column=0, sticky="w", pady=5, padx=5)
    timeinterval_entry.insert(0, "None")

    toplevelwindow_button = Button(
        toplevelwindow,
        text="Save file",
        command=lambda: automated_counting(timeinterval_entry, time_entry, ),
    )
    toplevelwindow_button.grid(
        row=4, columnspan=5, column=0, sticky="w", pady=5, padx=5
    )

    toplevelwindow.protocol("WM_DELETE_WINDOW")
    # makes the background window unavailable
    toplevelwindow.grab_set()
