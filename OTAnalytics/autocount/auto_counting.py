import heapq
from tkinter import Button, Entry, Label, Toplevel
import helpers.file_helper as file_helper
import pandas as pd
from shapely.geometry import LineString, Point
import os
import logging


def create_event(detector, object_id, vhc_class, nearest_x, nearest_y, frame):
    """Creates dictionary with event information

    Args:
        detector (str): crossed section
        object_id (int): row index / track id
        vhc_class (str): verhicle class
        nearest_x (int): x coordinate of crossing point
        nearest_y (int): y coordinate of crossing point
        frame (int): frame where crossing happend
    """

    file_helper.event_number += 1
    file_helper.list_of_analyses[file_helper.list_of_analyses_index].eventbased_dictionary[file_helper.event_number] = {"TrackID": object_id, "SectionID": detector, "Class": vhc_class, "Frame": int(frame), "X": int(nearest_x), "Y": int(nearest_y)}


def create_section_geometry_object():
    """_summary_
    """
    for detector in file_helper.flow_dict["Detectors"]:
        x1 = file_helper.flow_dict["Detectors"][detector]["start_x"]
        y1 = file_helper.flow_dict["Detectors"][detector]["start_y"]
        x2 = file_helper.flow_dict["Detectors"][detector]["end_x"]
        y2 = file_helper.flow_dict["Detectors"][detector]["end_y"]

        file_helper.flow_dict["Detectors"][detector]["geometry"] = LineString([(x1, y1), (x2, y2)])

def find_intersection(row):
    """_summary_

    Args:
        row (dataframerow): _description_

    Returns:
        _type_: _description_
    """

    for detector in  file_helper.flow_dict["Detectors"]:

        if row.geometry.intersects(file_helper.flow_dict["Detectors"][detector]["geometry"]):

            # returns coordinates from intersections as point object
            point_geometry = row.geometry.intersection( file_helper.flow_dict["Detectors"][detector]["geometry"])
            # create points from coords
            line_points = map(Point, row.geometry.coords)

            nearest, second_nearest = heapq.nsmallest(
                2, line_points, key=point_geometry.distance
            )

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
                
            create_event(detector,row.name,row.Class, nearest.x, nearest.y, frame_of_crossing)    

    return row

def assign_movement(row):
    """Assigns movement from from movement dic

    Args:
        row (dataframe row): row from dataframe containing trajectorie information

    Returns:
        movement_key: returns key if list of crossed sections is in movement values
    """
    sorted_sections = [x for (y,x) in sorted(zip(row["Crossed_Frames"], row["Crossed_Section"]))]

    movement = [k for k, v in file_helper.flow_dict["Movements"].items() if v == sorted_sections]

    return movement[0] if movement else None
        
# %%
def safe_to_csv(analyse,dataframe_autocount, dataframe_eventbased=None ):
    """Safe dataframe as cvs and asks for filepath.

    Args:
        process_object (dataframe): Dataframe with object information.
    """

    #dataframe_list = [dataframe_autocount, dataframe_eventbased]

    filepath_event = os.path.join(analyse.folder_path, analyse.analyse_name + '_events.csv')
    filepath_autocount = os.path.join(analyse.folder_path, analyse.analyse_name + '_count.csv')
    
    # for dataframe in dataframe_list:
    #     file_path = filedialog.asksaveasfilename(
    #         defaultextension=".csv", filetypes=[("CSV", "*.csv")]
    #     )
    dataframe_eventbased.to_csv(filepath_event)
    dataframe_autocount.to_csv(filepath_autocount)


# %%
def time_calculation_dataframe(track_df, fps=None, datetime_obj=None):
    """Creates columns with time, calculated from frame and fps.

    Args:
        timedelta_entry (int): Start time of video
        fps (int): Frames per seconds.
        object_validated_df (dataframe): Dataframe with tracks.

    Returns:
        dataframe: Dataframe with tracks and new created columns with
        information in timeformat.
    """
    if fps is None or datetime_obj is None:
        fps = file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.fps
        datetime_obj=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.datetime_obj

    track_df["first_appearance_time"] = pd.to_timedelta(
            (
                track_df["first_appearance_frame"]
                / fps
            ),
            unit="s",
        )+datetime_obj

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

