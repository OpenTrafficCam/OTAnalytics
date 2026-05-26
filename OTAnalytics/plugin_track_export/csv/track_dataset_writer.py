from pathlib import Path
from typing import Protocol, Sequence

from OTAnalytics.plugin_track_export.csv.writers.domain import (
    DomainTrackDatasetCsvWriter,
)
from OTAnalytics.plugin_track_export.csv.writers.pandas import (
    PandasTrackDatasetCsvWriter,
)
from OTAnalytics.plugin_track_export.csv.writers.polars import (
    PolarsTrackDatasetCsvWriter,
)


class TrackDatasetCsvWriter(Protocol):
    def supports(self, dataset: object) -> bool: ...

    def write(self, dataset: object, output_path: Path, append: bool) -> None: ...


class ResolvingTrackDatasetCsvWriter:
    def __init__(self, writers: Sequence[TrackDatasetCsvWriter]) -> None:
        self._writers = writers

    def write(self, dataset: object, output_path: Path, append: bool) -> None:
        for writer in self._writers:
            if writer.supports(dataset):
                writer.write(dataset, output_path, append)
                return
        raise TypeError(
            f"No CSV writer found for dataset of type {type(dataset).__name__}."
        )


def create_default_track_dataset_csv_writer() -> ResolvingTrackDatasetCsvWriter:
    return ResolvingTrackDatasetCsvWriter(
        [
            PolarsTrackDatasetCsvWriter(),
            PandasTrackDatasetCsvWriter(),
            DomainTrackDatasetCsvWriter(),
        ]
    )
