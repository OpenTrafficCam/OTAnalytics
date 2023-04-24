# % Import libraries and modules
from pathlib import Path

import pandas as pd
from pandas import DataFrame, read_json

import OTAnalytics.plugin_parser.otvision_parser as otvp


class PandasDataFrameParser:
    @staticmethod
    def from_json(f: Path) -> DataFrame:
        """Imports a json file and converts it to a pandas dataframe.

        Args:
            f (Path): Path to json file

        Returns:
            DataFrame: Data frame from the imported json file.
        """
        return read_json(f)

    @staticmethod
    def from_dict(d: dict, transpose: bool = False) -> DataFrame:
        """Converts a dict to a pandas dataframe.

        Args:
            d (dict): dict to convert
            transpose (bool, optional): Transposes the datafame if True.
            Defaults to False.

        Returns:
            DataFrame: Data from the dict as data frame.
        """
        df = DataFrame(d)
        if transpose:
            return df.transpose()
        return df


class EventParser:
    """Class to import and filter an *.otevents file.

    Args:
        config (dict): Dict that stores information about: time format, class and/or
        section filters, file paths to *.otevents and *.otflow files, start and end
        time and interval lenght in minutes.
    """

    def __init__(self, config: dict):
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FILTER_CLASS = config["FILTER_CLASS"]
        self.FILTER_SECTION = config["FILTER_SECTION"]
        self.EVENTLIST_PATH = Path(config["EVENTLIST_PATH"])
        self.SECTIONSLIST_PATH = Path(config["SECTIONSLIST_PATH"])
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]
        self.INTERVAL_LENGTH_MIN = config["INTERVAL_LENGTH_MIN"]

    def _import_eventlists(self) -> pd.DataFrame:
        if self.EVENTLIST_PATH.is_file():
            eventlist_path = [self.EVENTLIST_PATH]
        else:
            eventlist_path = list(Path(self.EVENTLIST_PATH).glob("*.otevents"))

        events = pd.DataFrame()

        for eventlist in eventlist_path:
            eventlist_dict = otvp._parse_bz2(eventlist)

            events_df = PandasDataFrameParser.from_dict(eventlist_dict["event_list"])

            events = pd.concat([events, events_df], axis=0)

        return events.sort_values(["occurrence"])

    def process_events(self) -> pd.DataFrame:
        """Function to generate a pandas dataframe with (filtered) single events from
        one or more *.otevent files.

        Returns:
            pd.DataFrame: Single events as pandas dataframe.
        """
        # Import Eventlist
        events_df = self._import_eventlists()

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

        # Filter events for classes

        if self.FILTER_CLASS != []:
            events_df = events_df[events_df["road_user_type"].isin(self.FILTER_CLASS)]

        # Filter events for sections
        if self.FILTER_SECTION != []:
            events_df = events_df[events_df["section_id"].isin(self.FILTER_SECTION)]

        valid_road_user_ids = (
            events_df.groupby("road_user_id").count()["frame_number"].reset_index()
        )
        valid_road_user_ids = valid_road_user_ids[
            valid_road_user_ids["frame_number"] > 1
        ]["road_user_id"]

        events_df = events_df[events_df["road_user_id"].isin(valid_road_user_ids)]

        if self.FROM_TIME != "":
            from_time_formatted = pd.to_datetime(self.FROM_TIME)
            events_df = events_df[events_df["occurrence"] >= from_time_formatted]
            start_time = from_time_formatted
        else:
            start_time = events_df.loc[0, "occurrence"]

        # Filter by end time
        if self.TO_TIME != "":
            to_time_formatted = pd.to_datetime(self.TO_TIME)
            events_df = events_df[events_df["occurrence"] < to_time_formatted]
            end_time = to_time_formatted
        else:
            end_time = events_df.loc[len(events_df) - 1, "occurrence"]

        self.INTERVALS = pd.date_range(
            start_time,
            end_time - pd.Timedelta("1s"),
            freq=f"{self.INTERVAL_LENGTH_MIN}min",
        )

        events_df["time_interval"] = (
            (
                events_df["occurrence"]
                - pd.TimedeltaIndex(
                    events_df["occurrence"].dt.minute % self.INTERVAL_LENGTH_MIN, "m"
                )
            )
            - pd.TimedeltaIndex(events_df["occurrence"].dt.second, "s")
            - pd.TimedeltaIndex(events_df["occurrence"].dt.microsecond, "microsecond")
        )

        return events_df.sort_values(["road_user_id", "occurrence"])