def eventased_dictionary_to_dataframe(analyse, fps=None, datetime_obj=None):
    """_summary_

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events

    Returns:
        dataframe: dataframe with events and belonging datetime
    """
    if fps is None or datetime_obj is None:
        fps = analyse.videoobject.fps
        datetime_obj = analyse.videoobject.datetime_obj

    eventbased_dataframe = pd.DataFrame.from_dict(analyse.eventbased_dictionary, orient='index')
    eventbased_dataframe.index.set_names(["EventID"], inplace=True)
    eventbased_dataframe["seconds"] = (eventbased_dataframe["Frame"] /fps)
    eventbased_dataframe["seconds"] = eventbased_dataframe["seconds"].astype('int')  
    eventbased_dataframe["DateTime"] = pd.to_timedelta(eventbased_dataframe["seconds"], unit='seconds')
    eventbased_dataframe["DateTime"] = eventbased_dataframe["DateTime"] + datetime_obj
    #eventbased_dataframe = eventbased_dataframe.set_index("EventID")
    eventbased_dataframe.drop('seconds', axis=1, inplace=True)
    return eventbased_dataframe


def automated_counting(entry_interval=None, entry_timedelta=None, for_drawing=False, multicomputation = False):
    """Calls previous functions for better readability.

    Args:
        timedelta_entry (int): Time between two  frames.
        fps (int): Frames per seconds.
        flowdictionary (dictionary): Dictionary with sections and movements.
        tracks (dictionary): Dictionary with tracks.
    Returns:
        (dataframe): Dateframe with counted vehicles and further information.
    """
    #create log
    logging.basicConfig(filename="log.txt", level=logging.INFO,
                        format="%(asctime)s %(message)s",  filemode="w")
    #indexes to analyse
    analyse_indexes = []
    
    if multicomputation:


        for index in range(len(file_helper.list_of_analyses)):
            analyse_indexes.append(index)

    else:
        for index in file_helper.selectionlist_videofiles:

            analyse_indexes.append(index)

    for analyse_index in analyse_indexes:
    # create necessary columns
        #try:
        if file_helper.list_of_analyses[analyse_index].tracks_dic and file_helper.flow_dict["Detectors"]:
            file_helper.list_of_analyses_index = analyse_index

            file_helper.list_of_analyses[analyse_index].tracks_df["Crossed_Section"] = ""
            file_helper.list_of_analyses[analyse_index].tracks_df["Crossed_Frames"] = ""

            create_section_geometry_object()
            file_helper.list_of_analyses[analyse_index].tracks_df =file_helper.list_of_analyses[analyse_index].tracks_df.apply(lambda row: find_intersection(row), axis=1)
            file_helper.list_of_analyses[analyse_index].tracks_df["Movement"] = file_helper.list_of_analyses[analyse_index].tracks_df.apply(lambda row: assign_movement(row), axis=1)
            file_helper.list_of_analyses[analyse_index].tracks_df["Appearance"] = time_calculation_dataframe(file_helper.list_of_analyses[analyse_index].tracks_df)
            eventbased_dataframe = eventased_dictionary_to_dataframe(file_helper.list_of_analyses[file_helper.list_of_analyses_index],fps=None, datetime_obj=None)

            tracks_df_result = clean_dataframe(file_helper.list_of_analyses[analyse_index].tracks_df)

            # # if for_drawing:

                #return file_helper.list_of_analyses[file_helper.list_of_analyses_index].cleaned_dataframe

            safe_to_csv(file_helper.list_of_analyses[analyse_index],tracks_df_result, eventbased_dataframe)
        else:
            logging.info(f"\n Could not compute File: {file_helper.list_of_analyses[analyse_index].analyse_name}")



def create_setting_window():
    """Creates window with button to resample dataframe and two
    inputfields to enter starting time and timeinterval.

    Args:
        fps (int): Frames per second.
        flowdictionary (dictionary): Dictionary with sections and movements.
        tracks (dictionary): Dictionary with tracks.
    """

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

    toplevelwindow_button_compute_onefile = Button(
        toplevelwindow,
        text="Compute",
        command=lambda: automated_counting(timeinterval_entry, time_entry, ),
    )
    toplevelwindow_button_compute_onefile.grid(
        row=4, columnspan=5, column=0, sticky="w", pady=5, padx=5
    )
    toplevelwindow_button_compute_all = Button(
        toplevelwindow,
        text="Compute all",
        command=lambda: automated_counting(timeinterval_entry, time_entry,multicomputation=True ),
    )
    toplevelwindow_button_compute_all.grid(
        row=5, columnspan=5, column=0, sticky="w", pady=5, padx=5
    )


    toplevelwindow.protocol("WM_DELETE_WINDOW")
    # makes the background window unavailable
    toplevelwindow.grab_set()
