import sys
from pathlib import Path
from typing import Optional

import pandas
from pandas import DataFrame

svz_zuordnung_8_1 = {
    "bicyclist": "Fahrrad",
    "car": "Pkw",
    "motorcyclist": "Motorräder",
    "private_van": "Pkw",
    "bus": "Bus",
    "train": "Zug",
    "truck": "Lkw ohne Anhänger",
    "scooter_driver": "other",
    "cargo_bike_driver": "Fahrrad",
    "bicyclist_with_trailer": "Fahrrad",
    "car_with_trailer": "Pkw mit Anhänger",
    "private_van_with_trailer": "Pkw mit Anhänger",
    "truck_with_trailer": "Lkw mit Anhänger",
    "delivery_van": "Lieferwagen",
    "delivery_van_with_trailer": "Lieferwagen",
    "truck_with_semitrailer": "Sattelkraftfahrzeuge",
    "other": "other",
}

svz_zuordnung_aggregiert = {
    "bicyclist": "Fahrrad",
    "car": "LVm",
    "motorcyclist": "Krad",
    "private_van": "LVm",
    "bus": "Bus",
    "train": "Zug",
    "truck": "LoA",
    "scooter_driver": "other",
    "cargo_bike_driver": "Fahrrad",
    "bicyclist_with_trailer": "Fahrrad",
    "car_with_trailer": "LVm",
    "private_van_with_trailer": "LVm",
    "truck_with_trailer": "Lzg",
    "delivery_van": "LVm",
    "delivery_van_with_trailer": "LVm",
    "truck_with_semitrailer": "Lzg",
    "other": "other",
}

kfz_all = {
    "bicyclist": "0",
    "car": "1",
    "motorcyclist": "1",
    "private_van": "1",
    "bus": "1",
    "train": "1",
    "truck": "1",
    "scooter_driver": "1",
    "cargo_bike_driver": "0",
    "bicyclist_with_trailer": "0",
    "car_with_trailer": "1",
    "private_van_with_trailer": "1",
    "truck_with_trailer": "1",
    "delivery_van": "1",
    "delivery_van_with_trailer": "1",
    "truck_with_semitrailer": "1",
    "other": "0",
}

kfz_8_1 = {
    "Fahrrad": "0",
    "Pkw": "1",
    "Motorräder": "1",
    "Bus": "1",
    "Zug": "1",
    "Lkw ohne Anhänger": "1",
    "Pkw mit Anhänger": "1",
    "Lkw mit Anhänger": "1",
    "Lieferwagen": "1",
    "Sattelkraftfahrzeuge": "1",
    "other": "1",
}

svz_8_1_order = {
    "Kfz": "0",
    "Fahrrad": "9",
    "Pkw": "2",
    "Motorräder": "1",
    "Bus": "8",
    "Zug": "XX",
    "Lkw ohne Anhänger": "4",
    "Pkw mit Anhänger": "5",
    "Lkw mit Anhänger": "6",
    "Lieferwagen": "3",
    "Sattelkraftfahrzeuge": "7",
    "other": "X",
}

kfz_agg = {
    "Fahrrad": "0",
    "LVm": "1",
    "Krad": "1",
    "Bus": "1",
    "Zug": "1",
    "LoA": "1",
    "Lzg": "1",
    "other": "0",
}

svz_agg_order = {
    "Kfz": "0",
    "Fahrrad": "6",
    "LVm": "2",
    "Krad": "1",
    "Bus": "3",
    "Zug": "8",
    "LoA": "4",
    "Lzg": "5",
    "other": "X",
}


def analyse(path: str, output_suffix: str, input_suffix: str) -> None:
    folder = Path(path)

    loaded = []
    for file in folder.glob(f"*statistic{input_suffix}.csv"):
        data = pandas.read_csv(file, sep=",", encoding="utf8")
        data["file_name"] = file.stem
        loaded.append(data)

    all = pandas.concat(loaded)
    all["8_1"] = all["track_classification"].apply(
        lambda current: svz_zuordnung_8_1[current]
    )
    all["svz"] = all["track_classification"].apply(
        lambda current: svz_zuordnung_aggregiert[current]
    )
    all["A0"] = 1
    all.loc[all["in A1"], "A1"] = 1
    all.loc[~all["in A1"], "A1"] = 0
    all.loc[all["in A2"], "A2"] = 1
    all.loc[~all["in A2"], "A2"] = 0
    all.loc[all["in A3"], "A3"] = 1
    all.loc[~all["in A3"], "A3"] = 0

    all_file = folder / f"all.{output_suffix}.xlsx"
    svz_8_1_file = folder / f"svz_8_1.{output_suffix}.xlsx"
    svz_agg_file = folder / f"svz_agg.{output_suffix}.xlsx"

    create_aggregate(all, all_file, "track_classification", kfz_all)

    create_aggregate(all, svz_8_1_file, "8_1", kfz_8_1, svz_8_1_order)

    create_aggregate(all, svz_agg_file, "svz", kfz_agg, svz_agg_order)

    return


def create_aggregate(
    all: DataFrame,
    all_file: Path,
    classification: str,
    kfz: dict = {},
    order: Optional[dict] = {},
) -> None:
    all = all.loc[:, [classification, "A1", "A2", "A3", "A0"]]
    grouped: DataFrame = all.groupby([classification]).sum().reset_index()

    grouped["kfz"] = grouped[classification].apply(lambda current: kfz[current])

    kfz_agg = grouped.groupby("kfz").sum()
    kfz_agg = kfz_agg[~kfz_agg[classification].str.contains("Fahrrad")]
    kfz_agg.iloc[0, 0] = "Kfz"

    result = pandas.concat(
        [kfz_agg, grouped.loc[:, [classification, "A1", "A2", "A3", "A0"]]]
    )

    result["A4"] = result["A0"] - result["A3"]
    result["A1 in %"] = result["A1"] / result["A0"]
    result["A2 in %"] = result["A2"] / result["A0"]
    result["A3 in %"] = result["A3"] / result["A0"]
    result["A4 in %"] = result["A4"] / result["A0"]

    if order:
        result["order"] = result[classification].apply(lambda current: order[current])
        result.sort_values("order", inplace=True)
    result.loc[
        :,
        [
            classification,
            "A1",
            "A2",
            "A3",
            "A4",
            "A0",
            "A1 in %",
            "A2 in %",
            "A3 in %",
            "A4 in %",
        ],
    ].to_excel(all_file, index=False)


if __name__ == "__main__":
    print(sys.argv)
    analyse(sys.argv[1], output_suffix="all", input_suffix=".all")
    analyse(sys.argv[1], output_suffix="events", input_suffix="")
