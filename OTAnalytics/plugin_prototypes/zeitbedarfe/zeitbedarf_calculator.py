# % Import libraries and modules
# import numpy as np
import pandas as pd

"""from OTAnalytics.plugin_parser.otanalytics_parser import (
    JsonParser,
    PandasDataFrameParser,
)"""
from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser

# from OTAnalytics.plugin_prototypes.counter.event_counter import CountsProcessor
# from OTAnalytics.plugin_prototypes.event_processor.event_processor
# import EventProcessor


class ZeitbedarfsProcessor:
    def __init__(self, config: dict, events: pd.DataFrame) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]
        self.INTERVAL_LENGTH_MIN = config["INTERVAL_LENGTH_MIN"]
        self.SECTIONSLIST_PATH = config["SECTIONSLIST_PATH"]
        self.EVENTS = events

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(self.SECTIONSLIST_PATH)

        self.SIGNALPROG = pd.read_csv(config["SIGNALPROG_PATH"])

        if self.FROM_TIME != "":
            from_time_formatted = pd.to_datetime(self.FROM_TIME)
            events = events[events["occurrence"] >= from_time_formatted]
            start_time = from_time_formatted
        else:
            start_time = events.loc[0, "occurrence"]

        # Filter by end time
        if self.TO_TIME != "":
            to_time_formatted = pd.to_datetime(self.TO_TIME)
            events = events[events["occurrence"] < to_time_formatted]
            end_time = to_time_formatted
        else:
            end_time = events.loc[len(events) - 1, "occurrence"]

        self.INTERVALS = pd.date_range(
            start_time,
            end_time - pd.Timedelta("1s"),
            freq=f"{self.INTERVAL_LENGTH_MIN}min",
        )
