from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.filter_pandas_track_store import (
    FilterByIdPandasTrackDataset,
    FilterLastNDetectionsPandasTrackDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import PythonTrack
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from tests.utils.assertions import assert_track_datasets_equal


class TestFilterByIdPandasTrackDataset:
    def test_filter_by_id_all_included(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        expected = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        track_ids = [car_track.id.id, pedestrian_track.id.id]
        target = FilterByIdPandasTrackDataset(dataset, track_ids)

        assert_track_datasets_equal(target, expected)

    def test_filter_by_id_one_matching(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
        bicycle_track: Track,
    ) -> None:
        expected = PandasTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )
        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        track_ids = [bicycle_track.id.id, pedestrian_track.id.id]
        target = FilterByIdPandasTrackDataset(dataset, track_ids)

        assert_track_datasets_equal(target, expected)


class TestFilterLastNSegmentsPandasTrackDataset:
    def test_filter_last_n_segments_all_included(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track_continuing: Track,
        pedestrian_track: Track,
        single_detection_track: Track,
    ) -> None:
        expected_car_track = create_expected_track(car_track_continuing)
        expected_pedestrian_track = create_expected_track(pedestrian_track)
        expected = PandasTrackDataset.from_list(
            [expected_car_track, expected_pedestrian_track], track_geometry_factory
        )
        last_n = 2

        target = FilterLastNDetectionsPandasTrackDataset(
            PandasTrackDataset.from_list(
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
