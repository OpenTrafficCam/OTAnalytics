from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pandas as pd

from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_track_export.csv.writers.pandas import (
    PandasTrackDatasetCsvWriter,
)
from tests.utils.builders.track_builder import TrackBuilder, append_sample_data


class TestPandasTrackDatasetCsvWriter:
    def test_supports_pandas_dataframe_provider(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        output_file_csv: Path,
    ) -> None:
        given = create_given(track_geometry_factory, track_builder, output_file_csv)

        writer = PandasTrackDatasetCsvWriter()
        assert writer.supports(given.dataset) is True

    def test_does_not_support_non_pandas_dataset(self) -> None:
        writer = PandasTrackDatasetCsvWriter()
        assert writer.supports(Mock()) is False

    def test_write_resets_index_into_columns(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        output_file_csv: Path,
    ) -> None:
        given = create_given(track_geometry_factory, track_builder, output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert track.TRACK_ID in result.columns
        assert track.OCCURRENCE in result.columns

    def test_write_includes_header_when_not_appending(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        output_file_csv: Path,
    ) -> None:
        given = create_given(track_geometry_factory, track_builder, output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        with open(given.output_path) as f:
            first_line = f.readline()
        assert track.TRACK_ID in first_line

    def test_write_excludes_header_when_appending(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        output_file_csv: Path,
    ) -> None:
        given = create_given(track_geometry_factory, track_builder, output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)
        target.write(given.dataset, given.output_path, append=True)

        result = pd.read_csv(given.output_path)
        expected_row_count = 2 * len(given.dataset.get_data())
        assert len(result) == expected_row_count

    def test_write_applies_column_ordering(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        output_file_csv: Path,
    ) -> None:
        given = create_given(track_geometry_factory, track_builder, output_file_csv)

        target = create_target()
        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert result.columns[0] == track.TRACK_ID


@dataclass
class Given:
    dataset: PandasTrackDataset
    output_path: Path


def create_given(
    track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    track_builder: TrackBuilder,
    output_file: Path,
) -> Given:
    track_builder = append_sample_data(track_builder)
    dataset = PandasTrackDataset.from_list(
        tracks=[track_builder.build_track()],
        track_geometry_factory=track_geometry_factory,
    )
    return Given(dataset=dataset, output_path=output_file)


def create_target() -> PandasTrackDatasetCsvWriter:
    return PandasTrackDatasetCsvWriter()
