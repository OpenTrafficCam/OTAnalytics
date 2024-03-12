from pandas import DataFrame

from OTAnalytics.application.use_cases.track_export import (
    ExportTracks,
    TrackExportSpecification,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PandasDataFrameProvider,
)


class CsvTrackExport(ExportTracks):
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def export(self, specification: TrackExportSpecification) -> None:
        dataframe = self._get_data()
        dataframe = set_column_order(dataframe)
        output_path = specification.save_path.with_suffix(".tracks.csv")
        dataframe.to_csv(output_path, index=False)

    def _get_data(self) -> DataFrame:
        dataset = self._track_repository.get_all()
        if isinstance(dataset, PandasTrackDataset):
            return dataset.as_dataframe().reset_index()
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
    ]
    dataframe = dataframe[
        desired_columns_order
        + [col for col in dataframe.columns if col not in desired_columns_order]
    ]

    return dataframe
