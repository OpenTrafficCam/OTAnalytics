from typing import cast
from unittest.mock import Mock, call

import pytest
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.track import Track, TrackDataset, TrackGeometryDataset, TrackId
from OTAnalytics.plugin_datastore.python_track_store import (
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasDetection,
    PandasTrack,
    PandasTrackDataset,
    _convert_tracks,
)
from tests.conftest import (
    TrackBuilder,
    assert_equal_detection_properties,
    assert_equal_track_properties,
    assert_track_datasets_equal,
)
from tests.OTAnalytics.plugin_datastore.conftest import (
    assert_track_geometry_dataset_add_all_called_correctly,
    create_mock_geometry_dataset,
)


class TestPandasDetection:
    def test_properties(self) -> None:
        builder = TrackBuilder()
        builder.append_detection()
        python_detection = builder.build_detections()[0]
        data = Series(python_detection.to_dict())
        pandas_detection = PandasDetection(data)

        assert_equal_detection_properties(pandas_detection, python_detection)


class TestPandasTrack:
    def test_properties(self) -> None:
        builder = TrackBuilder()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        python_track = builder.build_track()
        detections = [detection.to_dict() for detection in python_track.detections]
        data = DataFrame(detections)
        data[track.TRACK_CLASSIFICATION] = data[track.CLASSIFICATION]
        pandas_track = PandasTrack(data)

        assert_equal_track_properties(pandas_track, python_track)


