from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import polars as pl
import pytest

from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsTrackDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_track_export.csv.track_dataset_writer import (
    ResolvingTrackDatasetCsvWriter,
    TrackDatasetCsvWriter,
)
from OTAnalytics.plugin_track_export.csv.writers.domain import (
    DomainTrackDatasetCsvWriter,
)
from OTAnalytics.plugin_track_export.csv.writers.pandas import (
    PandasTrackDatasetCsvWriter,
)
from OTAnalytics.plugin_track_export.csv.writers.polars import (
    PolarsTrackDatasetCsvWriter,
)
from tests.utils.builders.track_builder import TrackBuilder, append_sample_data


@dataclass
class GivenResolving:
    supporting_writer: Mock
    non_supporting_writer: Mock
    dataset: Mock
    output_path: Path


def create_given_resolving(tmp_path: Path) -> GivenResolving:
    return GivenResolving(
        supporting_writer=Mock(spec=TrackDatasetCsvWriter),
        non_supporting_writer=Mock(spec=TrackDatasetCsvWriter),
        dataset=Mock(),
        output_path=tmp_path / "out.csv",
    )


def setup_default_resolving(given: GivenResolving) -> GivenResolving:
    given.supporting_writer.supports.return_value = True
    given.non_supporting_writer.supports.return_value = False
    return given


def create_target_resolving(given: GivenResolving) -> ResolvingTrackDatasetCsvWriter:
    return ResolvingTrackDatasetCsvWriter(
        [given.non_supporting_writer, given.supporting_writer]
    )


class TestResolvingTrackDatasetCsvWriter:
    def test_selects_first_supporting_writer(self, tmp_path: Path) -> None:
        given = setup_default_resolving(create_given_resolving(tmp_path))
        target = create_target_resolving(given)

        target.write(given.dataset, given.output_path, append=False)

        given.supporting_writer.write.assert_called_once_with(
            given.dataset, given.output_path, False
        )
        given.non_supporting_writer.write.assert_not_called()

    def test_skips_non_supporting_writers(self, tmp_path: Path) -> None:
        given = setup_default_resolving(create_given_resolving(tmp_path))
        target = create_target_resolving(given)

        target.write(given.dataset, given.output_path, append=False)

        given.non_supporting_writer.write.assert_not_called()

    def test_raises_type_error_for_unsupported_dataset(self, tmp_path: Path) -> None:
        non_supporting = Mock(spec=TrackDatasetCsvWriter)
        non_supporting.supports.return_value = False
        target = ResolvingTrackDatasetCsvWriter([non_supporting])

        with pytest.raises(TypeError, match="No CSV writer found"):
            target.write(Mock(), tmp_path / "out.csv", append=False)


# ---------------------------------------------------------------------------
# PolarsTrackDatasetCsvWriter
# ---------------------------------------------------------------------------

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


@dataclass
class GivenPolars:
    dataset: Mock
    raw_df: pl.DataFrame
    output_path: Path


def create_given_polars(tmp_path: Path) -> GivenPolars:
    raw_df = pl.DataFrame(_POLARS_COLUMNS)
    dataset = Mock()
    dataset.get_data.return_value = raw_df
    return GivenPolars(dataset=dataset, raw_df=raw_df, output_path=tmp_path / "out.csv")


def setup_default_polars(given: GivenPolars) -> GivenPolars:
    return given


def create_target_polars(given: GivenPolars) -> PolarsTrackDatasetCsvWriter:
    return PolarsTrackDatasetCsvWriter()


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

    def test_write_drops_row_id(self, tmp_path: Path) -> None:
        given = setup_default_polars(create_given_polars(tmp_path))
        target = create_target_polars(given)

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert "row_id" not in result.columns

    def test_write_includes_header_when_not_appending(self, tmp_path: Path) -> None:
        given = setup_default_polars(create_given_polars(tmp_path))
        target = create_target_polars(given)

        target.write(given.dataset, given.output_path, append=False)

        with open(given.output_path) as f:
            first_line = f.readline()
        assert track.TRACK_ID in first_line

    def test_write_excludes_header_when_appending(self, tmp_path: Path) -> None:
        given = setup_default_polars(create_given_polars(tmp_path))
        target = create_target_polars(given)

        target.write(given.dataset, given.output_path, append=False)
        target.write(given.dataset, given.output_path, append=True)

        result = pd.read_csv(given.output_path)
        assert len(result) == 2

    def test_write_applies_column_ordering(self, tmp_path: Path) -> None:
        given = setup_default_polars(create_given_polars(tmp_path))
        target = create_target_polars(given)

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert result.columns[0] == track.TRACK_ID


# ---------------------------------------------------------------------------
# PandasTrackDatasetCsvWriter
# ---------------------------------------------------------------------------


@dataclass
class GivenPandas:
    dataset: PandasTrackDataset
    output_path: Path


def create_given_pandas(
    track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    track_builder: TrackBuilder,
    tmp_path: Path,
) -> GivenPandas:
    track_builder = append_sample_data(track_builder)
    dataset = PandasTrackDataset.from_list(
        tracks=[track_builder.build_track()],
        track_geometry_factory=track_geometry_factory,
    )
    return GivenPandas(dataset=dataset, output_path=tmp_path / "out.csv")


def setup_default_pandas(given: GivenPandas) -> GivenPandas:
    return given


def create_target_pandas(given: GivenPandas) -> PandasTrackDatasetCsvWriter:
    return PandasTrackDatasetCsvWriter()


