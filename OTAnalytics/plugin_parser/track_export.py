from OTAnalytics.application.config import CONTEXT_FILE_TYPE_TRACKS
from OTAnalytics.application.export_path_builder import build_export_path
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.track_export import (
    ExportTracks,
    TrackExportSpecification,
)
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_parser.json_parser import write_json
from OTAnalytics.plugin_track_export.csv.track_dataset_writer import (
    ResolvingTrackDatasetCsvWriter,
    create_default_track_dataset_csv_writer,
)


class CsvTrackExport(ExportTracks):
    """
    A CsvTrackExport exports tracks to .csv format.
    Moreover, TracksMetadata and VideosMetadata are exported in json format.
    Allows to either overwrite csv file or append tracks to existing csv file.

    Incrementally exporting tracks turns this CsvTrackExport into a
    stateful ExportTracks. TracksMetadata and VideosMetadata are incrementally merged
    until ExportMode.FLUSH is provided.
    (Cached metadata are not cleared upon flush,
    this exporter should not be reused afterwards!)
    """

    PRIMARY_SUFFIX = f".{CONTEXT_FILE_TYPE_TRACKS}.csv"
    TRACKS_METADATA_SUFFIX = ".tracks_metadata.json"
    VIDEOS_METADATA_SUFFIX = ".videos_metadata.json"

    def __init__(
        self,
        track_repository: TrackRepository,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        csv_writer: ResolvingTrackDatasetCsvWriter = (
            create_default_track_dataset_csv_writer()
        ),
    ) -> None:
        self._track_repository = track_repository
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata
        self._csv_writer = csv_writer

        self._iterative_tracks_metadata: dict = self._tracks_metadata.to_dict()
        self._iterative_videos_metadata: dict = self._videos_metadata.to_dict()

    def _update_iterative_metadata(self) -> None:
        self._tracks_metadata.merge_into_dict(self._iterative_tracks_metadata)
        self._videos_metadata.merge_into_dict(self._iterative_videos_metadata)

    def export(self, specification: TrackExportSpecification) -> None:
        self._update_iterative_metadata()

        append = specification.export_mode.is_subsequent_write()
        output_path = build_export_path(
            specification.export_directory,
            specification.export_filename_stem,
            self.PRIMARY_SUFFIX,
        )
        dataset = self._track_repository.get_all()
        self._csv_writer.write(dataset, output_path, append)

        if specification.export_mode.is_final_write():
            tracks_metadata_path = build_export_path(
                specification.export_directory,
                specification.export_filename_stem,
                self.TRACKS_METADATA_SUFFIX,
            )
            write_json(self._iterative_tracks_metadata, tracks_metadata_path)

            videos_metadata_path = build_export_path(
                specification.export_directory,
                specification.export_filename_stem,
                self.VIDEOS_METADATA_SUFFIX,
            )
            write_json(self._iterative_videos_metadata, videos_metadata_path)

            self._iterative_tracks_metadata.clear()
            self._iterative_videos_metadata.clear()
