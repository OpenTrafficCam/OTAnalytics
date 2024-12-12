from typing import Literal

from pandas import DataFrame

from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.track_export import (
    ExportTracks,
    TrackExportSpecification,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.track_store import PandasDataFrameProvider
from OTAnalytics.plugin_parser.json_parser import write_json


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

    def __init__(
        self,
        track_repository: TrackRepository,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
    ) -> None:
        self._track_repository = track_repository
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata

        self._iterative_tracks_metadata: dict = self._tracks_metadata.to_dict()
        self._iterative_videos_metadata: dict = self._videos_metadata.to_dict()

    def _update_iterative_metadata(self) -> None:
        self._tracks_metadata.merge_into_dict(self._iterative_tracks_metadata)
        self._videos_metadata.merge_into_dict(self._iterative_videos_metadata)

    def export(self, specification: TrackExportSpecification) -> None:
        self._update_iterative_metadata()

        append = specification.export_mode.is_subsequent_write()
        dataframe = self._get_data()
        dataframe = set_column_order(dataframe)
        path = specification.save_path
        output_path = path.with_suffix(".tracks.csv")
        write_mode: Literal["w", "a"] = "a" if append else "w"
        dataframe.to_csv(output_path, index=False, header=not append, mode=write_mode)

        if specification.export_mode.is_final_write():
            tracks_metadata_path = path.with_suffix(".tracks_metadata.json")
            write_json(self._iterative_tracks_metadata, tracks_metadata_path)

            videos_metadata_path = path.with_suffix(".videos_metadata.json")
            write_json(self._iterative_videos_metadata, videos_metadata_path)

            self._iterative_tracks_metadata.clear()
            self._iterative_videos_metadata.clear()

    def _get_data(self) -> DataFrame:
        dataset = self._track_repository.get_all()
        if isinstance(dataset, PandasDataFrameProvider):
            return dataset.get_data().reset_index()
        detections = []
        for _track in dataset.as_list():
            track_classification = _track.classification
            for detection in _track.detections:
                current = detection.to_dict()
                # Add missing track classification to detection dict
                current[track.TRACK_CLASSIFICATION] = track_classification
                detections.append(current)
        return DataFrame(detections)


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
    dataframe = dataframe[
        desired_columns_order
        + [col for col in dataframe.columns if col not in desired_columns_order]
    ]

    return dataframe
