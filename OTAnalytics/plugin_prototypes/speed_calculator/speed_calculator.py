# % Import libraries and modules
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px

from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser
from OTAnalytics.plugin_prototypes.counter.counter import Counter

# import plotly.express as px


class SpeedCalculator:
    """Class to calculate and plot average speeds for flows between two sections
    for one camera view.

    Args:
        config (dict): Dict that stores information about: time format,
        file path to an *.otflow file, start and end time, interval
        lenght in minutes and a dict of names for the different directions.
        events (pd.DataFrame): _description_
        filter_sections (list, optional): Get speeds only for certain sections.
        Has to be a minimum of two sections. Defaults to [] (all sections are
        included).
        filter_directions (list, optional): Get speeds only for certain directions.
        Defaults to [] (all directions are included).
        filter_classes (list, optional): Get speeds only for certain road user types.
        Defaults to [] (all road users are included).
    """

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
            filter_sections, filter_classes, both_timestamps=True
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
        """Calculate average speeds for each flow between two sections. **Note: only
        flows that have distances provided within the plugin_data of the *.otflow file
        will be considered!**

        Args:
            return_table (bool, optional): When True, returns the dataframe. Otherwise,
            the dataframe is only stored in SpeedCalculator class for plotting.
            Defaults to True.

        Returns:
            pd.DataFrame: Pandas dataframe containing each movement as returned by
            the ´get_flows´ function of the Counter class with average speed.
        """
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
        row: Optional[str] = None,
        section_name: str = "",
        nbins: int = 30,
    ) -> None:
        """Create one or more histograms for average speeds by road user class.

        Args:
            row (Optional[str], optional): Create multiple plots distiguished
            by any column of the Pandas dataframe. Defaults to None.
            section_name (str, optional): Name of the section for
            the plot titel. Defaults to "".
            nbins (int, optional): Number of bin used in the histogram plot.
            Defaults to 30.
        """
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
            color="road_user_type",
            # barnorm="overlay",
            nbins=nbins,
            histnorm="percent",
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
        row: Optional[str] = None,
        section_name: str = "",
    ) -> None:
        """Create one or more acetter plots of the average speed of each
        movement over the number of overall road users in the respective
        time interval.

        Args:
            row (Optional[str], optional): Create multiple plots distiguished
            by any column of the Pandas dataframe. Defaults to None.
            section_name (str, optional): Name of the section for
            the plot titel. Defaults to "".
        """
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
