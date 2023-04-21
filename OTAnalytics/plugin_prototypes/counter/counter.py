# % Import libraries and modules
from pathlib import Path

import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
from mpl_chord_diagram import chord_diagram

from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser


class Counter:
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

    def get_flows(self, all_timestamps: bool = False) -> pd.DataFrame:
        # Create counting table
        # Get direction for each track (first and last event!)
        events = self.EVENTS.sort_values(["road_user_id", "occurrence"])
        events["section_id2"] = events["section_id"]
        if all_timestamps:
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

        return flows_section

    def create_counting_table(
        self,
        filter_sections: list = [],
        filter_directions: list = [],
        filter_classes: list = [],
        return_table: bool = True,
    ) -> pd.DataFrame:
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

    def convert_flow_table_SH(
        self,
        flows: pd.DataFrame,
        flow_names: dict,
        mode_mapper: dict,
        aggregated: bool = False,
    ) -> pd.DataFrame:
        ret_table = pd.DataFrame()
        for flow, value in flow_names.items():
            tmp_flows = flows[
                (flows["from_section"] == value["from"])
                & (flows["to_section"] == value["to"])
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

    def create_flow_table(self, return_table: bool = True) -> pd.DataFrame:
        if not hasattr(self, "FLOWS"):
            self.FLOWS = self.get_flows()
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

    def plot_counts(self, intersection_name: str = "") -> None:
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

    def plot_flows(self) -> None:
        nodes = [section.id for section in self.SECTIONS]

        flows = self.FLOW_TABLE
        time_intervals = self.INTERVALS

        road_user_types = self.FLOWS["road_user_type"].unique()

        # Plot flows
        fig, axs = plt.subplots(
            len(time_intervals),
            len(road_user_types),
            dpi=300,
            figsize=(5 * len(time_intervals), 5 * len(road_user_types)),
        )
        for i in range(0, len(time_intervals)):
            for j in range(0, len(road_user_types)):
                if len(road_user_types) > 1 and len(time_intervals) > 1:
                    axs_ij = axs[i, j]
                elif len(road_user_types) > 1 and len(time_intervals) == 1:
                    axs_ij = axs[j]
                elif len(road_user_types) == 1 and len(time_intervals) > 1:
                    axs_ij = axs[i]
                flow_matrix = pd.pivot_table(
                    flows[
                        (flows["time_interval"] == time_intervals[i])
                        & (flows["road_user_type"] == road_user_types[j])
                    ],
                    index="from_section",
                    columns="to_section",
                    values="n_vehicles",
                    aggfunc="sum",
                    sort=False,
                ).to_numpy(na_value=0)

                chord_diagram(
                    flow_matrix,
                    names=nodes,
                    order=None,
                    width=0.05,
                    pad=30.0,
                    gap=0.03,
                    chordwidth=0.5,
                    ax=axs_ij,
                    colors=None,
                    cmap=None,
                    alpha=0.6,
                    use_gradient=False,
                    chord_colors=None,
                    start_at=45,
                    extent=360,
                    directed=True,
                    show=False,
                )
                times = self._set_time_format(
                    pd.Series(time_intervals), self.TIME_FORMAT
                )
                axs_ij.set_title(
                    f"Time Interval: {times[i]},\nRoad User: {road_user_types[j]}",
                    loc="Left",
                )
