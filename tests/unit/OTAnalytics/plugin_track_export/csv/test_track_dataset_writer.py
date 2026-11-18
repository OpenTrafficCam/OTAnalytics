from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.plugin_track_export.csv.track_dataset_writer import (
    ResolvingTrackDatasetCsvWriter,
    TrackDatasetCsvWriter,
)


class TestResolvingTrackDatasetCsvWriter:
    def test_selects_first_supporting_writer(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = create_target(given)

        target.write(given.dataset, given.output_path, append=False)

        given.supporting_write_mock.assert_called_once_with(
            given.dataset, given.output_path, False
        )
        given.non_supporting_write_mock.assert_not_called()

    def test_skips_non_supporting_writers(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = create_target(given)

        target.write(given.dataset, given.output_path, append=False)

        given.non_supporting_write_mock.assert_not_called()

    def test_raises_type_error_for_unsupported_dataset(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = ResolvingTrackDatasetCsvWriter([given.non_supporting_writer])

        with pytest.raises(TypeError, match="No CSV writer found"):
            target.write(Mock(), tmp_path / "out.csv", append=False)


class NonSupportingTrackDatasetCsvWriter:
    def __init__(self, write_mock: Mock) -> None:
        self.write_mock = write_mock

    def supports(self, dataset: object) -> bool:
        return False

    def write(self, dataset: object, output_path: Path, append: bool) -> None:
        self.write_mock(dataset, output_path, append)


class SupportingTrackDatasetCsvWriter:
    def __init__(self, write_mock: Mock) -> None:
        self.write_mock = write_mock

    def supports(self, dataset: object) -> bool:
        return True

    def write(self, dataset: object, output_path: Path, append: bool) -> None:
        self.write_mock(dataset, output_path, append)


@dataclass
class Given:
    supporting_writer: TrackDatasetCsvWriter
    non_supporting_writer: TrackDatasetCsvWriter
    supporting_write_mock: Mock
    non_supporting_write_mock: Mock
    dataset: Mock
    output_path: Path


def create_given(tmp_path: Path) -> Given:
    supporting_write_mock = Mock()
    non_supporting_write_mock = Mock()
    return Given(
        supporting_writer=SupportingTrackDatasetCsvWriter(supporting_write_mock),
        non_supporting_writer=NonSupportingTrackDatasetCsvWriter(
            non_supporting_write_mock
        ),
        supporting_write_mock=supporting_write_mock,
        non_supporting_write_mock=non_supporting_write_mock,
        dataset=Mock(),
        output_path=tmp_path / "out.csv",
    )


def create_target(given: Given) -> ResolvingTrackDatasetCsvWriter:
    return ResolvingTrackDatasetCsvWriter(
        [given.non_supporting_writer, given.supporting_writer]
    )
