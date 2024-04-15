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
    def __init__(
        self,
        track_repository: TrackRepository,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
    ) -> None:
        self._track_repository = track_repository
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata

    def export(self, specification: TrackExportSpecification) -> None:
        dataframe = self._get_data()
        dataframe = set_column_order(dataframe)
        output_path = specification.save_path.with_suffix(".tracks.csv")
        dataframe.to_csv(output_path, index=False)

        tracks_metadata_path = specification.save_path.with_suffix(
            ".tracks_metadata.json"
        )
        tracks_metadata = self._tracks_metadata.to_dict()
        write_json(tracks_metadata, tracks_metadata_path)
        videos_metadata_path = specification.save_path.with_suffix(
            ".videos_metadata.json"
        )
        videos_metadata = self._videos_metadata.to_dict()
        write_json(videos_metadata, videos_metadata_path)

    def _get_data(self) -> DataFrame:
        dataset = self._track_repository.get_all()
        if isinstance(dataset, PandasDataFrameProvider):
            return dataset.get_data().reset_index()
        detections = [
            [detection.to_dict() for detection in track.detections]
            for track in dataset.as_list()
        ]
        return DataFrame.from_dict(detections)


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
