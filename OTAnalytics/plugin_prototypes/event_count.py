# % Import libraries and modules
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
from plugin_prototypes.otanalytics_parser import JsonParser, PandasDataFrameParser

# % set env parameters and path
EVENTS = "event_list"
SECTIONS = "sections"
eventlist_json_path = Path("data/eventlist.json")
sectionlist_json_path = Path("data/sectionlist.json")
from_time = ""
to_time = ""
interval_length = 1  # im minutes

# % Import Eventlist
eventlist_dict = JsonParser.from_dict(eventlist_json_path)

# % Import Sectionlist
sectionlist_dict = JsonParser.from_dict(sectionlist_json_path)

# % Create DataFrames for meta data and events
events_df = PandasDataFrameParser.from_dict(eventlist_dict[EVENTS]).sort_values(
    ["frame_number"]
)
events_df["timestamp"] = pd.to_datetime(
    events_df["timestamp"], format="%Y-%m-%d_%H-%M-%S"
)

# % Create list of section dicts
sections_dict = sectionlist_dict[SECTIONS]


# % Add degrees to directions
def get_degrees(p_1_x: float, p_1_y: float, p_2_x: float, p_2_y: float) -> float:
    diff_x = p_2_x - p_1_x
    diff_y = p_2_y - p_1_y

    v = np.array([diff_x, diff_y])
    u = np.array([0, -1])

    angle = np.degrees(np.arctan2(np.linalg.det([u, v]), np.dot(u, v)))

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

    if angle == 0:
        angle2 = angle + 360
    else:
        angle2 = angle

    sections_dict[s]["degrees"] = {
        "p1_to_p2": [deg_range(angle - 180), deg_range(angle2)],
        "p2_to_p1": [deg_range(angle), deg_range(angle + 180)],
    }


# % Get direciton names
def get_dir_name_line(event: pd.DataFrame, sections: dict) -> pd.Series:
    section_id = str(event["section_id"])
    section = sections[section_id]

    p_1_x = event["direction_vector"][0]
    p_1_y = event["direction_vector"][1]
    p_2_x = event["event_coordinate"][0]
    p_2_y = event["event_coordinate"][1]

    angle_of_track = deg_range(get_degrees(p_1_x, p_1_y, p_2_x, p_2_y))

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


events_df_dir = events_df.apply(get_dir_name_line, args=[sections_dict], axis=1)

# % Create section name mapper
section_name_mapper = {
    sections_dict[s]["section_id"]: sections_dict[s]["name"]
    for s in sections_dict.keys()
}

# % TODO: Set time intervals
if from_time != "":
    from_time_formatted = pd.to_datetime(from_time)
    events_df_dir = events_df_dir[events_df_dir["timestamp"] >= from_time_formatted]
    start_time = from_time_formatted
else:
    start_time = events_df_dir.loc[0, "timestamp"]

if to_time != "":
    to_time_formatted = pd.to_datetime(to_time)
    events_df_dir = events_df_dir[events_df_dir["timestamp"] < to_time_formatted]
else:
    end_time = events_df_dir.loc[len(events_df_dir) - 1, "timestamp"]

duration = end_time - start_time
interval = pd.Timedelta(interval_length, "m")

# % Create counting table
counts_section = (
    events_df_dir.groupby(
        [
            pd.Grouper(key="timestamp", freq=f"{interval_length}Min"),
            "section_id",
            "direction",
            "vehicle_type",
        ]
    )["vehicle_id"]
    .count()
    .reset_index()
    .rename({"timestamp": "time_interval", "vehicle_id": "n_vehicles"}, axis=1)
)
counts_section["section_name"] = counts_section["section_id"].map(section_name_mapper)
counts_section_agg = (
    counts_section.pivot(
        index=["time_interval", "section_id", "section_name", "direction"],
        columns="vehicle_type",
        values="n_vehicles",
    )
    .reset_index()
    .fillna(0)
)

# % Create counting plot
p = sns.FacetGrid(
    counts_section, hue="vehicle_type", row="section_name", col="direction", aspect=2
)
p.map(
    sns.barplot,
    "time_interval",
    "n_vehicles",
    alpha=0.7,
    order=counts_section["time_interval"].unique(),
)

# % Create flow table
flows_section = events_df_dir[["vehicle_id", "vehicle_type", "timestamp", "section_id"]]
flows_section["section_id2"] = flows_section["section_id"]
flows_section = (
    flows_section.pivot_table(
        index="vehicle_id",
        values=["section_id", "section_id2", "timestamp", "vehicle_type"],
        aggfunc={
            "section_id": "first",
            "section_id2": "last",
            "timestamp": "first",
            "vehicle_type": "first",
        },
        fill_value=0,
    )
    .reset_index()
    .rename({"section_id": "from_section", "section_id2": "to_section"}, axis=1)
)
flows_section = (
    flows_section.groupby(
        [
            pd.Grouper(key="timestamp", freq=f"{interval_length}Min"),
            "from_section",
            "to_section",
            "vehicle_type",
        ]
    )["vehicle_id"]
    .count()
    .reset_index()
    .rename({"timestamp": "time_interval"}, axis=1)
)
flows_section["from_section"] = flows_section["from_section"].map(section_name_mapper)
flows_section["to_section"] = flows_section["to_section"].map(section_name_mapper)
flows_section = (
    flows_section.pivot(
        index=["time_interval", "from_section", "to_section"],
        columns="vehicle_type",
        values="vehicle_id",
    )
    .reset_index()
    .fillna(0)
)
