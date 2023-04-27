# % Import libraries and modules
from pathlib import Path

import pandas as pd
import plotly.express as px

from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser


class Counter:
    """Class to create counting tables and plots for single sections
    or flows for one camera view.

    Args:
        config (dict): Dict that stores information about: time format,
        file path to an *.otflow file, start and end time, interval
        lenght in minutes and a dict of names for the different directions.
    """

    def __init__(self, config: dict, events: pd.DataFrame) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]
        self.INTERVAL_LENGTH_MIN = config["INTERVAL_LENGTH_MIN"]
        self.SECTIONSLIST_PATH = Path(config["SECTIONSLIST_PATH"])
        self.DIRECTION_NAMES = config["DIRECTION_NAMES"]
        self.EVENTS = events

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(self.SECTIONSLIST_PATH)

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

    def get_flows(
        self,
        filter_sections: list = [],
        filter_classes: list = [],
        both_timestamps: bool = False,
    ) -> pd.DataFrame:
        """Get a pandas dataframe of flows from a pandas dataframe of single events.

        Args:
            filter_sections (list, optional): Get flows only for certain sections.
            Has to be a minimum of two sections. Defaults to [] (all sections are
            included).
            filter_classes (list, optional): Get flows only for certain road user types.
            Defaults to [] (all road users are included).
            both_timestamps (bool, optional): Return also the timestamp of the
            intersection event with the second section of the flow. Defaults to False.

        Returns:
            pd.DataFrame: Pandas dataframe of single movements.
        """
        # Get direction for each track (first and last event!)
        events = self.EVENTS.sort_values(["road_user_id", "occurrence"])
        events["section_id2"] = events["section_id"]
        events = events[events["event_type"] == "section-enter"]
        if both_timestamps:
            events["occurrence2"] = events["occurrence"]

            flows_section = (
                events.pivot_table(
                    index="road_user_id",
                    values=[
                        "section_id",
                        "section_id2",
                        "occurrence",
                        "occurrence2",
                        "time_interval",
                        "road_user_type",
                    ],
                    aggfunc={
                        "section_id": "first",
                        "section_id2": "last",
                        "occurrence": "first",
                        "occurrence2": "last",
                        "time_interval": "first",
                        "road_user_type": "first",
                    },
                    fill_value=0,
                )
                .reset_index()
                .rename(
                    {
                        "section_id": "from_section",
                        "section_id2": "to_section",
                        "occurrence": "occurrence_from",
                        "occurrence2": "occurrence_to",
                    },
                    axis=1,
                )
            )

        else:
            flows_section = (
                events.pivot_table(
                    index="road_user_id",
                    values=[
                        "section_id",
                        "section_id2",
                        "occurrence",
                        "time_interval",
                        "road_user_type",
                    ],
                    aggfunc={
                        "section_id": "first",
                        "section_id2": "last",
                        "occurrence": "first",
                        "time_interval": "first",
                        "road_user_type": "first",
                    },
                    fill_value=0,
                )
                .reset_index()
                .rename(
                    {"section_id": "from_section", "section_id2": "to_section"},
                    axis=1,
                )
            )

        if filter_sections != []:
            flows_section = flows_section[
                (flows_section["from_section"].isin(filter_sections))
                & (flows_section["to_section"].isin(filter_sections))
            ]
        if filter_classes != []:
            flows_section = flows_section[
                (flows_section["road_user_type"].isin(filter_classes))
            ]

        return flows_section

    def create_counting_table(
        self,
        filter_sections: list = [],
        filter_directions: list = [],
        filter_classes: list = [],
        return_table: bool = True,
    ) -> pd.DataFrame:
        """Create a simple counting table for a section. The counting table is stored
        in the Counter class as well as returned as pandas dataframe (optional).

        Args:
            filter_sections (list, optional): Get flows only for certain sections.
            Has to be a minimum of two sections. Defaults to [] (all sections are
            included).
            filter_directions (list, optional): Get flows only for certain directions.
            Defaults to [] (all directions are included).
            filter_classes (list, optional): Get flows only for certain road user types.
            Defaults to [] (all road users are included).
            return_table (bool, optional): When True, returns the dataframe. Otherwise,
            the dataframe is only stored in Counter class for plotting.
            Defaults to True.

        Returns:
            pd.DataFrame: Pandas dataframe containing the number of road users for
            each time interval, section, direction and class.
        """
        if not hasattr(self, "FLOWS"):
            self.FLOWS = self.get_flows()
        counts_section_first_last = (
            self.FLOWS.groupby(
                [
                    pd.Grouper(key="occurrence", freq=f"{self.INTERVAL_LENGTH_MIN}Min"),
                    "from_section",
                    "road_user_type",
                ]
            )["road_user_id"]
            .count()
            .reset_index()
            .rename(
                {
                    "occurrence": "time_interval",
                    "road_user_id": "n_vehicles",
                    "from_section": "section_id",
                },
                axis=1,
            )
        )
        # TODO: direction_mapper when plugin_data can be parsed
        counts_section_first_last["direction"] = self.DIRECTION_NAMES[
            "first_to_last_section"
        ]

        counts_section_last_first = (
            self.FLOWS.groupby(
                [
                    pd.Grouper(key="occurrence", freq=f"{self.INTERVAL_LENGTH_MIN}Min"),
                    "to_section",
                    "road_user_type",
                ]
            )["road_user_id"]
            .count()
            .reset_index()
            .rename(
                {
                    "occurrence": "time_interval",
                    "road_user_id": "n_vehicles",
                    "to_section": "section_id",
                },
                axis=1,
            )
        )
        # TODO: direction_mapper when plugin_data can be parsed
        counts_section_last_first["direction"] = self.DIRECTION_NAMES[
            "last_to_first_section"
        ]

        counts_section = (
            pd.concat([counts_section_first_last, counts_section_last_first])
            .sort_values(["time_interval", "section_id", "direction", "road_user_type"])
            .reset_index(drop=True)
        )

        # Set time intervals
        intervals = self.INTERVALS

        # Import Sectionlist
        section_list = [section.id.id for section in self.SECTIONS]

        if filter_sections != []:
            section_list = [s for s in section_list if s in filter_sections]

        # Import directions
        direction_list = self.DIRECTION_NAMES.values()

        if filter_directions != []:
            direction_list = [d for d in direction_list if d in filter_directions]

        else:
            direction_list = self.DIRECTION_NAMES

        # Import Classes
        class_list = self.FLOWS["road_user_type"].unique()

        if filter_classes != []:
            class_list = [c for c in class_list if c in filter_classes]

        # Create table template
        counts_template = pd.DataFrame()
        for i in intervals:
            for j in direction_list:
                for k in class_list:
                    counts_to_add = pd.DataFrame(
                        {
                            "section_id": section_list,
                            "time_interval": i,
                            "direction": j,
                            "road_user_type": k,
                        }
                    )
                    counts_template = pd.concat([counts_template, counts_to_add])

        # Merge data and save
        self.COUNTING_TABLE = (
            pd.merge(
                counts_template,
                counts_section,
                on=["time_interval", "section_id", "road_user_type", "direction"],
                how="left",
            )
            .fillna(0)
            .sort_values(["time_interval", "section_id", "direction", "road_user_type"])
        )

        if return_table:
            return self.COUNTING_TABLE

    def convert_flow_table(
        self,
        flows: pd.DataFrame,
        flow_names: dict,
        mode_mapper: dict,
        aggregated: bool = False,
    ) -> pd.DataFrame:
        """Convert the format of a flow table to the format for the customer SH.

        Args:
            flows (pd.DataFrame): _description_
            flow_names (dict): _description_
            mode_mapper (dict): _description_
            aggregated (bool, optional): _description_. Defaults to False.

        Returns:
            pd.DataFrame: Pandas dataframe of flow table in the format
            for the customer SH.
        """
        ret_table = pd.DataFrame()
        for flow, value in flow_names.items():
            tmp_flows = flows[
                (flows["from_section"].isin(value["from"]))
                & (flows["to_section"].isin(value["to"]))
                & (flows["road_user_type"].isin(value["classes"]))
            ]
            if aggregated:
                new_flows = pd.DataFrame(
                    {
                        "Datum": tmp_flows["time_interval"].dt.strftime("%d.%m.%Y"),
                        "Uhrzeit": tmp_flows["time_interval"].dt.strftime("%H:%M:%S"),
                        "Strom-Bezeichnung": flow,
                        "Fzg-Typ": tmp_flows["road_user_type"],
                        "Anzahl": tmp_flows["n_vehicles"],
                    }
                )
            else:
                new_flows = pd.DataFrame(
                    {
                        "Datum": tmp_flows["occurrence"].dt.strftime("%d.%m.%Y"),
                        "Uhrzeit": tmp_flows["occurrence"].dt.strftime("%H:%M:%S"),
                        "Strom-Bezeichnung": flow,
                        "Fzg-Typ": tmp_flows["road_user_type"],
                    }
                )

            ret_table = pd.concat(
                [
                    ret_table,
                    new_flows,
                ]
            )

        ret_table = ret_table.sort_values(["Datum", "Uhrzeit"]).reset_index(drop=True)
        ret_table["Fzg-Typ"] = ret_table["Fzg-Typ"].map(mode_mapper)

        if aggregated:
            ret_table = (
                ret_table.groupby(["Datum", "Uhrzeit", "Strom-Bezeichnung", "Fzg-Typ"])
                .sum()
                .reset_index()
            )

        return ret_table

    def create_flow_table(
        self,
        filter_sections: list = [],
        filter_classes: list = [],
        return_table: bool = True,
    ) -> pd.DataFrame:
        """Create a simple flow table for the flows between all (filtered) sections.
        A flow is defined as a movement from a section to another section.
        The flow table is stored in the Counter class as well as
        returned as pandas dataframe (optional).

        Args:
            filter_sections (list, optional): Get flows only for certain sections.
            Has to be a minimum of two sections. Defaults to [] (all sections are
            included).
            filter_classes (list, optional): Get flows only for certain road user types.
            Defaults to [] (all road users are included).
            return_table (bool, optional): When True, returns the dataframe. Otherwise,
            the dataframe is only stored in Counter class for plotting.
            Defaults to True.

        Returns:
            pd.DataFrame: Pandas dataframe containing the number of road users for
            each time interval, flow and class.
        """
        if not hasattr(self, "FLOWS"):
            self.FLOWS = self.get_flows(filter_sections, filter_classes)
        flows_section = (
            self.FLOWS.groupby(
                [
                    pd.Grouper(key="occurrence", freq=f"{self.INTERVAL_LENGTH_MIN}Min"),
                    "from_section",
                    "to_section",
                    "road_user_type",
                ]
            )["road_user_id"]
            .count()
            .reset_index()
            .rename(
                {
                    "occurrence": "time_interval",
                    "road_user_id": "n_vehicles",
                },
                axis=1,
            )
        ).sort_values(["time_interval", "from_section", "to_section", "road_user_type"])

        # Set time intervals
        intervals = self.INTERVALS
        # Import Sectionlist
        section_list = [section.id.id for section in self.SECTIONS]

        if filter_sections != []:
            section_list = [s for s in section_list if s in filter_sections]

        # Import Classes
        class_list = self.FLOWS["road_user_type"].unique()

        if filter_classes != []:
            class_list = [c for c in class_list if c in filter_classes]

        # Create table template
        flows_template = pd.DataFrame()
        for i in intervals:
            for j in section_list:
                for k in self.FLOWS["road_user_type"].unique():
                    flows_to_add = pd.DataFrame(
                        {
                            "from_section": j,
                            "to_section": section_list,
                            "time_interval": i,
                            "road_user_type": k,
                        }
                    )
                    flows_template = pd.concat([flows_template, flows_to_add])

        # Merge data and save
        self.FLOW_TABLE = pd.merge(
            flows_template.reset_index(drop=True),
            flows_section,
            on=["time_interval", "from_section", "to_section", "road_user_type"],
            how="left",
        ).fillna(0)

        if return_table:
            return self.FLOW_TABLE

    def _set_time_format(self, series: pd.Series, format: str) -> pd.Series:
        return series.map(lambda x: x.strftime(format))

    def plot_counts(
        self, counts_section: pd.DataFrame = pd.DataFrame(), intersection_name: str = ""
    ) -> None:
        """Plot the counts for all (filtered) sections in a bar plot.
        The counting table needs to be created first using the
        ´create_counting_table´ function.

        Args:
            counts_section (pd.DataFrame, optional): Pandas dataframe of countings.
            If not provided, the counting table stored in the Counter class is used.
            Defaults to pd.DataFrame().
            intersection_name (str, optional): Name of the intersection for
            the plot titel. Defaults to "".
        """

        if len(counts_section) < 1:
            counts_section = self.COUNTING_TABLE

        # Set the time format for plotting
        counts_section["time_interval"] = self._set_time_format(
            counts_section["time_interval"], self.TIME_FORMAT
        )

        # % Create counting plot
        fig = px.bar(
            counts_section,
            x="time_interval",
            y="n_vehicles",
            color="road_user_type",
            barmode="stack",
            facet_col="direction",
            facet_row="section_id",
            facet_col_spacing=0.05,
            facet_row_spacing=0.2,
            height=len(counts_section["section_id"].unique()) * 400,
        )

        fig.update_layout(
            title=f"Counts at intersection {intersection_name}",
            yaxis_title="Number of road users",
            xaxis_title="Time of day",
            legend_title="Type of<br>road user",
        )
        fig.show()

    def plot_flows(
        self,
        flows_section: pd.DataFrame = pd.DataFrame(),
        intersection_name: str = "",
    ) -> None:
        """Plot the flows for all (filtered) sections in a bar plot.
        A flow table needs to be created first using the
        ´create_flow_table´ function.

        Args:
            flows_section (pd.DataFrame, optional): Pandas dataframe of flows. If not
            provided, the flow table stored in the Counter class is used.
            Defaults to pd.DataFrame().
            intersection_name (str, optional): Name of the intersection for
            the plot titel. Defaults to "".
        """
        if len(flows_section) < 1:
            flows_section = self.FLOW_TABLE

        # Set the time format for plotting
        flows_section["Datum, Uhrzeit"] = (
            flows_section["Datum"] + ", " + flows_section["Uhrzeit"]
        )

        # % Create counting plot
        fig = px.bar(
            flows_section,
            x="Datum, Uhrzeit",
            y="Anzahl",
            color="Fzg-Typ",
            barmode="stack",
            facet_row="Strom-Bezeichnung",
            facet_col_spacing=0.05,
            facet_row_spacing=0.2,
            height=len(flows_section["Strom-Bezeichnung"].unique()) * 400,
        )

        fig.show()
