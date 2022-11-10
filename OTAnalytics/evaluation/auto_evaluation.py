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

from datetime import datetime
import logging

#create log
logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format="%(asctime)s %(message)s",  filemode="w")


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

import json
from view.tracks import load_and_convert
from autocount.auto_counting import dataframe_from_dictionary_sections, calculate_intersections, find_intersection_order, eventased_dictionary_to_dataframe

#%%
# load section file

FILEPATH_SECTION = r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam02\TUDCam02_sections.otflow"
INPUT_TRACK_DIR = (r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam02\Detection_Tracking_YOLOv5s\Track-files")
OUTPUT_DIR = (r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam01\Eventfiles")
#%%


# sectionfile creation
sectionfile = open(FILEPATH_SECTION, "r")
section_file = sectionfile.read()
section_file = json.loads(section_file)
section_df = dataframe_from_dictionary_sections(section_file["Detectors"])

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
track_list = Path(INPUT_TRACK_DIR).glob("*.ottrk")

for filepath in track_list:
    datetime_string = datetime_str(str(filepath), epoch_datetime="1970-01-01_00-00-00")
    datetime_obj = get_datetime_obj(datetime_string)
    print("creating datetime from filename worked")
    trackfile, filename = load_trackfile(filepath)
    # Load and convert Tracks
    _, _, tracks_df, _ = load_and_convert(x_resize_factor=1, y_resize_factor=1, autoimport=True, files=trackfile)

    if tracks_df is None:
        continue

    #expand trackdataframe
    track_df = calculate_intersections(section_df, tracks_df)
    
    #to get eventbased dataframe
    track_df, eventbased_dictionary = find_intersection_order(track_df, flow_dict=section_file["Detectors"], fps=20)
    
    #create dataframe from event based dictionary
    if eventbased_dictionary:
        eventbased_df = eventased_dictionary_to_dataframe(eventbased_dictionary, fps=20, datetime_obj=datetime_obj)

        eventbased_df.to_csv(f"{filename}_events.csv")

#start loop


# %%