class TestPandasTrackDatasetCsvWriter:
    def test_supports_pandas_dataframe_provider(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        tmp_path: Path,
    ) -> None:
        given = setup_default_pandas(
            create_given_pandas(track_geometry_factory, track_builder, tmp_path)
        )
        writer = PandasTrackDatasetCsvWriter()
        assert writer.supports(given.dataset) is True

    def test_does_not_support_non_pandas_dataset(self) -> None:
        writer = PandasTrackDatasetCsvWriter()
        assert writer.supports(Mock()) is False

    def test_write_resets_index_into_columns(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        tmp_path: Path,
    ) -> None:
        given = setup_default_pandas(
            create_given_pandas(track_geometry_factory, track_builder, tmp_path)
        )
        target = create_target_pandas(given)

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert track.TRACK_ID in result.columns
        assert track.OCCURRENCE in result.columns

    def test_write_includes_header_when_not_appending(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        tmp_path: Path,
    ) -> None:
        given = setup_default_pandas(
            create_given_pandas(track_geometry_factory, track_builder, tmp_path)
        )
        target = create_target_pandas(given)

        target.write(given.dataset, given.output_path, append=False)

        with open(given.output_path) as f:
            first_line = f.readline()
        assert track.TRACK_ID in first_line

    def test_write_excludes_header_when_appending(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        tmp_path: Path,
    ) -> None:
        given = setup_default_pandas(
            create_given_pandas(track_geometry_factory, track_builder, tmp_path)
        )
        target = create_target_pandas(given)

        target.write(given.dataset, given.output_path, append=False)
        target.write(given.dataset, given.output_path, append=True)

        result = pd.read_csv(given.output_path)
        expected_row_count = 2 * len(given.dataset.get_data())
        assert len(result) == expected_row_count

    def test_write_applies_column_ordering(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        tmp_path: Path,
    ) -> None:
        given = setup_default_pandas(
            create_given_pandas(track_geometry_factory, track_builder, tmp_path)
        )
        target = create_target_pandas(given)

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert result.columns[0] == track.TRACK_ID


# ---------------------------------------------------------------------------
# DomainTrackDatasetCsvWriter
# ---------------------------------------------------------------------------


@dataclass
class GivenDomain:
    dataset: Mock
    track_mock: Mock
    detection_mock: Mock
    output_path: Path


def create_given_domain(tmp_path: Path) -> GivenDomain:
    detection_mock = Mock()
    detection_mock.to_dict.return_value = {
        track.TRACK_ID: "1",
        track.CLASSIFICATION: "car",
        track.CONFIDENCE: 0.9,
        track.X: 1.0,
        track.Y: 2.0,
        track.W: 10.0,
        track.H: 20.0,
        track.FRAME: 1,
        track.OCCURRENCE: "2023-01-01T00:00:00+00:00",
        track.INTERPOLATED_DETECTION: False,
        track.VIDEO_NAME: "vid.mp4",
        track.INPUT_FILE: "file.ottrk",
    }
    track_mock = Mock()
    track_mock.classification = "car"
    track_mock.detections = [detection_mock]

    dataset = Mock()
    dataset.as_list.return_value = [track_mock]

    return GivenDomain(
        dataset=dataset,
        track_mock=track_mock,
        detection_mock=detection_mock,
        output_path=tmp_path / "out.csv",
    )


def setup_default_domain(given: GivenDomain) -> GivenDomain:
    return given


def create_target_domain(given: GivenDomain) -> DomainTrackDatasetCsvWriter:
    return DomainTrackDatasetCsvWriter()


class TestDomainTrackDatasetCsvWriter:
    def test_supports_track_dataset(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        tmp_path: Path,
    ) -> None:
        track_builder = append_sample_data(track_builder)
        dataset = PandasTrackDataset.from_list(
            tracks=[track_builder.build_track()],
            track_geometry_factory=track_geometry_factory,
        )
        writer = DomainTrackDatasetCsvWriter()
        assert writer.supports(dataset) is True

    def test_does_not_support_plain_object(self) -> None:
        writer = DomainTrackDatasetCsvWriter()
        assert writer.supports(object()) is False

    def test_write_includes_track_classification(self, tmp_path: Path) -> None:
        given = setup_default_domain(create_given_domain(tmp_path))
        target = create_target_domain(given)

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert track.TRACK_CLASSIFICATION in result.columns
        assert result[track.TRACK_CLASSIFICATION].iloc[0] == "car"

    def test_write_calls_to_dict_on_detections(self, tmp_path: Path) -> None:
        given = setup_default_domain(create_given_domain(tmp_path))
        target = create_target_domain(given)

        target.write(given.dataset, given.output_path, append=False)

        given.detection_mock.to_dict.assert_called_once()

    def test_write_includes_header_when_not_appending(self, tmp_path: Path) -> None:
        given = setup_default_domain(create_given_domain(tmp_path))
        target = create_target_domain(given)

        target.write(given.dataset, given.output_path, append=False)

        with open(given.output_path) as f:
            first_line = f.readline()
        assert track.TRACK_ID in first_line

    def test_write_excludes_header_when_appending(self, tmp_path: Path) -> None:
        given = setup_default_domain(create_given_domain(tmp_path))
        target = create_target_domain(given)

        target.write(given.dataset, given.output_path, append=False)
        target.write(given.dataset, given.output_path, append=True)

        result = pd.read_csv(given.output_path)
        assert len(result) == 2
