# % Import libraries and modules
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px

from OTAnalytics.plugin_parser.otanalytics_parser import JsonParser
from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser

# from OTAnalytics.plugin_prototypes.event_processor.event_processor
# import EventProcessor


class ZeitbedarfsProcessor:
    def __init__(
        self, config: dict, events: pd.DataFrame, signal_time_offset: int = 0
    ) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]
        self.SIGTIMEOFFSET = signal_time_offset  # in milliseconds

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(Path(config["SECTIONSLIST_PATH"]))

        signalprog = pd.read_csv(Path(config["SIGNALPROG_PATH"]))
        signalprogmapper = JsonParser.from_dict(Path(config["SIGNALPROG_MAPPER_PATH"]))

        self.SIGNALEVENTS = self._reshape_signal_program_data(
            signalprog, signalprogmapper
        )

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

        # without explicit direction of the track at the section:
        # only first enter-section event. needs dummy sections
        # close to the real sections for each line section to take
        # account of broken tracks!
        events = (
            events.sort_values(["road_user_id", "occurrence"])
            .groupby(["road_user_id"])
            .first()
            .reset_index()
        )

        self.SECTIONEVENTS = events[
            events["event_type"] == "section-enter"
        ].reset_index(drop=True)

        self.SCENEEVENTS = events[events["event_type"] == "scene-enter"].reset_index(
            drop=True
        )

    def _reshape_signal_program_data(
        self, signalprog: pd.DataFrame, signalprogmapper: dict
    ) -> pd.DataFrame:
        signal_prog = signalprog[["d_time", "sig_name", "sig_status"]].rename(
            {
                "d_time": "occurrence",
                "sig_name": "section_id",
                "sig_status": "event_type",
            },
            axis=1,
        )

        signal_prog["occurrence"] = pd.to_datetime(
            signal_prog["occurrence"], format="%Y-%m-%d %H:%M:%S.%f"
        ) - pd.Timedelta(self.SIGTIMEOFFSET, "milliseconds")

        signal_prog["section_id"] = signal_prog["section_id"].map(
            signalprogmapper["signal_names_to_section_ids"]
        )
        signal_prog["event_type"] = (
            signal_prog["event_type"]
            .astype(str)
            .map(signalprogmapper["signal_status_to_event_types"])
        )

        signal_prog["road_user_type"] = "traffic_signal"

        return signal_prog

    # TODO: add time_interval
    def calculate_zbw(
        self, max_zb_value: float, return_table: bool = True
    ) -> pd.DataFrame:
        events_signal = self.SIGNALEVENTS
        events_section = self.SECTIONEVENTS

        events_queue_pos = pd.DataFrame()

        for section_id in events_signal["section_id"].unique():
            events_zb = (
                pd.concat(
                    [
                        events_section[events_section["section_id"] == section_id],
                        events_signal,
                    ]
                )
                .sort_values(["occurrence"])
                .reset_index(drop=True)
            )
            events_zb["time_diff"] = events_zb["occurrence"].diff()
            events_zb["time_diff_sec"] = events_zb["time_diff"].dt.total_seconds()

            u = 0
            for row in range(0, len(events_zb)):
                if events_zb.loc[row, "event_type"] == "signal-green":
                    a = 0
                    u += 1
                if events_zb.loc[row, "event_type"] == "signal-red":
                    a = 1
                if a == 1:
                    events_zb.loc[row, "rotfahrer"] = "Ja"
                else:
                    events_zb.loc[row, "rotfahrer"] = "Nein"
                events_zb.loc[row, "umlauf"] = u

            events_zb = events_zb[~events_zb["umlauf"].isna()]

            for u in events_zb["umlauf"].unique():
                events_tmp = events_zb[
                    (events_zb["umlauf"] == u)
                    & (events_zb["event_type"] == "section-enter")
                ].reset_index(drop=True)
                if len(events_tmp) > 0:
                    events_tmp["queue_position"] = range(1, len(events_tmp) + 1)
                    last_row = events_tmp[events_tmp["time_diff_sec"] > max_zb_value]
                    if len(last_row) > 0:
                        last_row = last_row.head(1).index[0]
                        events_tmp = events_tmp[0:last_row]
                    events_queue_pos = pd.concat([events_queue_pos, events_tmp])
                else:
                    continue

        self.ZBEVENTS = events_queue_pos[
            events_queue_pos["road_user_type"] != "traffic_signal"
        ]

        if return_table:
            return self.ZBEVENTS

    def _set_time_format(self, series: pd.Series, format: str) -> pd.Series:
        return series.map(lambda x: x.strftime(format))

    def plot_zb(
        self,
        color: Optional[str] = None,
        facet_col: Optional[str] = None,
        facet_row: Optional[str] = None,
        intersection_name: str = "",
        exclude_red_drivers: bool = True,
    ) -> None:
        events_zb = self.ZBEVENTS

        events_zb["time_interval"] = self._set_time_format(
            events_zb["time_interval"], self.TIME_FORMAT
        )

        if exclude_red_drivers:
            events_zb = events_zb[events_zb["rotfahrer"] == "Nein"]

        # % Create plot
        fig = px.box(
            events_zb,
            x="queue_position",
            y="time_diff_sec",
            color=color,
            facet_col=facet_col,
            facet_row=facet_row,
            facet_col_spacing=0.05,
            facet_row_spacing=0.1,
            height=800,
        )

        """fig.update_yaxes(
            title_text="Number of road users",
        )"""
        fig.update_layout(
            title=f"Zeitbedarfswerte an Section {intersection_name}",
            xaxis_title="Warteschlangenposition",
            yaxis_title="Zeitbedarf [s]",
            legend_title=color,
        )
        fig.show()
