from pathlib import Path
from typing import cast

import polars as pl

from OTAnalytics.domain import track
from OTAnalytics.plugin_datastore.polars_track_store import (
    PolarsDataFrameProvider,
    drop_row_id,
)


def set_column_order_polars(df: pl.DataFrame) -> pl.DataFrame:
    desired = [
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
    existing_desired = [c for c in desired if c in df.columns]
    remaining = [c for c in df.columns if c not in desired]
    return df.select(existing_desired + remaining)


class PolarsTrackDatasetCsvWriter:
    def supports(self, dataset: object) -> bool:
        return isinstance(dataset, PolarsDataFrameProvider)

    def write(self, dataset: object, output_path: Path, append: bool) -> None:
        polars_dataset = cast(PolarsDataFrameProvider, dataset)
        df = drop_row_id(polars_dataset.get_data())
        df = set_column_order_polars(df)
        write_mode = "ab" if append else "wb"
        with open(output_path, write_mode) as f:
            df.write_csv(f, include_header=not append)
