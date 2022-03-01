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

import os
import re

flow_dict = {"Detectors": {}, "Movements": {}}
selectionlist = []
raw_detections = []
tracks = {}
tracks_live = {}


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


# def extract_pattern(filename):

#     # return re.search("[a-z]+", filename)


def create_pattern(videofilename):

    file_pattern = re.split(r"\_", videofilename)

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

    return otflow_pattern, ottrk_pattern


def check_fileexistence(path, otflow_patthern, ottrk_pattern):
    # sourcery skip: use-fstring-for-concatenation

    for root, dirs, files in os.walk(path):
        for file in files:
            if bool(re.search(otflow_patthern, file)):

                otflow_file = file

            elif bool(re.search(ottrk_pattern, file)):

                ottrk_file = file

    return otflow_file, ottrk_file
