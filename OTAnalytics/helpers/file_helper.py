# OTAnalytics: helpers for filehandling
# Copyright (C) 2020 OpenTrafficCam Contributors
# <https://github.com/OpenTrafficCam
# <team@opentrafficcam.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# %%
import os
import re
import itertools
from shapely.geometry import LineString, Point
from datetime import datetime

# %%

flow_dict = {"Detectors": {}, "Movements": {}}
selectionlist_objects = []
selectionlist_sections = []
# maybe necessary to incomment

list_of_analyses = []



raw_detections = []
tracks_dic = {}
tracks_df = None
tracks_geoseries = None

cleaned_object_dataframe = []
eventbased_dictionary = {}

event_number = 1

tracks_live = {}
otflow_file = None
ottrk_file = None



def get_dir(path: str):
    """removes filename from path

    Args:
        path (str): filepath

    Returns:
        _type_: directory of path
    """

    return os.path.dirname(path)


def get_filename(path: str):

    return os.path.basename(path)


def create_pattern(videofilename):

    file_pattern = re.split(r"\_", videofilename)
    otflow_pattern = None
    ottrk_pattern = None

    try:

        otflow_pattern = (
            f"^{file_pattern[0]}\\_" + r"\w{4}\_" + file_pattern[2][:4] + ".*otflow"
        )

        ottrk_pattern = (
            r"^"
            + file_pattern[0]
            + r"\_"
            + r"\w{4}\_"
            + file_pattern[2]
            + r"\_"
            + file_pattern[3][:8]
            + ".*ottrk"
        )
    except Exception:
        return otflow_pattern, ottrk_pattern

    return otflow_pattern, ottrk_pattern


def check_fileexistence(path, otflow_pattern, ottrk_pattern):
    # sourcery skip: use-fstring-for-concatenation
    global otflow_file
    global ottrk_file

    for root, dirs, files in os.walk(path):
        for file in files:
            if bool(re.search(otflow_pattern, file)):

                otflow_file = file

            elif bool(re.search(ottrk_pattern, file)):

                ottrk_file = file
    return bool(re.search(otflow_pattern, file)), bool(re.search(ottrk_pattern, file))

def re_initialize():
    global flow_dict, raw_detections, tracks

    flow_dict = {"Detectors": {}, "Movements": {}}
    raw_detections = []
    tracks = {}


# %%
def permutation_of_list(selected_sections, maxpermutation=2):
    """Creates a list of all possible combination of section to create every possible movement

    Args:
        selected_sections (_type_): Sections
        maxpermutation (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: List of possible combinations of sections.
    """

    return list(itertools.permutations(selected_sections, r=maxpermutation))


# %%
def fill_tree_views(option=3, tree_movements=None, tree_sections=None):

    global flow_dict, raw_detections, tracks

    if option in [1, 3]:
        for movement in flow_dict["Movements"]:

            tree_movements.insert(
                parent="",
                index="end",
                text=movement,
                value=[(flow_dict["Movements"][movement])],
            )

    if option in [2, 3]:
        for detector in flow_dict["Detectors"]:
            tree_sections.insert(parent="", index="end", text=detector)


def geobject_creator(row):
    if len(row["Coord"]) > 1:
        return LineString(row["Coord"])
    else:
        return Point(row["Coord"])

def get_datetime_from_filename(filename: str, epoch_datetime="1970-01-01_00-00-00"):
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