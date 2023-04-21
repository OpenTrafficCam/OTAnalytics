# % Import libraries and modules
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px

from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser
from OTAnalytics.plugin_prototypes.counter.counter import Counter

# import plotly.express as px


class SpeedCalculator:
    def __init__(
        self,
        config: dict,
        events: pd.DataFrame,
        filter_sections: list = [],
        filter_directions: list = [],
        filter_classes: list = [],
    ) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(Path(config["SECTIONSLIST_PATH"]))

        events = events[events["event_type"] == "section-enter"].reset_index(drop=True)

        counts_processor = Counter(config, events)

        self.MOVEMENTS = counts_processor.get_flows(
            filter_sections, filter_classes, all_timestamps=True
        )

        self.COUNTING_TABLES = counts_processor.create_counting_table(
            filter_sections, filter_directions, filter_classes
        )
        self.DIRECTION_NAMES = config["DIRECTION_NAMES"]

    def _set_time_format(self, series: pd.Series, format: str) -> pd.Series:
        return series.map(lambda x: x.strftime(format))

    def calculate_speeds(
        self,
        return_table: bool = True,
    ) -> pd.DataFrame:
        from_sections = []
        to_sections = []
        distances = []

        for section in self.SECTIONS:
            if len(section.plugin_data["distances"]) > 0:
                for distance in section.plugin_data["distances"]:
                    from_sections.append(section.id.id)
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
        ) * 3.6

        q = (
            (
                self.COUNTING_TABLES.copy()[
                    self.COUNTING_TABLES["direction"]
                    == self.DIRECTION_NAMES["first_to_last_section"]
                ]
                .drop("road_user_type", axis=1)
                .groupby(["section_id", "time_interval", "direction"])
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

    def plot_v_hist(
        self,
        col: Optional[str] = None,
        row: Optional[str] = None,
        section_name: str = "",
        nbins: int = 30,
    ) -> None:
        speed_table = self.SPEED_TABLE.copy()

        # Set the time format for plotting
        speed_table["time_interval"] = self._set_time_format(
            speed_table["time_interval"], self.TIME_FORMAT
        )

        # % Create counting plot
        fig = px.histogram(
            speed_table,
            x="speed",
            barmode="relative",
            # barnorm="overlay",
            nbins=nbins,
            histnorm="percent",
            facet_col=col,
            facet_row=row,
            facet_col_spacing=0.05,
            facet_row_spacing=0.1,
            height=800,
        )

        fig.update_layout(
            title=f"Geschwindigkeiten an {section_name}",
            xaxis_title="Geschwindigkeit [km/h]",
            legend_title="Type of<br>road user",
        )
        fig.show()

    def plot_q_v(
        self,
        col: Optional[str] = None,
        row: Optional[str] = None,
        section_name: str = "",
    ) -> None:
        speed_table = self.SPEED_TABLE.copy()

        # Set the time format for plotting
        speed_table["time_interval"] = self._set_time_format(
            speed_table["time_interval"], self.TIME_FORMAT
        )

        # % Create counting plot
        fig = px.scatter(
            speed_table,
            x="n_vehicles",
            y="speed",
            color="road_user_type",
            facet_col=col,
            facet_row=row,
            facet_col_spacing=0.05,
            facet_row_spacing=0.1,
            height=800,
        )

        fig.update_layout(
            title=f"Q-V-Diagram für {section_name}",
            xaxis_title="Gesamtverkehrsstärke [Q_Kfz]",
            yaxis_title="Geschwindigkeit [km/h]",
            legend_title="Type of<br>road user",
        )
        fig.show()
