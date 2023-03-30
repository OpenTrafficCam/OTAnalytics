# % Import libraries and modules
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from plugin_parser.otanalytics_parser import JsonParser, PandasDataFrameParser

# % set env parameters and path
EVENTS = "event_list"
SECTIONS = "sections"
# SIGNAL_PROG = "signal_programs"
TIME_FORMAT = "%d.%m%.%y %H:%M Uhr"
eventlist_json_path = Path("data/eventlist.json")
sectionlist_json_path = Path("data/sectionlist.json")
signal_prog_list_json_path = Path("data/signal_programs.json")
from_time = ""
to_time = ""
interval_length = 2  # im minutes

# % Import Eventlist
eventlist_dict = JsonParser.from_dict(eventlist_json_path)

# % Import Sectionlist
sectionlist_dict = JsonParser.from_dict(sectionlist_json_path)

# % Import Signal programme list
signal_prog_list_dict = JsonParser.from_dict(signal_prog_list_json_path)


# % Create DataFrames for meta data and events
def import_events(events: dict) -> pd.DataFrame:
    events_df = PandasDataFrameParser.from_dict(events).sort_values(["frame_number"])
    events_df["timestamp"] = pd.to_datetime(
        events_df["timestamp"], format="%Y-%m-%d_%H-%M-%S"
    )

    return events_df


section_events_df = import_events(eventlist_dict[EVENTS])
signal_events_df = import_events(signal_prog_list_dict[EVENTS])

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
def get_dir_name_line(event: pd.DataFrame, sections: dict, exclude: str) -> pd.Series:
    if event["vehicle_type"] == exclude:
        return event
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


section_events_df_dir = section_events_df.apply(
    get_dir_name_line, args=[sections_dict, "SIGNAL"], axis=1
).reset_index(drop="index")

# % Create section name mapper
section_name_mapper = {
    sections_dict[s]["section_id"]: sections_dict[s]["name"]
    for s in sections_dict.keys()
}

# % TODO: Set time intervals
if from_time != "":
    from_time_formatted = pd.to_datetime(from_time)
    section_events_df_dir = section_events_df_dir[
        section_events_df_dir["timestamp"] >= from_time_formatted
    ]
    start_time = from_time_formatted
else:
    start_time = section_events_df_dir.loc[0, "timestamp"]

if to_time != "":
    to_time_formatted = pd.to_datetime(to_time)
    section_events_df_dir = section_events_df_dir[
        section_events_df_dir["timestamp"] < to_time_formatted
    ]
else:
    end_time = section_events_df_dir.loc[len(section_events_df_dir) - 1, "timestamp"]

duration = end_time - start_time
interval = pd.Timedelta(interval_length, "m")


# % Calculate Zeitbedarfe
def calculate_zbw(
    events: pd.DataFrame, signal_program: pd.DataFrame, directions: dict
) -> pd.DataFrame:
    events_queue_pos = pd.DataFrame()

    for section_id in signal_program["section_id"].unique():
        all_events = pd.concat(
            [events[events["direction"] == directions[section_id]], signal_program]
        ).sort_values(["timestamp", "event_type"], ascending=[True, False])
        events_section = all_events[
            all_events["section_id"] == section_id
        ].reset_index()
        events_section["time_diff"] = events_section["timestamp"].diff()
        events_section["time_diff_sec"] = events_section["time_diff"].dt.total_seconds()

        u = 0
        for row in range(0, len(events_section)):
            if events_section.loc[row, "event_type"] == "SIGNAL_GREEN":
                u += 1
            events_section.loc[row, "umlauf"] = u

        for u in events_section["umlauf"].unique():
            events_section.loc[events_section["umlauf"] == u, "queue_position"] = range(
                0, len(events_section[events_section["umlauf"] == u])
            )

        events_queue_pos = pd.concat([events_queue_pos, events_section])

    return events_queue_pos[events_queue_pos["vehicle_type"] != "SIGNAL"]


events_queue_pos = calculate_zbw(
    section_events_df_dir, signal_events_df, directions={3: "stadteinwärts"}
)


# % Create plot
fig = px.box(
    events_queue_pos,
    x="queue_position",
    y="time_diff_sec",
    facet_col="direction",
    facet_row="section_id",
    facet_col_spacing=0.05,
    facet_row_spacing=0.1,
    height=800,
)

"""fig.update_yaxes(
    title_text="Number of road users",
)"""
fig.update_layout(
    title="Zeitbedarfswerte an Section X",
    xaxis_title="Warteschlangenposition",
    yaxis_title="Zeitbedarf [s]",
    legend_title="Zeitbedarfswert",
)
fig.show()
