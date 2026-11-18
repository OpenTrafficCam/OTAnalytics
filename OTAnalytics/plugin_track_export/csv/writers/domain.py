from pathlib import Path
from typing import cast

from pandas import DataFrame

from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_track_export.csv.writers.pandas import set_column_order


class DomainTrackDatasetCsvWriter:
    def supports(self, dataset: object) -> bool:
        return isinstance(dataset, TrackDataset)

    def write(self, dataset: object, output_path: Path, append: bool) -> None:
        domain_dataset = cast(TrackDataset, dataset)
        detections = []
        for _track in domain_dataset.as_list():
            track_classification = _track.classification
            for detection in _track.detections:
                current = detection.to_dict()
                current[track.TRACK_CLASSIFICATION] = track_classification
                detections.append(current)
        dataframe = set_column_order(DataFrame(detections))
        dataframe.to_csv(
            output_path,
            index=False,
            header=not append,
            mode="a" if append else "w",
        )
