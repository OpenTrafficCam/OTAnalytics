from pathlib import Path

import pandas as pd


class McMioParser:
    def __init__(self, CONFIG: dict, access_roads: dict):
        self.path = Path(CONFIG["MIO_COUNT_PATH"])
        self.CONFIG = CONFIG
        self.access_roads = access_roads
        self.START_TIME = pd.to_datetime(
            str(pd.to_datetime(self.CONFIG["FROM_TIME"]).date())
        )

    def _read_excel(self) -> pd.DataFrame:
        if self.path.is_file():
            excel_path = [self.path]
        else:
            excel_path = list(self.path.glob("*.xlsm"))

        countings = pd.DataFrame()

        for excel_file in excel_path:
            for ar in self.access_roads.keys():
                countings_tmp = pd.read_excel(
                    excel_file,
                    sheet_name=ar,
                    skiprows=range(3),
                )

                directions = [
                    i for i in self.access_roads.values() if self.access_roads[ar] != i
                ]

                for dir in directions:
                    col = countings_tmp.columns.get_indexer(
                        countings_tmp.columns[countings_tmp.columns == dir]
                    )[0]
                    col_range = list(range(col - 2, col + 4))
                    countings_ext = countings_tmp.iloc[:, [0] + col_range][
                        0 : int((60 / self.CONFIG["INTERVAL_LENGTH_MIN"]) * 24 + 1)
                    ]

                    countings_df = countings_ext.iloc[1:, :].reset_index(drop=True)
                    countings_df.columns = ["Zeitstempel"] + [
                        i.lstrip() for i in list(countings_ext.iloc[0, 1:])
                    ]

                    countings_df["from_section"] = self.access_roads[ar]
                    countings_df["to_section"] = dir
                    countings_df["Zeitstempel"] = self.START_TIME + pd.to_timedelta(
                        pd.Series(
                            [
                                self.CONFIG["INTERVAL_LENGTH_MIN"] * i
                                for i in range(
                                    0, int(60 / self.CONFIG["INTERVAL_LENGTH_MIN"] * 24)
                                )
                            ]
                        ),
                        unit="m",
                    )

                    countings = pd.concat([countings, countings_df], axis=0)

        return countings.sort_values(["Zeitstempel", "from_section", "to_section"])

    def _formatting(self, excel_table: pd.DataFrame) -> pd.DataFrame:
        formatted_table = pd.melt(
            excel_table,
            id_vars=["Zeitstempel", "from_section", "to_section"],
            value_vars=["RAD", "KRAD", "PKW & LFW", "LFW", "BUS", "LKW ab 3,5t"],
            var_name="Fzg-Typ",
            value_name="Anzahl",
        )

        # Renaming columns to match column names in flow_table
        formatted_table.rename(
            columns={
                "Zeitstempel": "time_interval",
            },
            inplace=True,
        )

        # Group by sections, time interval, and road user type
        formatted_table["Datum"] = formatted_table["time_interval"].dt.strftime(
            "%d.%m.%Y"
        )
        formatted_table["Uhrzeit"] = formatted_table["time_interval"].dt.strftime(
            "%H:%M:%S"
        )

        return (
            formatted_table.drop(["time_interval"], axis=1)
            .sort_values(["Datum", "Uhrzeit", "from_section", "to_section", "Fzg-Typ"])
            .reset_index(drop=True)
        )

    def excel_parser(self, aggregate: bool = False) -> pd.DataFrame:
        """Function to import Excel files from manual counts in the
        QuerPlaner/platomo format

        Args:
            aggregate (bool, optional): When set to True, aggregated counting
            data for each time interval set in the config dict are returned.
            Defaults to False.

        Returns:
            pd.DataFrame: Pandas dataframe of manual counting data in
            the SH format.
        """
        return self._formatting(self._read_excel())
