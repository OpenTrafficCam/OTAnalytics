from typing import Iterable
from unittest.mock import Mock

import pytest
from _pytest.fixtures import FixtureRequest

from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset import FilteredTrackDataset
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CLASS_BICYCLIST,
    CLASS_CAR,
    CLASS_CARGOBIKE,
    CLASS_PEDESTRIAN,
)
from tests.utils.assertions import (
    assert_equal_track_properties,
    assert_track_dataset_has_tracks,
)
from tests.utils.builders.track_dataset_provider import (
    IMPLEMENTATIONS,
    TrackDatasetProvider,
)
from tests.utils.builders.track_segment_builder import (
    TrackSegmentDatasetBuilderProvider,
)


class TestFilteredTrackDataset:
    def get_datasets(
        self,
        tracks: list[Track],
        include_classes: list[str],
        exclude_classes: list[str],
    ) -> dict[str, FilteredTrackDataset]:
        provider = TrackDatasetProvider()
        return {
            dataset_type: provider.provide_filtered(
                dataset_type, tracks, include_classes, exclude_classes
            )
            for dataset_type in IMPLEMENTATIONS
        }

    def get_mocked_datasets(
        self, include_classes: list[str], exclude_classes: list[str]
    ) -> list[tuple[FilteredTrackDataset, Mock]]:
        provider = TrackDatasetProvider()
        return [
            provider.provide_filtered_mock(
                dataset_type, include_classes, exclude_classes
            )
            for dataset_type in IMPLEMENTATIONS
        ]

    def remove_by_id(self, tracks: Iterable[Track], classes: list[str]) -> list[Track]:
        return [track for track in tracks if track.classification in classes]

    def test_include_and_exclude_classes_properties(self) -> None:
        include_classes = [CLASS_CARGOBIKE, CLASS_CAR]
        exclude_classes = [CLASS_PEDESTRIAN, CLASS_BICYCLIST]
        filtered_datasets = self.get_datasets([], include_classes, exclude_classes)
        for filtered_dataset in filtered_datasets.values():
            assert filtered_dataset.include_classes == frozenset(include_classes)
            assert filtered_dataset.exclude_classes == frozenset(exclude_classes)

    def test_track_ids(self, cargo_bike_track: Track, bicycle_track: Track) -> None:
        filtered_datasets = self.get_datasets(
            [cargo_bike_track, bicycle_track], [CLASS_BICYCLIST], []
        )
        for filtered_dataset in filtered_datasets.values():
            assert filtered_dataset.track_ids == frozenset([bicycle_track.id])

    def test_first_and_last_occurrence(
        self, car_track: Track, cargo_bike_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets(
            [cargo_bike_track, car_track], [CLASS_CARGOBIKE], []
        )
        for filtered_dataset in filtered_datasets.values():
            assert (
                filtered_dataset.first_occurrence
                == cargo_bike_track.first_detection.occurrence
            )
            assert (
                filtered_dataset.last_occurrence
                == cargo_bike_track.last_detection.occurrence
            )

    @pytest.mark.parametrize(
        "include_classes,exclude_classes,expected",
        [
            (
                [CLASS_PEDESTRIAN, CLASS_CARGOBIKE],
                [CLASS_CARGOBIKE],
                [CLASS_PEDESTRIAN, CLASS_CARGOBIKE],
            ),
            ([], [], [CLASS_CAR, CLASS_PEDESTRIAN, CLASS_BICYCLIST, CLASS_CARGOBIKE]),
            (
                [],
                [CLASS_PEDESTRIAN],
                [CLASS_CAR, CLASS_BICYCLIST, CLASS_CARGOBIKE],
            ),
            ([CLASS_PEDESTRIAN], [], [CLASS_PEDESTRIAN]),
            ([CLASS_CAR], ["plane"], [CLASS_CAR]),
        ],
    )
    def test_classifications(
        self,
        include_classes: list[str],
        exclude_classes: list[str],
        expected: list[str],
        all_tracks: list[Track],
    ) -> None:
        filtered_datasets = self.get_datasets(
            all_tracks, include_classes, exclude_classes
        )

        for filtered_dataset in filtered_datasets.values():
            assert filtered_dataset.classifications == frozenset(expected)

    def test_empty(self, car_track: Track, bicycle_track: Track) -> None:
        empty_filtered_datasets = self.get_datasets([], [CLASS_CAR], [])
        for empty_filtered_dataset in empty_filtered_datasets.values():
            assert empty_filtered_dataset.empty
            filled_but_ignored_dataset = empty_filtered_dataset.add_all([bicycle_track])
            assert filled_but_ignored_dataset.empty
            filled_not_ignored_dataset = filled_but_ignored_dataset.add_all([car_track])
            assert not filled_not_ignored_dataset.empty

    def test_filter_no_filters(
        self,
        all_tracks: list[Track],
    ) -> None:
        filtered_datasets = self.get_datasets(all_tracks, [], [])
        for filtered_dataset in filtered_datasets.values():
            assert_track_dataset_has_tracks(filtered_dataset, all_tracks)

    def test_filter_include_classes(
        self,
        all_tracks: list[Track],
        cargo_bike_track: Track,
        bicycle_track: Track,
    ) -> None:
        filtered_datasets = self.get_datasets(
            all_tracks, [CLASS_CARGOBIKE, CLASS_BICYCLIST], [CLASS_BICYCLIST]
        )
        for filtered_dataset in filtered_datasets.values():
            assert_track_dataset_has_tracks(
                filtered_dataset, [cargo_bike_track, bicycle_track]
            )

    def test_filter_exclude_classes(
        self,
        all_tracks: list[Track],
        car_track: Track,
        pedestrian_track: Track,
        cargo_bike_track: Track,
    ) -> None:
        filtered_datasets = self.get_datasets(all_tracks, [], [CLASS_BICYCLIST])
        for filtered_dataset in filtered_datasets.values():
            assert_track_dataset_has_tracks(
                filtered_dataset, [car_track, pedestrian_track, cargo_bike_track]
            )

    def test_cache_with_no_filter_settings(self, tracks: list[Track]) -> None:
        filtered_datasets = self.get_datasets(tracks, [], [])
        for filtered_dataset in filtered_datasets.values():
            filtered_result = filtered_dataset._filter()
            cached_filtered_result = filtered_dataset._filter()
            assert filtered_result == cached_filtered_result

    def test_cache_with_include_filter(self, tracks: list[Track]) -> None:
        filtered_datasets = self.get_datasets(
            tracks, [CLASS_BICYCLIST], [CLASS_CARGOBIKE]
        )
        for filtered_dataset in filtered_datasets.values():
            filtered_result = filtered_dataset._filter()
            cached_filtered_result = filtered_dataset._filter()
            assert filtered_result == cached_filtered_result

    def test_cache_with_exclude_filter(self, tracks: list[Track]) -> None:
        filtered_datasets = self.get_datasets(tracks, [], [CLASS_CARGOBIKE])
        for filtered_dataset in filtered_datasets.values():
            filtered_result = filtered_dataset._filter()
            cached_filtered_result = filtered_dataset._filter()
            assert filtered_result == cached_filtered_result

    def test_len(self, all_tracks: list[Track]) -> None:
        filtered_datasets = self.get_datasets(
            all_tracks, [], [CLASS_CARGOBIKE, CLASS_BICYCLIST]
        )
        for filtered_dataset in filtered_datasets.values():
            assert len(filtered_dataset) == 2

    def test_get_for(
        self, car_track: Track, bicycle_track: Track, cargo_bike_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track, cargo_bike_track],
            [],
            [CLASS_CARGOBIKE, CLASS_BICYCLIST],
        )
        for filtered_dataset in filtered_datasets.values():
            result_car = filtered_dataset.get_for(car_track.id)
            assert result_car is not None
            assert_equal_track_properties(result_car, car_track)
            assert filtered_dataset.get_for(bicycle_track.id) is None
            assert filtered_dataset.get_for(cargo_bike_track.id) is None
            assert filtered_dataset.get_for(TrackId("foobar")) is None

    def test_as_list(self, car_track: Track, bicycle_track: Track) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track],
            [],
            [CLASS_BICYCLIST],
        )
        for filtered_dataset in filtered_datasets.values():
            assert len(filtered_dataset) == 1
            result = filtered_dataset.as_list()
            assert len(result) == 1
            assert_equal_track_properties(result[0], car_track)

    def test_intersecting_tracks(self) -> None:
        mocked_datasets = self.get_mocked_datasets([], [])
        sections = Mock()
        offset = Mock()
        for dataset, mock_other in mocked_datasets:
            dataset.intersecting_tracks(sections, offset)
            mock_other.intersecting_tracks.assert_called_once_with(sections, offset)

    def test_intersection_points(self) -> None:
        mocked_datasets = self.get_mocked_datasets([], [])
        sections = Mock()
        offset = Mock()
        for dataset, mock_other in mocked_datasets:
            dataset.intersection_points(sections, offset)
            mock_other.intersection_points.assert_called_once_with(sections, offset)

    def test_contained_by_section(self) -> None:
        mocked_datasets = self.get_mocked_datasets([], [])
        sections = Mock()
        offset = Mock()
        for dataset, mock_other in mocked_datasets:
            dataset.contained_by_sections(sections, offset)
            mock_other.contained_by_sections.assert_called_once_with(sections, offset)

    def test_filter_by_min_detection_length(
        self, car_track: Track, bicycle_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track], [CLASS_CAR], []
        )
        for filtered_dataset in filtered_datasets.values():
            result_no_tracks = filtered_dataset.filter_by_min_detection_length(4)
            assert len(result_no_tracks) == 0
            result_all_tracks = filtered_dataset.filter_by_min_detection_length(2)
            assert len(result_all_tracks) == 1
            assert_equal_track_properties(result_all_tracks.as_list()[0], car_track)

    @pytest.mark.parametrize(
        "include_classes,exclude_classes,expected_track_fixture_name",
        [
            ([], [], ["car_track", "bicycle_track"]),
            ([CLASS_CAR], [CLASS_CAR], ["car_track"]),
            ([], [CLASS_CAR], ["bicycle_track"]),
        ],
    )
    def test_get_first_segments(
        self,
        include_classes: list[str],
        exclude_classes: list[str],
        expected_track_fixture_name: list[str],
        track_segment_dataset_builder_provider: TrackSegmentDatasetBuilderProvider,
        car_track: Track,
        bicycle_track: Track,
        request: FixtureRequest,
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track], include_classes, exclude_classes
        )
        for implementation, filtered_dataset in filtered_datasets.items():
            expected_tracks: list[Track] = [
                request.getfixturevalue(fixture_name)
                for fixture_name in expected_track_fixture_name
            ]
            builder = track_segment_dataset_builder_provider.provide(implementation)
            builder.add_first_segments(expected_tracks)
            expected_segments = builder.build()
            segments = filtered_dataset.get_first_segments()
            assert expected_segments == segments

    @pytest.mark.parametrize(
        "include_classes,exclude_classes,expected_track_fixture_name",
        [
            ([], [], ["car_track", "bicycle_track"]),
            ([CLASS_CAR], [CLASS_CAR], ["car_track"]),
            ([], [CLASS_CAR], ["bicycle_track"]),
        ],
    )
    def test_get_last_segments(
        self,
        include_classes: list[str],
        exclude_classes: list[str],
        expected_track_fixture_name: list[str],
        track_segment_dataset_builder_provider: TrackSegmentDatasetBuilderProvider,
        car_track: Track,
        bicycle_track: Track,
        request: FixtureRequest,
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track], include_classes, exclude_classes
        )
        for implementation, filtered_dataset in filtered_datasets.items():
            expected_tracks: list[Track] = [
                request.getfixturevalue(fixture_name)
                for fixture_name in expected_track_fixture_name
            ]
            builder = track_segment_dataset_builder_provider.provide(implementation)
            builder.add_last_segments(expected_tracks)
            expected_segments = builder.build()
            segments = filtered_dataset.get_last_segments()
            assert expected_segments == segments

    def test_add_all(
        self, car_track: Track, bicycle_track: Track, cargo_bike_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets([car_track], [], [])
        for filtered_dataset in filtered_datasets.values():
            result = filtered_dataset.add_all([bicycle_track, cargo_bike_track])
            assert isinstance(result, type(filtered_dataset))
            assert result.include_classes == filtered_dataset.include_classes
            assert result.exclude_classes == filtered_dataset.exclude_classes
            assert_track_dataset_has_tracks(
                result, [car_track, bicycle_track, cargo_bike_track]
            )

    def test_remove(
        self, car_track: Track, bicycle_track: Track, cargo_bike_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track, cargo_bike_track], [], []
        )
        for filtered_dataset in filtered_datasets.values():
            result = filtered_dataset.remove(cargo_bike_track.id)
            assert isinstance(result, type(filtered_dataset))
            assert result.include_classes == filtered_dataset.include_classes
            assert result.exclude_classes == filtered_dataset.exclude_classes
            assert result.get_for(cargo_bike_track.id) is None
            assert_track_dataset_has_tracks(result, [car_track, bicycle_track])

    def test_remove_multiple(
        self, car_track: Track, bicycle_track: Track, cargo_bike_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track, cargo_bike_track], [], []
        )
        for filtered_dataset in filtered_datasets.values():
            result = filtered_dataset.remove_multiple(
                {cargo_bike_track.id, bicycle_track.id}
            )
            assert isinstance(result, type(filtered_dataset))
            assert result.include_classes == filtered_dataset.include_classes
            assert result.exclude_classes == filtered_dataset.exclude_classes
            assert_track_dataset_has_tracks(result, [car_track])

    def test_clear(
        self, car_track: Track, bicycle_track: Track, cargo_bike_track: Track
    ) -> None:
        filtered_datasets = self.get_datasets(
            [car_track, bicycle_track, cargo_bike_track], [], []
        )
        for filtered_dataset in filtered_datasets.values():
            result = filtered_dataset.clear()
            assert isinstance(result, type(filtered_dataset))
            assert result.include_classes == filtered_dataset.include_classes
            assert result.exclude_classes == filtered_dataset.exclude_classes
            assert not result.as_list()

    def test_split(self, car_track: Track, bicycle_track: Track) -> None:
        filtered_datasets = self.get_datasets([car_track, bicycle_track], [], [])
        for filtered_dataset in filtered_datasets.values():
            chunks = filtered_dataset.split(2)
            assert len(chunks) == 2
            for chunk, expected_track in zip(chunks, [car_track, bicycle_track]):
                assert isinstance(chunk, type(filtered_dataset))
                assert chunk.include_classes == filtered_dataset.include_classes
                assert chunk.exclude_classes == filtered_dataset.exclude_classes
                assert_track_dataset_has_tracks(chunk, [expected_track])

    def test_calculate_geometries_for(self) -> None:
        offsets = [Mock()]
        mocked_datasets = self.get_mocked_datasets([], [])
        for dataset, mock_other in mocked_datasets:
            dataset.calculate_geometries_for(offsets)
            mock_other.calculate_geometries_for.assert_called_once_with(offsets)

    def test_cut_with_section(self) -> None:
        section = Mock()
        offset = Mock()
        track_ids = [Mock()]
        mocked_datasets = self.get_mocked_datasets([], [])
        for dataset, mock_other in mocked_datasets:
            cut_dataset = Mock()
            type(cut_dataset).track_ids = Mock()
            mock_other.cut_with_section.return_value = (cut_dataset, track_ids)

            result_dataset, original_track_ids = dataset.cut_with_section(
                section, offset
            )
            assert original_track_ids == track_ids
            assert result_dataset.track_ids == cut_dataset.track_ids
            assert isinstance(result_dataset, FilteredTrackDataset)
            assert result_dataset.include_classes == frozenset()
            assert result_dataset.exclude_classes == frozenset()
            mock_other.cut_with_section.assert_called_once_with(section, offset)
