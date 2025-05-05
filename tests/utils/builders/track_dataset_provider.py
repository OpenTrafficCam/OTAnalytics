from typing import Literal
from unittest.mock import Mock

from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.filtered_track_dataset import (
    FilterByClassTrackDataset,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import (
    FilteredPythonTrackDataset,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    FilterByClassPandasTrackDataset,
    PandasTrackDataset,
)


def create_mock_geometry_dataset(
    get_for_side_effect: list[Mock] | None = None,
) -> tuple[Mock, Mock]:
    geometry_dataset = Mock(spec=TrackGeometryDataset)
    updated_geometry_dataset = Mock()
    geometry_dataset.add_all.return_value = updated_geometry_dataset
    geometry_dataset.remove.return_value = updated_geometry_dataset
    if get_for_side_effect is not None:
        geometry_dataset.get_for.side_effect = get_for_side_effect
    return geometry_dataset, updated_geometry_dataset


PYTHON: Literal["PYTHON"] = "PYTHON"
PANDAS: Literal["PANDAS"] = "PANDAS"
IMPLEMENTATIONS = [PYTHON, PANDAS]


class TrackDatasetProvider:
    GEOMETRY_FACTORY: TRACK_GEOMETRY_FACTORY = (
        ShapelyTrackGeometryDataset.from_track_dataset
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
        return PythonTrackDataset.from_list(
            tracks, ShapelyTrackGeometryDataset.from_track_dataset
        )

    def provide_filtered(
        self,
        dataset_type: str,
        tracks: list[Track],
        include_classes: list[str],
        exclude_classes: list[str],
    ) -> FilterByClassTrackDataset:
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
    ) -> FilterByClassPandasTrackDataset:
        return FilterByClassPandasTrackDataset(
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
    ) -> tuple[FilterByClassTrackDataset, Mock]:
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
                FilterByClassPandasTrackDataset(
                    mock, frozenset(include_classes), frozenset(exclude_classes)
                ),
                mock,
            )
        else:
            raise ValueError(f"Not known TrackDataset type of {dataset_type}!")
