#%%
"""Module to create eventbased dataframe and safe as csv. Input files are the folder where the ottrk are located and
    and the previously created section file    

Returns:
    csv: safe the eventbased dataframe as csv
"""

import os
import sys
import re

from pathlib import Path
from shapely.geometry import LineString


from datetime import datetime
import logging

#create log
logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format="%(asctime)s %(message)s",  filemode="w")


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

import helpers.file_helper as file_helper
import json
from view.tracks import load_and_convert
from autocount.auto_counting import find_intersection, assign_movement,time_calculation_dataframe, eventased_dictionary_to_dataframe, clean_dataframe

#%%
# load section file

FILEPATH_SECTION = r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam02\TUDCam02_sections.otflow"
INPUT_TRACK_DIR = (r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam02\Detection_Tracking_YOLOv5s\Track-files")
OUTPUT_DIR = (r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam01\Eventfiles")
#%%
track_list = Path(INPUT_TRACK_DIR).glob("*.ottrk")

# sectionfile creation
sectionfile = open(FILEPATH_SECTION, "r")
section_file = sectionfile.read()
detector_dic = json.loads(section_file)

def create_detector_geometry(detector_dic):
    for detector in detector_dic["Detectors"]:
        x1 = detector_dic["Detectors"][detector]["start_x"]
        y1 = detector_dic["Detectors"][detector]["start_y"]
        x2 = detector_dic["Detectors"][detector]["end_x"]
        y2 = detector_dic["Detectors"][detector]["end_y"]

        detector_dic["Detectors"][detector]["geometry"] = LineString([(x1, y1), (x2, y2)])

    return detector_dic
detector_dic = create_detector_geometry(detector_dic)


#%%

def datetime_str(filename, epoch_datetime="1970-01-01_00-00-00"):
    """ Get date and time from file name.
    Searches for "_yyyy-mm-dd_hh-mm-ss".
    Returns "yyyy-mm-dd_hh-mm-ss".
    Args:
        filename (str): filename with expression
        epoch_datetime (str): Unix epoch (00:00:00 on 1 January 1970)
    Returns:
        str: datetime
    """
    regex = "_([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_[0-9]{2,2}-[0-9]{2,2}-[0-9]{2,2})"
    match = re.search(regex, filename)
    if not match:
        return epoch_datetime

    # Assume that there is only one timestamp in the file name
    datetime_str = match.group(1)  # take group withtout underscore

    try:
        datetime.strptime(datetime_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return epoch_datetime

    return datetime_str

def get_datetime_obj(datetime_str):
    """create datetimepobject

    Args:
        datetime_str (str): datetime from re as string

    Returns:
        datetime: datetimeobject
    """
    return datetime.strptime(datetime_str, '%Y-%m-%d_%H-%M-%S')


#%%%
#Load track from filepath
def load_trackfile(filepath):
    trackfile = open(filepath, "r")
    trackfile = trackfile.read()
    trackfile_dic = json.loads(trackfile)

    #trackfilename from metadata
    return trackfile,trackfile_dic["vid_config"]["file"]


# %%

def autoevaluate(detector_dic):
    for filepath in track_list:
        file_helper.flow_dict = detector_dic


        datetime_string = datetime_str(str(filepath), epoch_datetime="1970-01-01_00-00-00")
        datetime_obj = get_datetime_obj(datetime_string)
        print("creating datetime from filename worked")
        trackfile, filename = load_trackfile(filepath)
        # Load and convert Tracks
        _, _, tracks_df, _ = load_and_convert(x_resize_factor=1, y_resize_factor=1, autoimport=True, files=trackfile)

        # if there are not tracks due to empty file
        if tracks_df is None:
            continue

        tracks_df["Crossed_Section"] = ""
        tracks_df["Crossed_Frames"] = ""

        #find intersection
        tracks_df = tracks_df.apply(lambda row: find_intersection(row), axis=1)
        tracks_df["Movement"] = tracks_df.apply(lambda row: assign_movement(row), axis=1)
        tracks_df["Appearance"] = time_calculation_dataframe(tracks_df, 20,datetime_obj )

        eventbased_dataframe = eventased_dictionary_to_dataframe(file_helper.eventbased_dictionary,20, datetime_obj)
        tracks_df_result = clean_dataframe(tracks_df)

        eventbased_dataframe.to_csv(f"{filename}_events.csv")
        tracks_df_result.to_csv(f"{filename}_tracks.csv")
        #create dataframe

autoevaluate(detector_dic)