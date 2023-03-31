# % Import libraries and modules
# import numpy as np
import pandas as pd

"""from OTAnalytics.plugin_parser.otanalytics_parser import (
    JsonParser,
    PandasDataFrameParser,
)"""
from OTAnalytics.plugin_parser.otanalytics_parser import JsonParser
from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser

# from OTAnalytics.plugin_prototypes.counter.event_counter import CountsProcessor
# from OTAnalytics.plugin_prototypes.event_processor.event_processor
# import EventProcessor


class ZeitbedarfsProcessor:
    def __init__(self, config: dict, events: pd.DataFrame) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(config["SECTIONSLIST_PATH"])

        signalprog = pd.read_csv(config["SIGNALPROG_PATH"])
        signalprogmapper = JsonParser.from_dict(config["SIGNALPROG_MAPPER_PATH"])

        signalprog = self._reshape_signal_program_data(signalprog, signalprogmapper)

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
            freq=f"{config['INTERVAL_LENGTH_MIN']}min",
        )

        self.EVENTS = pd.concat([events, signalprog]).sort_values(["occurrence"])

    def _reshape_signal_program_data(
        self, signalprog: pd.DataFrame, signalprogmapper: dict
    ) -> pd.DataFrame:
        signal_prog = signalprog[["d_time", "sig_name", "sig_status"]].rename(
            {
                "d_time": "occurrence",
                "sig_name": "section_id",
                "sig_status": "event_type",
            }
        )

        signal_prog["section_id"] = signal_prog["section_id"].map(
            signalprogmapper["signal_names_to_section_ids"]
        )
        signal_prog["event_type"] = signal_prog["event_type"].map(
            signalprogmapper["signal_status_to_event_types"]
        )

        return signal_prog

        pass
