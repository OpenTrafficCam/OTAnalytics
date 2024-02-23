from typing import Literal
from unittest.mock import Mock

from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    FilteredTrackDataset,
    TrackDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import (
    FilteredPythonTrackDataset,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    FilteredPandasTrackDataset,
    PandasTrackDataset,
)

PYTHON: Literal["PYTHON"] = "PYTHON"
PANDAS: Literal["PANDAS"] = "PANDAS"
IMPLEMENTATIONS = [PYTHON, PANDAS]


class TrackDatasetProvider:
    GEOMETRY_FACTORY: TRACK_GEOMETRY_FACTORY = (
        PygeosTrackGeometryDataset.from_track_dataset
    )

    def provide(self, dataset_type: str, tracks: list[Track]) -> TrackDataset:
        if dataset_type == PYTHON:
            return self.provide_python(tracks)
        elif dataset_type == PANDAS:
            return self.provide_pandas(tracks)
        else:
            raise ValueError(f"Not known TrackDataset type of {dataset_type}!")

    def provide_pandas(self, tracks: list[Track]) -> PandasTrackDataset:
        return PandasTrackDataset.from_list(tracks, self.GEOMETRY_FACTORY)

    def provide_python(self, tracks: list[Track]) -> PythonTrackDataset:
        return PythonTrackDataset.from_list(tracks)

    def provide_filtered(
        self,
        dataset_type: str,
        tracks: list[Track],
        include_classes: list[str],
        exclude_classes: list[str],
    ) -> FilteredTrackDataset:
        if dataset_type == PYTHON:
            return self.provide_filtered_python(
                tracks, include_classes, exclude_classes
            )
        elif dataset_type == PANDAS:
            return self.provide_filtered_pandas(
                tracks, include_classes, exclude_classes
            )
        else:
            raise ValueError(f"Not known TrackDataset type of {dataset_type}!")

    def provide_filtered_pandas(
        self,
        tracks: list[Track],
        include_classes: list[str],
        exclude_classes: list[str],
    ) -> FilteredPandasTrackDataset:
        return FilteredPandasTrackDataset(
            self.provide_pandas(tracks),
            frozenset(include_classes),
            frozenset(exclude_classes),
        )

    def provide_filtered_python(
        self,
        tracks: list[Track],
        include_classes: list[str],
        exclude_classes: list[str],
    ) -> FilteredPythonTrackDataset:
        return FilteredPythonTrackDataset(
            self.provide_python(tracks),
            frozenset(include_classes),
            frozenset(exclude_classes),
        )

    def provide_filtered_mock(
        self,
        dataset_type: str,
        include_classes: list[str],
        exclude_classes: list[str],
    ) -> tuple[FilteredTrackDataset, Mock]:
        if dataset_type == PYTHON:
            mock = Mock()
            return (
                FilteredPythonTrackDataset(
                    mock, frozenset(include_classes), frozenset(exclude_classes)
                ),
                mock,
            )
        elif dataset_type == PANDAS:
            mock = Mock()
            return (
                FilteredPandasTrackDataset(
                    mock, frozenset(include_classes), frozenset(exclude_classes)
                ),
                mock,
            )
        else:
            raise ValueError(f"Not known TrackDataset type of {dataset_type}!")