class TestPandasTrackDataset:
    def _create_dataset(self, size: int) -> TrackDataset:
        tracks = []
        for i in range(1, size + 1):
            tracks.append(self.__build_track(str(i)))

        dataset = PandasTrackDataset.from_list(tracks)
        return dataset

    def test_use_track_classificator(self) -> None:
        first_detection_class = "car"
        track_class = "pedestrian"
        builder = TrackBuilder()
        builder.add_confidence(1.0)
        builder.add_track_class(first_detection_class)
        builder.add_detection_class(first_detection_class)
        builder.append_detection()
        builder.add_detection_class(track_class)
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        track = builder.build_track()

        dataset = PandasTrackDataset.from_list([track])

        added_track = dataset.get_for(track.id)

        assert added_track is not None
        assert added_track.classification == track_class

    def test_add(self) -> None:
        builder = TrackBuilder()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        track = builder.build_track()
        expected_dataset = PandasTrackDataset.from_list([track])
        dataset = PandasTrackDataset()

        merged = dataset.add_all(PythonTrackDataset({track.id: track}))

        assert 0 == len(dataset.as_list())
        for actual, expected in zip(merged, expected_dataset):
            assert_equal_track_properties(actual, expected)

    def test_add_nothing(self) -> None:
        dataset = PandasTrackDataset()

        merged = dataset.add_all(PythonTrackDataset())

        assert 0 == len(merged.as_list())

    def test_add_all(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        third_track = self.__build_track("3")
        expected_dataset = PandasTrackDataset.from_list(
            [first_track, second_track, third_track]
        )
        dataset = PandasTrackDataset.from_list([])
        assert len(dataset) == 0
        dataset = dataset.add_all([first_track])
        assert len(dataset) == 1
        merged = cast(
            PandasTrackDataset,
            dataset.add_all(
                PythonTrackDataset(
                    {second_track.id: second_track, third_track.id: third_track}
                )
            ),
        )
        for actual, expected in zip(merged.as_list(), expected_dataset.as_list()):
            assert_equal_track_properties(actual, expected)
        assert merged._geometry_datasets == {}

    def test_add_two_existing_pandas_datasets(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        expected_dataset = PandasTrackDataset.from_list([first_track, second_track])
        first = PandasTrackDataset.from_list([first_track])
        second = PandasTrackDataset.from_list([second_track])
        merged = cast(PandasTrackDataset, first.add_all(second))

        for actual, expected in zip(merged.as_list(), expected_dataset.as_list()):
            assert_equal_track_properties(actual, expected)
        assert merged._geometry_datasets == {}

    def test_add_all_merge_tracks(
        self, first_track: Track, first_track_continuing: Track, second_track: Track
    ) -> None:
        (
            geometry_dataset_no_offset,
            updated_geometry_dataset_no_offset,
        ) = create_mock_geometry_dataset()
        (
            geometry_dataset_with_offset,
            updated_geometry_dataset_with_offset,
        ) = create_mock_geometry_dataset()
        geometry_datasets = {
            RelativeOffsetCoordinate(0, 0): cast(
                TrackGeometryDataset, geometry_dataset_no_offset
            ),
            RelativeOffsetCoordinate(0.5, 0.5): cast(
                TrackGeometryDataset, geometry_dataset_with_offset
            ),
        }
        dataset = PandasTrackDataset.from_dataframe(
            _convert_tracks([first_track]), geometry_datasets
        )
        dataset_merged_track = cast(
            PandasTrackDataset, dataset.add_all([first_track_continuing, second_track])
        )
        expected_merged_track = PythonTrack(
            first_track.id,
            first_track_continuing.classification,
            first_track.detections + first_track_continuing.detections,
        )
        expected_dataset = PandasTrackDataset.from_list(
            [expected_merged_track, second_track]
        )
        assert_track_datasets_equal(dataset_merged_track, expected_dataset)
        assert_track_geometry_dataset_add_all_called_correctly(
            geometry_dataset_no_offset.add_all, expected_dataset
        )
        assert_track_geometry_dataset_add_all_called_correctly(
            geometry_dataset_with_offset.add_all, expected_dataset
        )
        assert dataset_merged_track._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset_no_offset,
            RelativeOffsetCoordinate(0.5, 0.5): updated_geometry_dataset_with_offset,
        }

    def __build_track(self, track_id: str, length: int = 5) -> Track:
        builder = TrackBuilder()
        builder.add_track_id(track_id)
        for i in range(0, length):
            builder.append_detection()
        return builder.build_track()

    def test_get_by_id(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        returned = dataset.get_for(first_track.id)

        assert returned is not None
        assert_equal_track_properties(returned, first_track)

    def test_get_missing(self) -> None:
        dataset = PandasTrackDataset()

        returned = dataset.get_for(TrackId("1"))

        assert returned is None

    def test_clear(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        empty_set = dataset.clear()

        assert 0 == len(empty_set.as_list())

    def test_remove(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        tracks_df = _convert_tracks([first_track, second_track])
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PandasTrackDataset.from_dataframe(
            tracks_df, {RelativeOffsetCoordinate(0, 0): geometry_dataset}
        )

        removed_track_set = cast(PandasTrackDataset, dataset.remove(first_track.id))
        for actual, expected in zip(
            removed_track_set.as_list(),
            PandasTrackDataset.from_list([second_track]).as_list(),
        ):
            assert_equal_track_properties(actual, expected)
        geometry_dataset.remove.assert_called_once_with({first_track.id})
        assert removed_track_set._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset,
        }

    def test_len(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list([first_track, second_track])
        assert len(dataset) == 2
        empty_dataset = PandasTrackDataset.from_list([])
        assert len(empty_dataset) == 0

    @pytest.mark.parametrize(
        "num_tracks,batches,expected_batches", [(10, 1, 1), (10, 4, 4), (3, 4, 3)]
    )
    def test_split(self, num_tracks: int, batches: int, expected_batches: int) -> None:
        dataset = self._create_dataset(num_tracks)
        assert len(dataset) == num_tracks
        split_datasets = dataset.split(batches)

        assert len(dataset) == sum([len(_dataset) for _dataset in split_datasets])
        assert len(split_datasets) == expected_batches

        it = iter(dataset)

        for idx, _dataset in enumerate(split_datasets):
            for expected_track in _dataset:
                it_track = next(it)
                assert expected_track.id == it_track.id
                assert len(expected_track.detections) == len(it_track.detections)

                for detection, expected_detection in zip(
                    expected_track.detections, it_track.detections
                ):
                    assert_equal_detection_properties(detection, expected_detection)

    def test_split_with_existing_geometries(
        self, first_track: Track, second_track: Track
    ) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        first_batch_geometries_no_offset = Mock()
        second_batch_geometries_no_offset = Mock()
        geometry_dataset_no_offset, _ = create_mock_geometry_dataset(
            [first_batch_geometries_no_offset, second_batch_geometries_no_offset]
        )

        first_batch_geometries_with_offset = Mock()
        second_batch_geometries_with_offset = Mock()
        geometry_dataset_with_offset, _ = create_mock_geometry_dataset(
            [first_batch_geometries_with_offset, second_batch_geometries_with_offset]
        )

        geometry_datasets = {
            RelativeOffsetCoordinate(0, 0): cast(
                TrackGeometryDataset, geometry_dataset_no_offset
            ),
            RelativeOffsetCoordinate(0.5, 0.5): cast(
                TrackGeometryDataset, geometry_dataset_with_offset
            ),
        }
        tracks_df = _convert_tracks([first_track, second_track])

        dataset = PandasTrackDataset(tracks_df, geometry_datasets)
        result = cast(list[PythonTrackDataset], dataset.split(batches=2))
        assert_track_datasets_equal(
            result[0], PandasTrackDataset.from_list([first_track])
        )
        assert_track_datasets_equal(
            result[1], PandasTrackDataset.from_list([second_track])
        )
        assert geometry_dataset_no_offset.get_for.call_args_list == [
            call((first_track.id.id,)),
            call((second_track.id.id,)),
        ]
        assert geometry_dataset_with_offset.get_for.call_args_list == [
            call((first_track.id.id,)),
            call((second_track.id.id,)),
        ]

    def test_filter_by_minimum_detection_length(self) -> None:
        first_track = self.__build_track("1", length=5)
        second_track = self.__build_track("2", length=10)
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        filtered_dataset = dataset.filter_by_min_detection_length(7)
        assert len(filtered_dataset) == 1
        for actual_track, expected_track in zip(filtered_dataset, [second_track]):
            assert_equal_track_properties(actual_track, expected_track)
