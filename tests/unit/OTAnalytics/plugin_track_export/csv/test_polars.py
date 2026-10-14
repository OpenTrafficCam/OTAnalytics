from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import polars as pl

from OTAnalytics.domain import track
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsTrackDataset,
)
from OTAnalytics.plugin_track_export.csv.writers.polars import (
    PolarsTrackDatasetCsvWriter,
)

_POLARS_COLUMNS = {
    track.TRACK_ID: ["1"],
    track.CLASSIFICATION: ["car"],
    track.CONFIDENCE: [0.9],
    track.X: [1.0],
    track.Y: [2.0],
    track.W: [10.0],
    track.H: [20.0],
    track.FRAME: [1],
    track.OCCURRENCE: ["2023-01-01T00:00:00+00:00"],
    track.INTERPOLATED_DETECTION: [False],
    track.VIDEO_NAME: ["vid.mp4"],
    track.INPUT_FILE: ["file.ottrk"],
    track.TRACK_CLASSIFICATION: ["car"],
    "row_id": [0],
}


class TestPolarsTrackDatasetCsvWriter:
    def test_supports_polars_dataframe_provider(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        writer = PolarsTrackDatasetCsvWriter()
        dataset = PolarsTrackDataset.from_list([], track_geometry_factory)
        assert writer.supports(dataset) is True

    def test_does_not_support_non_polars_dataset(self) -> None:
        writer = PolarsTrackDatasetCsvWriter()
        assert writer.supports(Mock()) is False

    def test_write_drops_row_id(self, output_file_csv: Path) -> None:
        given = create_given(output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert "row_id" not in result.columns

    def test_write_includes_header_when_not_appending(
        self, output_file_csv: Path
    ) -> None:
        given = create_given(output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        with open(given.output_path) as f:
            first_line = f.readline()
        assert track.TRACK_ID in first_line

    def test_write_excludes_header_when_appending(self, output_file_csv: Path) -> None:
        given = create_given(output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)
        target.write(given.dataset, given.output_path, append=True)

        result = pd.read_csv(given.output_path)
        assert len(result) == 2

    def test_write_applies_column_ordering(self, output_file_csv: Path) -> None:
        given = create_given(output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert result.columns[0] == track.TRACK_ID


@dataclass
class Given:
    dataset: Mock
    raw_df: pl.DataFrame
    output_path: Path


def create_given(output_file: Path) -> Given:
    raw_df = pl.DataFrame(_POLARS_COLUMNS)
    dataset = Mock()
    dataset.get_data.return_value = raw_df
    return Given(dataset=dataset, raw_df=raw_df, output_path=output_file)


def setup_default(given: Given) -> Given:
    return given


def create_target() -> PolarsTrackDatasetCsvWriter:
    return PolarsTrackDatasetCsvWriter()
