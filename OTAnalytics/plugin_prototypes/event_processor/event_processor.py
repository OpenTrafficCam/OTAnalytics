# % Import libraries and modules
import pandas as pd

from OTAnalytics.plugin_parser.otanalytics_parser import (
    JsonParser,
    PandasDataFrameParser,
)


class EventProcessor:
    def __init__(self, config: dict):
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FILTER_CLASS = config["FILTER_CLASS"]
        self.FILTER_SECTION = config["FILTER_SECTION"]
        self.EVENTLIST_PATH = config["EVENTLIST_PATH"]
        self.SECTIONSLIST_PATH = config["SECTIONSLIST_PATH"]
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]
        self.INTERVAL_LENGTH_MIN = config["INTERVAL_LENGTH_MIN"]

    def process_events(self) -> pd.DataFrame:
        # Import Eventlist
        eventlist_dict = JsonParser.from_dict(self.EVENTLIST_PATH)

        # Create DataFrames for events
        # Parse Eventlist to DataFrame
        events_df = PandasDataFrameParser.from_dict(
            eventlist_dict["event_list"]
        ).sort_values(["frame_number"])

        # Set timeformat (funcionality not included in Parser, TODO?)
        events_df["occurrence"] = pd.to_datetime(
            events_df["occurrence"], format="%Y-%m-%d %H:%M:%S.%f"
        )

        # Filter by start time
        if self.FROM_TIME != "":
            from_time_formatted = pd.to_datetime(self.FROM_TIME)
            events_df = events_df[events_df["occurrence"] >= from_time_formatted]

        # Filter by end time
        if self.TO_TIME != "":
            to_time_formatted = pd.to_datetime(self.TO_TIME)
            events_df = events_df[events_df["occurrence"] < to_time_formatted]

        # Filter events for classes and sections and delete single intersections
        events_df = events_df[
            (events_df["section_id"].isin(self.FILTER_SECTION))
            & (events_df["road_user_type"].isin(self.FILTER_CLASS))
        ]

        valid_road_user_ids = (
            events_df.groupby("road_user_id").count()["frame_number"].reset_index()
        )
        valid_road_user_ids = valid_road_user_ids[
            valid_road_user_ids["frame_number"] > 1
        ]["road_user_id"]

        events_df = events_df[events_df["road_user_id"].isin(valid_road_user_ids)]

        return events_df.sort_values(["road_user_id", "occurrence"])
