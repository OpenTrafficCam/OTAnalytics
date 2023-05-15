# % Import libraries and modules
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import ujson

from OTAnalytics.plugin_parser.otvision_parser import OtsectionParser

ENCODING = "UTF-8"


class JsonParser:
    @staticmethod
    def from_dict(f: Path) -> dict:
        with open(f, "r", encoding=ENCODING) as out:
            eventlist_dict = ujson.load(out)
            return eventlist_dict


class ZeitbedarfsCalculator:
    """Class to calculate the Zeitbedarfswerte of the signalized intersection
    of one camera view.

    Args:
        config (dict): Dict that stores information about: time format,
        file path *.otflow file, start and end time and interval lenght in minutes.
        In addition, the file path to the signal programm events and the signal
        programm mapper file needs to be provided.

        events (pd.DataFrame): Pandas dataframe with events.
    """

    def __init__(self, config: dict, events: pd.DataFrame) -> None:
        self.TIME_FORMAT = config["TIME_FORMAT"]
        self.FROM_TIME = config["FROM_TIME"]
        self.TO_TIME = config["TO_TIME"]
        self.SIGTIMEOFFSET = config["SIGNAL_TIME_GAP"]  # in seconds
        self.MAX_ZB_VALUE = config["ZB_CUTOFF"]
        self.INTERVAL_LENGTH_MIN = config["INTERVAL_LENGTH_MIN"]
        self.CITY_NAME = config["CITY_NAME"]
        self.INTERSECTION_NAME = config["INTERSECTION_NAME"]

        otsection_parser = OtsectionParser()
        self.SECTIONS = otsection_parser.parse(Path(config["SECTIONSLIST_PATH"]))

        signalprog = pd.read_csv(Path(config["SIGNALPROG_PATH"]))
        signalprogmapper = JsonParser.from_dict(Path(config["SIGNALPROG_MAPPER_PATH"]))

        signal_events = self._reshape_signal_program_data(signalprog, signalprogmapper)

        signal_events = signal_events[
            signal_events["event_type"].isin(["signal-red-yellow", "signal-red"])
        ]
        signal_events = signal_events[
            (
                signal_events["intersection_name"].isin(
                    signalprogmapper["filter_intersection_name"]
                )
            )
            & (signal_events["section_id"].isin(signalprogmapper["filter_sig_name"]))
        ]
        if self.FROM_TIME != "":
            from_time_formatted = pd.to_datetime(self.FROM_TIME)
            events = events[events["occurrence"] >= from_time_formatted]
            signal_events = signal_events[
                signal_events["occurrence"] >= from_time_formatted
            ]
            start_time = from_time_formatted
        else:
            start_time = events.loc[0, "occurrence"]

        # Filter by end time
        if self.TO_TIME != "":
            to_time_formatted = pd.to_datetime(self.TO_TIME)
            events = events[events["occurrence"] < to_time_formatted]
            signal_events = signal_events[
                signal_events["occurrence"] < to_time_formatted
            ]
            end_time = to_time_formatted
        else:
            end_time = events.loc[len(events) - 1, "occurrence"]

        self.SIGNALEVENTS = signal_events

        self.INTERVALS = pd.date_range(
            start_time,
            end_time - pd.Timedelta("1s"),
            freq=f"{config['INTERVAL_LENGTH_MIN']}min",
        )

        # without explicit direction of the track at the section:
        # only first enter-section event. needs dummy sections
        # close to the real sections for each line section to take
        # account of broken tracks!
        section_events = (
            events[events["event_type"] == "section-enter"]
            .sort_values(["road_user_id", "occurrence"])
            .groupby(["road_user_id"])
            .first()
            .reset_index()
        )

        events["occurrence_day"] = events["occurrence"].dt.date
        section_events["occurrence_day"] = section_events["occurrence"].dt.date
        section_events["time_interval_t"] = section_events["time_interval"].dt.strftime(
            "%H:%M:%S"
        )

        scene_enter_events = (
            events[events["event_type"] == "enter-scene"]
            .reset_index(drop=True)
            .groupby(["occurrence_day", "road_user_id"])
            .first()
            .reset_index()
        )

        section_events = pd.merge(
            section_events,
            scene_enter_events[["road_user_id", "occurrence_day", "occurrence"]],
            on=["road_user_id", "occurrence_day"],
            how="left",
            suffixes=["", "_enter"],
        )

        section_events["time_scene_enter_to_section"] = (
            section_events["occurrence"] - section_events["occurrence_enter"]
        ).dt.total_seconds()

        section_events["max_fftime_scene_enter_to_section"] = section_events[
            "section_id"
        ].map(config["FF_TIME_ENTER_SCENE_TO_SECTION"])

        section_events = self._calculate_q(section_events)
        section_events["Stadt"] = self.CITY_NAME
        section_events["Knotenpunkt"] = self.INTERSECTION_NAME

        self.SECTIONEVENTS = section_events.reset_index(drop=True)

    def _calculate_q(self, section_events: pd.DataFrame) -> pd.DataFrame:
        interval_duration = self.INTERVAL_LENGTH_MIN
        q_factor = 60 / interval_duration
        q = (
            section_events[["section_id", "time_interval_t", "road_user_id"]]
            .groupby(["section_id", "time_interval_t"])
            .count()
            .rename({"road_user_id": "q"}, axis=1)
            .reset_index()
        )

        q["q"] = q["q"] * q_factor

        q["q"] = pd.cut(
            q["q"],
            bins=[0, 200, 400, 600, 800, 1000, 99999],
            labels=[
                "0-200 Fzg/h",
                "201-400 Fzg/h",
                "401-600 Fzg/h",
                "601-800 Fzg/h",
                "801-1000 Fzg/h",
                "über 1000 Fzg/h",
            ],
        ).astype(str)

        return pd.merge(
            section_events, q, on=["section_id", "time_interval_t"], how="left"
        )

    def _reshape_signal_program_data(
        self, signalprog: pd.DataFrame, signalprogmapper: dict
    ) -> pd.DataFrame:
        signal_prog = signalprog[
            ["intersection_name", "d_time", "sig_name", "sig_status"]
        ].rename(
            {
                "d_time": "occurrence",
                "sig_name": "section_id",
                "sig_status": "event_type",
            },
            axis=1,
        )

        signal_prog["occurrence"] = pd.to_datetime(
            signal_prog["occurrence"], format="%Y-%m-%d %H:%M:%S"
        ) + pd.Timedelta(self.SIGTIMEOFFSET, "seconds")

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

    def calculate_zbw(self, return_table: bool = True) -> pd.DataFrame:
        """Calculates the Zeitbedarfswert for each movement, if eligable.

        Args:
            return_table (bool, optional): When True, returns the dataframe. Otherwise,
            the dataframe is only stored in ZeitbedarfsCalculator class for plotting.
            Defaults to True.

        Returns:
            pd.DataFrame: Pandas dataframe containing each movement as returned by
            the ´get_flows´ function of the Counter class with the Zeitbedarfswert.
        """

        max_zb_value = self.MAX_ZB_VALUE
        events_signal = self.SIGNALEVENTS
        events_section = self.SECTIONEVENTS

        events_queue_pos = pd.DataFrame()

        for section_id in events_signal["section_id"].unique():
            events_zb = (
                pd.concat(
                    [
                        events_section[events_section["section_id"] == section_id],
                        events_signal[events_signal["section_id"] == section_id],
                    ]
                )
                .sort_values(["occurrence"])
                .reset_index(drop=True)
            )
            events_zb["time_diff"] = events_zb["occurrence"].diff()
            events_zb["time_diff_sec"] = events_zb["time_diff"].dt.total_seconds()
            events_zb["time_diff_sec"] = events_zb["time_diff_sec"].fillna(1)
            events_zb = events_zb[events_zb["time_diff_sec"] > 0].reset_index(drop=True)

            u = 0
            a = 0
            for row in range(0, len(events_zb)):
                if events_zb.loc[row, "event_type"] == "signal-red-yellow":
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

            # if first vehicle in queue is faster than max free flow time
            # OR if nth vehicle has a larger time difference to the vehicle before than
            # the max Zeitbedarfswert AND is faster than max free flow time
            # THEN delete this vehicle and the following vehiqcles from the umlauf

            for u in events_zb["umlauf"].unique():
                events_tmp = events_zb[
                    (events_zb["umlauf"] == u)
                    & (events_zb["event_type"] == "section-enter")
                ].reset_index(drop=True)
                if len(events_tmp) > 0:
                    if (
                        events_tmp.iloc[0]["max_fftime_scene_enter_to_section"]
                        > events_tmp.iloc[0]["time_scene_enter_to_section"]
                    ):
                        continue
                    last_row = events_tmp[
                        (events_tmp["time_diff_sec"] > max_zb_value)
                        & (
                            events_tmp["max_fftime_scene_enter_to_section"]
                            > events_tmp["time_scene_enter_to_section"]
                        )
                    ]
                    if len(last_row) > 0:
                        last_row = last_row.head(1).index[0] - 1
                        events_tmp = events_tmp.loc[0:last_row]
                    events_tmp["queue_position"] = range(1, len(events_tmp) + 1)
                    events_queue_pos = pd.concat([events_queue_pos, events_tmp])
                else:
                    continue
        # print(events_queue_pos)
        self.ZBEVENTS = events_queue_pos[
            (events_queue_pos["road_user_type"] != "traffic_signal")
            & (events_queue_pos["umlauf"] > 0)
        ].sort_values("occurrence")

        if return_table:
            return self.ZBEVENTS

    def _set_time_format(self, series: pd.Series, format: str) -> pd.Series:
        return series.map(lambda x: x.strftime(format))

    def plot_zb(
        self,
        events_zb: Optional[pd.DataFrame] = None,
        x: Optional[str] = "queue_position",
        xaxis_title: Optional[str] = "Warteschlangenposition",
        color: Optional[str] = None,
        category_orders: Optional[dict] = None,
        facet_col: Optional[str] = None,
        facet_row: Optional[str] = None,
        intersection_name: str = "",
        exclude_red_drivers: bool = True,
    ) -> None:
        """Create one or more box plots of the Zeitbedarfswerte of each
        movement over the queue position.

        Args:
            color (Optional[str], optional): Column name of the pandas dataframe
            for the color option of the box plot. Defaults to None.
            facet_col (Optional[str], optional): Column name of the pandas dataframe
            for the facet_col option of the box plot. Defaults to None.
            facet_row (Optional[str], optional): Column name of the pandas dataframe
            for the facet_row option of the box plot. Defaults to None.
            intersection_name (str, optional): Name of the intersection for
            the plot titel. Defaults to "".
            exclude_red_drivers (bool, optional): If set True, road users driving
            over a red signal will not be considered in the box plot. Defaults to True.
        """
        if events_zb is None:
            events_zb = self.ZBEVENTS

        events_zb["time_interval"] = self._set_time_format(
            events_zb["time_interval"], self.TIME_FORMAT
        )

        if exclude_red_drivers:
            events_zb = events_zb[events_zb["rotfahrer"] == "Nein"]

        # % Create plot
        fig = px.box(
            events_zb,
            x=x,
            y="time_diff_sec",
            color=color,
            category_orders=category_orders,
            facet_col=facet_col,
            facet_row=facet_row,
            facet_col_spacing=0.05,
            facet_row_spacing=0.1,
            height=800,
        )

        fig.update_layout(
            title=f"Zeitbedarfswerte an Section {intersection_name}",
            xaxis_title=xaxis_title,
            yaxis_title="Zeitbedarf [s]",
            legend_title=color,
        )
        fig.show()
