# % Import libraries and modules
from pathlib import Path

import numpy as np
import pandas as pd
from prototypes.otanalytics_parser import JsonParser, PandasDataFrameParser

# % set env parameters and path
EVENTS = "event_list"
SECTIONS = "sections"
eventlist_json_path = Path("data/eventlist.json")
sectionlist_json_path = Path("data/sectionlist.json")

# % Import Eventlist
eventlist_dict = JsonParser.from_dict(eventlist_json_path)

# % Import Sectionlist
sectionlist_dict = JsonParser.from_dict(sectionlist_json_path)

# % Create DataFrames for meta data and events
events_df = PandasDataFrameParser.from_dict(eventlist_dict[EVENTS])

# % Create list of section dicts
sections_dict = sectionlist_dict[SECTIONS]


# % Add degrees to directions
def get_degrees(p_1_x: float, p_1_y: float, p_2_x: float, p_2_y: float) -> float:
    diff_x = p_2_x - p_1_x
    diff_y = p_2_y - p_1_y

    v = np.array([diff_x, diff_y])
    u = np.array([0, 1])

    angle = np.degrees(np.arctan2(np.linalg.det([v, u]), np.dot(v, u)))

    return angle


def deg_range(angle: float) -> float:
    if angle < 0:
        return angle + 360
    elif angle > 360:
        return angle - 360
    else:
        return angle


for s in sections_dict.keys():
    p_1_x = sections_dict[s]["coordinates"]["p_1"]["x"]
    p_1_y = sections_dict[s]["coordinates"]["p_1"]["y"]
    p_2_x = sections_dict[s]["coordinates"]["p_2"]["x"]
    p_2_y = sections_dict[s]["coordinates"]["p_2"]["y"]
    angle = get_degrees(p_1_x, p_1_y, p_2_x, p_2_y)

    sections_dict[s]["degrees"] = {
        "p1_to_p2": [deg_range(angle - 90), deg_range(angle + 90)],
        "p2_to_p1": [deg_range(angle + 180 - 90), deg_range(angle + 180 + 90)],
    }


# % Get direciton names
def get_dir_name(event: pd.DataFrame, sections: dict) -> pd.Series:
    section_id = str(event["section_id"])
    section = sections[section_id]

    p_1_x = event["event_coordinate"][0]
    p_1_y = event["event_coordinate"][1]
    p_2_x = event["direction_vector"][0]
    p_2_y = event["direction_vector"][1]

    angle_of_track = deg_range(get_degrees(p_1_x, p_1_y, p_2_x, p_2_y) - 180)

    event["angle"] = angle_of_track

    for d in section["directions"].keys():
        min_angle = section["degrees"][d][0]
        max_angle = section["degrees"][d][1]
        if angle_of_track >= min_angle and angle_of_track <= max_angle:
            event["direction"] = section["directions"][d]
            return event
        elif (
            max_angle < min_angle
            and angle_of_track >= min_angle
            and angle_of_track <= 360
        ):
            event["direction"] = section["directions"][d]
            return event
        elif (
            max_angle < min_angle
            and angle_of_track >= 0
            and angle_of_track <= max_angle
        ):
            event["direction"] = section["directions"][d]
            return event


events_test = events_df.apply(get_dir_name, args=[sections_dict], axis=1)
