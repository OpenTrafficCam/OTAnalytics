from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pandas
from pandas.testing import assert_frame_equal

from OTAnalytics.application.config import CONTEXT_FILE_TYPE_TRACKS
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.track_export import (
    TrackExportSpecification,
    TrackFileFormat,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_parser.track_export import CsvTrackExport
from OTAnalytics.plugin_track_export.csv.track_dataset_writer import (
    ResolvingTrackDatasetCsvWriter,
)
from OTAnalytics.plugin_track_export.csv.writers.pandas import set_column_order
from tests.utils.builders.track_builder import TrackBuilder, append_sample_data


class TestCsvTrackExport:
    def test_export(
        self,
        track_builder: TrackBuilder,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        test_data_tmp_dir: Path,
    ) -> None:
        mock_tracks_metadata = Mock(spec=TracksMetadata)
        mock_tracks_metadata.to_dict.return_value = {"tracks": "metadata"}
        mock_videos_metadata = Mock(spec=VideosMetadata)
        mock_videos_metadata.to_dict.return_value = {"videos": "metadata"}
        track_builder = append_sample_data(track_builder)
        track_repository = Mock(spec=TrackRepository)
        track_dataset = PandasTrackDataset.from_list(
            tracks=[track_builder.build_track()],
            track_geometry_factory=track_geometry_factory,
        )
        track_repository.get_all.return_value = track_dataset
        use_case = CsvTrackExport(
            track_repository, mock_tracks_metadata, mock_videos_metadata
        )
        export_file_stem = "exported_tracks"
        actual_file = test_data_tmp_dir / f"{export_file_stem}.tracks.csv"
        specification = TrackExportSpecification(
            export_directory=test_data_tmp_dir,
            export_filename_stem=export_file_stem,
            export_format=[TrackFileFormat.CSV],
            export_mode=OVERWRITE,
        )

        use_case.export(specification=specification)

        actual = pandas.read_csv(
            actual_file,
            dtype={track.TRACK_ID: object, track.ORIGINAL_TRACK_ID: object},
            parse_dates=[track.OCCURRENCE],
        )
        expected = set_column_order(track_dataset.get_data().reset_index())
        assert sorted(actual.columns.tolist()) == sorted(expected.columns.tolist())
        assert_frame_equal(actual, expected)

    def test_export_preserves_filename_stem_with_multiple_dots(
        self,
        track_builder: TrackBuilder,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        test_data_tmp_dir: Path,
    ) -> None:
        """Regression test for OP#9548.

        When the filename stem contains multiple dots, all output files
        (.tracks.csv, .tracks_metadata.json, .videos_metadata.json) must
        preserve the full stem.
        """
        mock_tracks_metadata = Mock(spec=TracksMetadata)
        mock_tracks_metadata.to_dict.return_value = {"tracks": "metadata"}
        mock_videos_metadata = Mock(spec=VideosMetadata)
        mock_videos_metadata.to_dict.return_value = {"videos": "metadata"}
        track_builder = append_sample_data(track_builder)
        track_repository = Mock(spec=TrackRepository)
        track_dataset = PandasTrackDataset.from_list(
            tracks=[track_builder.build_track()],
            track_geometry_factory=track_geometry_factory,
        )
        track_repository.get_all.return_value = track_dataset
        use_case = CsvTrackExport(
            track_repository, mock_tracks_metadata, mock_videos_metadata
        )
        stem = "video.00000_2025-08-28_15-00-00"
        specification = TrackExportSpecification(
            export_directory=test_data_tmp_dir,
            export_filename_stem=stem,
            export_format=[TrackFileFormat.CSV],
            export_mode=OVERWRITE,
        )

        use_case.export(specification=specification)

        assert (test_data_tmp_dir / f"{stem}.tracks.csv").exists()
        assert (test_data_tmp_dir / f"{stem}.tracks_metadata.json").exists()
        assert (test_data_tmp_dir / f"{stem}.videos_metadata.json").exists()


class TestCsvTrackExportDelegation:
    def test_export_delegates_csv_writing_to_injected_writer(
        self, test_data_tmp_dir: Path
    ) -> None:
        given = setup_default_csv_track_export(
            create_given_csv_track_export(test_data_tmp_dir)
        )
        target = create_target_csv_track_export(given)
        dataset = Mock()
        given.track_repository.get_all.return_value = dataset
        specification = TrackExportSpecification(
            export_directory=given.export_directory,
            export_filename_stem=given.export_filename_stem,
            export_format=[TrackFileFormat.CSV],
            export_mode=OVERWRITE,
        )

        target.export(specification=specification)

        expected_output_path = (
            given.export_directory
            / f"{given.export_filename_stem}.{CONTEXT_FILE_TYPE_TRACKS}.csv"
        )
        given.csv_writer.write.assert_called_once_with(
            dataset, expected_output_path, False
        )


@dataclass
class GivenCsvTrackExport:
    track_repository: Mock
    tracks_metadata: Mock
    videos_metadata: Mock
    csv_writer: Mock
    export_directory: Path
    export_filename_stem: str


def create_given_csv_track_export(tmp_path: Path) -> GivenCsvTrackExport:
    track_repository = Mock(spec=TrackRepository)
    tracks_metadata = Mock(spec=TracksMetadata)
    tracks_metadata.to_dict.return_value = {"tracks": "metadata"}
    videos_metadata = Mock(spec=VideosMetadata)
    videos_metadata.to_dict.return_value = {"videos": "metadata"}
    csv_writer = Mock(spec=ResolvingTrackDatasetCsvWriter)
    return GivenCsvTrackExport(
        track_repository=track_repository,
        tracks_metadata=tracks_metadata,
        videos_metadata=videos_metadata,
        csv_writer=csv_writer,
        export_directory=tmp_path,
        export_filename_stem="exported_tracks",
    )


def setup_default_csv_track_export(
    given: GivenCsvTrackExport,
) -> GivenCsvTrackExport:
    return given


def create_target_csv_track_export(given: GivenCsvTrackExport) -> CsvTrackExport:
    return CsvTrackExport(
        given.track_repository,
        given.tracks_metadata,
        given.videos_metadata,
        given.csv_writer,
    )
