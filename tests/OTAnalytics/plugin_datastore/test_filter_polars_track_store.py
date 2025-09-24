import pytest

from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_datastore.filter_polars_track_dataset import (
    FilterByIdPolarsTrackDataset,
    FilterLastNDetectionsPolarsTrackDataset,
)
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsTrackDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import PythonTrack
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from tests.utils.assertions import assert_track_datasets_equal


@pytest.fixture
def track_geometry_factory() -> POLARS_TRACK_GEOMETRY_FACTORY:
    return PolarsTrackGeometryDataset.from_track_dataset


class TestFilterByIdPolarsTrackDataset:
    def test_filter_by_id_all_included(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        expected = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        track_ids = [car_track.id.id, pedestrian_track.id.id]
        target = FilterByIdPolarsTrackDataset(dataset, track_ids)

        assert_track_datasets_equal(target, expected)

    def test_filter_by_id_one_matching(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
        bicycle_track: Track,
    ) -> None:
        expected = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        track_ids = [bicycle_track.id.id, pedestrian_track.id.id]
        target = FilterByIdPolarsTrackDataset(dataset, track_ids)

        assert_track_datasets_equal(target, expected)


class TestFilterLastNSegmentsPolarsTrackDataset:
    def test_filter_last_n_segments_all_included(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track_continuing: Track,
        pedestrian_track: Track,
        single_detection_track: Track,
    ) -> None:
        expected_car_track = create_expected_track(car_track_continuing)
        expected_pedestrian_track = create_expected_track(pedestrian_track)
        expected = PolarsTrackDataset.from_list(
            [expected_car_track, expected_pedestrian_track], track_geometry_factory
        )
        last_n = 2

        target = FilterLastNDetectionsPolarsTrackDataset(
            PolarsTrackDataset.from_list(
                [car_track_continuing, pedestrian_track, single_detection_track],
                track_geometry_factory,
            ),
            last_n,
        )

        assert_track_datasets_equal(target, expected)


def create_expected_track(track: Track) -> PythonTrack:
    car_detections = track.detections[-2:]
    expected_car_track = PythonTrack(
        _original_id=track.id,
        _id=track.id,
        _classification=track.classification,
        _detections=car_detections,
    )
    return expected_car_track
