# % Import libraries and modules
from pathlib import Path

import pandas as pd

from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser
from OTAnalytics.plugin_prototypes.counter.event_counter import CountsProcessor

# import plotly.express as px


class SpeedProcessor:
    def __init__(
        self, config: dict, events: pd.DataFrame, signal_time_offset: int = 0
    ) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(Path(config["SECTIONSLIST_PATH"]))

        events = events[events["event_type"] == "section-enter"].reset_index(drop=True)

        counts_processor = CountsProcessor(config, events)

        self.MOVEMENTS = counts_processor.get_flows(all_timestamps=True)

        self.COUNTING_TABLES = counts_processor.create_counting_table()
        self.DIRECTION_NAMES = config["DIRECTION_NAMES"]

    def calculate_speeds(self, return_table: bool = True) -> pd.DataFrame:
        from_sections = []
        to_sections = []
        distances = []

        for section in self.SECTIONS:
            if len(section.plugin_data["distances"]) > 0:
                for distance in section.plugin_data["distances"]:
                    from_sections.append(section.id)
                    to_sections.append(list(distance.keys())[0])
                    distances.append(list(distance.values())[0])
            else:
                continue

        section_distances = pd.DataFrame(
            {
                "from_section": from_sections,
                "to_section": to_sections,
                "distance": distances,
            }
        )

        movements = pd.merge(
            self.MOVEMENTS,
            section_distances,
            on=["from_section", "to_section"],
            how="left",
        )

        movements_dis = movements[~movements["distance"].isna()]

        movements_dis["speed"] = (
            movements_dis["distance"]
            / (
                movements_dis["occurrence_to"] - movements_dis["occurrence_from"]
            ).dt.total_seconds()
        )

        q = (
            (
                self.COUNTING_TABLES[
                    self.COUNTING_TABLES["direction"]
                    == self.DIRECTION_NAMES["first_to_last_section"]
                ]
                .groupby(["section_id", "time_interval"])
                .sum()
            )
            .reset_index()
            .rename({"section_id": "from_section"}, axis=1)
        )

        self.SPEED_TABLE = pd.merge(
            movements_dis,
            q,
            on=["from_section", "time_interval"],
            how="left",
        )

        if return_table:
            return self.SPEED_TABLE
