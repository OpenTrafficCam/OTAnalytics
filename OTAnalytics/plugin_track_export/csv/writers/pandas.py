from pathlib import Path
from typing import cast

from pandas import DataFrame

from OTAnalytics.domain import track
from OTAnalytics.plugin_datastore.track_store import PandasDataFrameProvider


def set_column_order(dataframe: DataFrame) -> DataFrame:
    desired_columns_order = [
        track.TRACK_ID,
        track.CLASSIFICATION,
        track.CONFIDENCE,
        track.X,
        track.Y,
        track.W,
        track.H,
        track.FRAME,
        track.OCCURRENCE,
        track.INTERPOLATED_DETECTION,
        track.VIDEO_NAME,
        track.INPUT_FILE,
    ]
    return dataframe[
        desired_columns_order
        + [col for col in dataframe.columns if col not in desired_columns_order]
    ]


class PandasTrackDatasetCsvWriter:
    def supports(self, dataset: object) -> bool:
        return isinstance(dataset, PandasDataFrameProvider)

    def write(self, dataset: object, output_path: Path, append: bool) -> None:
        pandas_dataset = cast(PandasDataFrameProvider, dataset)
        dataframe = pandas_dataset.get_data().reset_index()
        dataframe = set_column_order(dataframe)
        dataframe.to_csv(
            output_path,
            index=False,
            header=not append,
            mode="a" if append else "w",
        )
