from pathlib import Path

import pandas as pd


class ExcelCountParser:
    def __init__(self, id_dict: dict, CONFIG: dict):
        self.path = Path(CONFIG["EXCEL_PATH"])
        self.id_to_class = id_dict["id_to_class"]
        self.id_flows = id_dict["id_flows"]
        self.CONFIG = CONFIG

    def _read_excel(self) -> pd.DataFrame:
        if self.path.is_file():
            excel_path = [self.path]
        else:
            excel_path = list(self.path.glob("*.xlsm"))

        countings = pd.DataFrame()

        for excel_file in excel_path:
            self.START_TIME = pd.to_datetime(
                str(pd.to_datetime(self.CONFIG["FROM_TIME"]).date())
                + str(excel_file).split(".")[0].split("_")[-1],
                format="%Y-%m-%d%H%M",
            )
            if self.START_TIME >= pd.to_datetime(self.CONFIG["FROM_TIME"]):
                countings_df = pd.read_excel(
                    excel_file,
                    sheet_name="Zaehler",
                    skiprows=range(1),
                    usecols=["Klasse", "Strom", "Zeitstempel"],
                )

                countings_df["Zeitstempel"] = self.START_TIME + pd.to_timedelta(
                    countings_df["Zeitstempel"], unit="s"
                )

                countings = pd.concat([countings, countings_df], axis=0)

        return countings.sort_values(["Zeitstempel"])

    def _formatting(self, excel_table: pd.DataFrame) -> pd.DataFrame:
        formatted_table = excel_table

        # Renaming columns to match column names in flow_table
        formatted_table.rename(
            columns={
                "Klasse": "road_user_type",
                "Zeitstempel": "time_interval",
            },
            inplace=True,
        )

        # Replacing vehicle class IDs by the proper vehicle names
        formatted_table["Fzg-Typ"] = formatted_table["road_user_type"].map(
            self.id_to_class
        )

        # Getting sections of origin and destination from "Strom"
        # in two different columns
        formatted_table["Strom-Bezeichnung"] = formatted_table["Strom"].map(
            self.id_flows
        )

        formatted_table["Anzahl"] = 1

        # Group by sections, time interval, and road user type
        formatted_table = (
            formatted_table.groupby(
                [
                    "Strom-Bezeichnung",
                    pd.Grouper(
                        freq=str(self.CONFIG["INTERVAL_LENGTH_MIN"]) + "min",
                        key="time_interval",
                    ),
                    "Fzg-Typ",
                ]
            )
            .count()
            .reset_index()
        )

        formatted_table["Datum"] = formatted_table["time_interval"].dt.strftime(
            "%d.%m.%Y"
        )
        formatted_table["Uhrzeit"] = formatted_table["time_interval"].dt.strftime(
            "%H:%M:%S"
        )

        return formatted_table.drop(
            ["road_user_type", "time_interval", "Strom"], axis=1
        )

    def excel_parser(self) -> pd.DataFrame:
        return self._formatting(self._read_excel())
