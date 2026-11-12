from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pandas as pd

from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_track_export.csv.writers.domain import (
    DomainTrackDatasetCsvWriter,
)
from tests.utils.builders.track_builder import TrackBuilder, append_sample_data


class TestDomainTrackDatasetCsvWriter:
    def test_supports_track_dataset(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_builder: TrackBuilder,
        output_file_csv: Path,
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

    def test_write_includes_track_classification(self, output_file_csv: Path) -> None:
        given = create_given(output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        result = pd.read_csv(given.output_path)
        assert track.TRACK_CLASSIFICATION in result.columns
        assert result[track.TRACK_CLASSIFICATION].iloc[0] == "car"

    def test_write_calls_to_dict_on_detections(self, output_file_csv: Path) -> None:
        given = create_given(output_file_csv)
        target = create_target()

        target.write(given.dataset, given.output_path, append=False)

        given.detection_mock.to_dict.assert_called_once()

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


@dataclass
class GivenDomain:
    dataset: Mock
    track_mock: Mock
    detection_mock: Mock
    output_path: Path


def create_given(output_file: Path) -> GivenDomain:
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
        output_path=output_file,
    )


def create_target() -> DomainTrackDatasetCsvWriter:
    return DomainTrackDatasetCsvWriter()
