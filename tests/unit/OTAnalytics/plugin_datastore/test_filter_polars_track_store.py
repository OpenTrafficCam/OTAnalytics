import pytest

from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_datastore.filter_polars_track_dataset import (
    FilterByClassPolarsTrackDataset,
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
from tests.utils.builders.track_builder import mark_last_detection_finished

SAMPLE_GEOREFERENCE_METADATA = GeoreferenceMetadata(
    geo_min_x=449199.0,
    geo_min_y=5699274.0,
    geo_max_x=449294.0,
    geo_max_y=5699370.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)


@pytest.fixture
def track_geometry_factory() -> POLARS_TRACK_GEOMETRY_FACTORY:
    return PolarsTrackGeometryDataset.from_track_dataset


class TestFilterByClassPolarsTrackDataset:
    def test_with_georeference_metadata_attaches_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        inner = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        target = FilterByClassPolarsTrackDataset(
            inner,
            include_classes=frozenset(),
            exclude_classes=frozenset(),
        )

        result = target.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_with_georeference_metadata_returns_filter_dataset(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        inner = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        target = FilterByClassPolarsTrackDataset(
            inner,
            include_classes=frozenset(["car"]),
            exclude_classes=frozenset(),
        )

        result = target.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        assert isinstance(result, FilterByClassPolarsTrackDataset)


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

    def test_split_finished(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
        bicycle_track: Track,
    ) -> None:
        finished_track = mark_last_detection_finished(car_track)
        dataset = PolarsTrackDataset.from_list(
            [finished_track, pedestrian_track, bicycle_track], track_geometry_factory
        )
        track_ids = [finished_track.id.id, pedestrian_track.id.id]
        target = FilterByIdPolarsTrackDataset(dataset, track_ids)

        finished, remaining = target.split_finished()

        finished_ids = {track_id.id for track_id in finished.track_ids}
        remaining_ids = {track_id.id for track_id in remaining.track_ids}
        assert finished_ids == {finished_track.id.id}
        assert remaining_ids == {pedestrian_track.id.id}


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
