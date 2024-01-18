import sys
from pathlib import Path

import pandas
from pandas import DataFrame


def analyse(path: str) -> None:
    folder = Path(path)
    output_file = folder / "all.xlsx"
    # events_file = folder / "events.csv"

    # events = pandas.read_csv(events_file)
    # track_ids = events.loc[
    #     events["event_type"] == "section-enter", "road_user_id"
    # ].unique()

    loaded = []
    for file in folder.glob("*statistic.csv"):
        data = pandas.read_csv(file, sep=",", encoding="utf8")
        data["file_name"] = file.stem
        loaded.append(data)

    all = pandas.concat(loaded)
    # all = all.loc[all["track_id"].isin(track_ids), :]
    # all.set_index(["file_name", "track_classification"], inplace=True)
    all["A0"] = 1
    all.loc[all["in A1"], "A1"] = 1
    all.loc[~all["in A1"], "A1"] = 0
    all.loc[all["in A2"], "A2"] = 1
    all.loc[~all["in A2"], "A2"] = 0
    all.loc[all["in A3"], "A3"] = 1
    all.loc[~all["in A3"], "A3"] = 0

    all = all.loc[:, ["track_classification", "A1", "A2", "A3", "A0"]]

    result: DataFrame = all.groupby(["track_classification"]).sum()
    result["A4"] = result["A0"] - result["A3"]
    result["A1 in %"] = result["A1"] / result["A0"]
    result["A2 in %"] = result["A2"] / result["A0"]
    result["A3 in %"] = result["A3"] / result["A0"]
    result["A4 in %"] = result["A4"] / result["A0"]

    result.loc[
        :, ["A1", "A2", "A3", "A4", "A0", "A1 in %", "A2 in %", "A3 in %", "A4 in %"]
    ].to_excel(output_file)

    return

    # pivot_len = all.pivot(
    #     index="file_name", columns="track_classification", values="detection_rate_len"
    # )
    # pivot_sum = all.pivot(
    #     index="file_name", columns="track_classification", values="detection_rate_sum"
    # )
    # pivot_max = all.pivot(
    #     index="file_name", columns="track_classification", values="detection_rate_max"
    # )
    #
    # axes = pivot_len.plot(linestyle="", marker="x", ylim=[0, 1])
    # figure = matplotlib.pyplot.gcf()
    # matplotlib.pyplot.xticks(rotation=90)
    # figure.savefig("all_len.png")
    #
    # axes = pivot_sum.plot(linestyle="", marker="x", ylim=[0, 1])
    # figure = matplotlib.pyplot.gcf()
    # matplotlib.pyplot.xticks(rotation=90)
    # figure.savefig("all_sum.png")
    #
    # axes = pivot_max.plot(linestyle="", marker="x", ylim=[0, 1])
    # figure = matplotlib.pyplot.gcf()
    # matplotlib.pyplot.xticks(rotation=90)
    # figure.savefig("all_max.png")


if __name__ == "__main__":
    print(sys.argv)
    analyse(sys.argv[1])
