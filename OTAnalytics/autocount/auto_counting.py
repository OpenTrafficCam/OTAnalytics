import heapq
from tkinter import Button, Entry, Label, Toplevel, filedialog

import geopandas as gpd
import helpers.config
import helpers.file_helper as file_helper
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
from view.helpers.gui_helper import button_bool, info_message



def create_event(detector , object_id,vhc_class, nearest_x,nearest_y, frame, ):
    print(file_helper.event_number)
    file_helper.event_number += 1
    file_helper.eventbased_dictionary[file_helper.event_number] = {"TrackID": object_id, "SectionID" : detector, "Class": vhc_class, "Frame": int(frame), "X": int(nearest_x), "Y": int(nearest_y)}


def create_section_geometry_object():
    for detector in file_helper.flow_dict["Detectors"]:
        x1 = file_helper.flow_dict["Detectors"][detector]["start_x"]
        y1 = file_helper.flow_dict["Detectors"][detector]["start_y"]
        x2 = file_helper.flow_dict["Detectors"][detector]["end_x"]
        y2 = file_helper.flow_dict["Detectors"][detector]["end_y"]

        file_helper.flow_dict["Detectors"][detector]["geometry"] = LineString([(x1,y1),(x2,y2)])

def find_intersection(row):
    """_summary_

    Args:
        row (_type_): _description_

    Returns:
        _type_: _description_
    """

    for detector in file_helper.flow_dict["Detectors"]:

        if row.geometry.intersects(file_helper.flow_dict["Detectors"][detector]["geometry"]):

            # returns coordinates from intersections as point object
            point_geometry = row.geometry.intersection(file_helper.flow_dict["Detectors"][detector]["geometry"])
            # create points from coords
            line_points = map(Point, row.geometry.coords)

            nearest, second_nearest = heapq.nsmallest(
                2, line_points, key=point_geometry.distance
            )

            #function for event
            

            closest_point_to_track = list(second_nearest.coords[:][0])

            #index at which the second closest points are
            index_number = row.Coord.index(closest_point_to_track)
            if row["Crossed_Section"]:
                row["Crossed_Section"].append(detector)

                frame_of_crossing = row.Frame[index_number]
                row["Crossed_Frames"].append(frame_of_crossing)

            else:
                row["Crossed_Section"] = [detector]

                frame_of_crossing = row.Frame[index_number]
                row["Crossed_Frames"] = [frame_of_crossing]
            create_event(detector,row.index,row.Class, nearest.x, nearest.y, frame_of_crossing )
    return row

def assign_movement(row):
    """_summary_

    Args:
        row (_type_): _description_

    Returns:
        _type_: _description_
    """
    row["Crossed_Section"] = [x for (y,x) in sorted(zip(row["Crossed_Frames"], row["Crossed_Section"]))]

    movement = [k for k, v in file_helper.flow_dict["Movements"].items() if v == row["Crossed_Section"]]

    return movement[0] if movement else None
        
# %%
def safe_to_csv(dataframe_autocount, dataframe_eventbased=None):
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
def time_calculation_dataframe(track_df):
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

    track_df["first_appearance_time"] = pd.to_timedelta(
            (
                track_df["first_appearance_frame"]
                / helpers.config.videoobject.fps
            ),
            unit="s",
        )+helpers.config.videoobject.datetime_obj  

    return track_df["first_appearance_time"].astype('datetime64[s]')



def clean_dataframe(track_df):
    """Deletes unnecessary columns.

    Args:
        object_validated_df (dataframe): dataframe of validated object tracking

    Returns:
        dataframe: returns cleaned dataframe
    """
    # List hast to be tuple or string in order to be groupby
    track_df["Crossed_Section"] = track_df["Crossed_Section"].apply(str)
 
    return track_df.loc[
        :,
        [
            "Class",
            "Crossed_Section",
            "Movement",
            "Appearance",

        ], ]


def resample_dataframe(entry_interval, track_df):
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

        track_df["Datetime"] = pd.to_datetime(
            track_df["Appearance"]
        )

        track_df = track_df.set_index("Datetime")

        track_df = (
            track_df.groupby(
                by=[
                    pd.Grouper(freq=f"{entry_interval_time}T"),
                    "Class",
                    "Crossed_Section",
                    "Movement",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="counts")
        )

        # track_df["Datetime"] = track_df["Datetime"].dt.strftime(
        #     "%H:%M:%S"
        # )

    return track_df

def eventased_dictionary_to_dataframe(eventbased_dictionary, fps=None, datetime_obj=None):
    """_summary_

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events

    Returns:
        dataframe: dataframe with events and belonging datetime
    """
    if fps is None:
        fps = helpers.config.videoobject.fps
    if datetime_obj is None:
        datetime_obj = helpers.config.videoobject.datetime_obj

    eventbased_dataframe = pd.DataFrame.from_dict(eventbased_dictionary, orient='index')
    eventbased_dataframe.index.set_names(["EventID"], inplace=True)
    eventbased_dataframe["seconds"] = (eventbased_dataframe["Frame"] /fps)
    eventbased_dataframe["seconds"] = eventbased_dataframe["seconds"].astype('int')  
    eventbased_dataframe["DateTime"] = pd.to_timedelta(eventbased_dataframe["seconds"], unit='seconds')
    eventbased_dataframe["DateTime"] = eventbased_dataframe["DateTime"] + datetime_obj
#   eventbased_dataframe = eventbased_dataframe.set_index("EventID")
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
    # create necessary columns
    file_helper.event_number = 0
    file_helper.tracks_df["Crossed_Section"] = ""
    file_helper.tracks_df["Crossed_Frames"] = ""
    print(file_helper.tracks_df)

    create_section_geometry_object()

    file_helper.flow_dict["Movements"] = {"Sued-Nord": ["Sued", "Nord"], "Nord-Sued": ["Nord", "Sued"]}
    file_helper.tracks_df = file_helper.tracks_df.apply(lambda row: find_intersection(row), axis=1)
    file_helper.tracks_df["Movement"] = file_helper.tracks_df.apply(lambda row: assign_movement(row), axis=1)
    file_helper.tracks_df["Appearance"] = time_calculation_dataframe(file_helper.tracks_df)

    tracks_df_result = clean_dataframe(file_helper.tracks_df)



    # object_with_intersection_df, file_helper.eventbased_dictionary = find_intersection_order(object_with_intersection_df)
    # object_with_intersection_df = assign_movement(object_with_intersection_df)

    # object_with_intersection_df = time_calculation_dataframe(object_with_intersection_df)

    # file_helper.cleaned_object_dataframe = clean_dataframe(object_with_intersection_df)

    #button_bool["dataframe_cleaned"] = True

    # file_helper.cleaned_object_dataframe["Datetime"] = pd.to_datetime(
    #     file_helper.cleaned_object_dataframe["first_appearance_time"]
    # )
    # file_helper.cleaned_object_dataframe.index.set_names(['Object_ID'], inplace=True)
    # file_helper.cleaned_object_dataframe.reset_index(inplace=True)

    # file_helper.cleaned_object_dataframe.set_index("Datetime" ,inplace=True)
    
    # eventbased_dataframe = eventased_dictionary_to_dataframe(file_helper.eventbased_dictionary)

    if for_drawing:

        return file_helper.cleaned_object_dataframe

    # cleaned_resampled_object_df = resample_dataframe(
    #     entry_interval, file_helper.cleaned_object_dataframe
    # )

    safe_to_csv(tracks_df_result)

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
