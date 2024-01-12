from typing import cast
from unittest.mock import Mock, call

import numpy
import pytest
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.geometry import (
    ImageCoordinate,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.python_track_store import (
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasDetection,
    PandasTrack,
    PandasTrackDataset,
    _convert_tracks,
    extract_hostname,
)
from tests.OTAnalytics.plugin_datastore.conftest import (
    assert_track_geometry_dataset_add_all_called_correctly,
    create_mock_geometry_dataset,
)
from tests.conftest import (
    TrackBuilder,
    assert_equal_detection_properties,
    assert_equal_track_properties,
    assert_track_datasets_equal,
)


class TestPandasDetection:
    def test_convert_frame_number_to_python_data_type(self) -> None:
        track_id = "track-id"
        new_frame_number = 2
        builder = TrackBuilder()
        python_detection = builder.create_detection()
        detection_values = python_detection.to_dict()
        detection_values[track.FRAME] = numpy.int64(new_frame_number)
        data = Series(detection_values)
        detection = PandasDetection(track_id=track_id, data=data)

        assert type(detection.frame) is int
        assert detection.frame == new_frame_number

    def test_properties(self) -> None:
        builder = TrackBuilder()
        builder.append_detection()
        python_detection = builder.build_detections()[0]
        data = Series(
            python_detection.to_dict(),
            name=python_detection.occurrence,
        )
        pandas_detection = PandasDetection(python_detection.track_id.id, data)

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
        data = DataFrame(detections).set_index([track.OCCURRENCE]).sort_index()
        data[track.TRACK_CLASSIFICATION] = data[track.CLASSIFICATION]
        data = data.drop([track.TRACK_ID], axis=1)
        pandas_track = PandasTrack(python_track.id.id, data)

        assert_equal_track_properties(pandas_track, python_track)


class TestPandasTrackDataset:
    def _create_dataset(self, size: int) -> TrackDataset:
        tracks = []
        for i in range(1, size + 1):
            tracks.append(self.__build_track(str(i)))

        dataset = PandasTrackDataset.from_list(
            tracks, PygeosTrackGeometryDataset.from_track_dataset
        )
        return dataset

    def test_use_track_classificator(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
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

        dataset = PandasTrackDataset.from_list([track], track_geometry_factory)

        added_track = dataset.get_for(track.id)

        assert added_track is not None
        assert added_track.classification == track_class

    def test_add(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        builder = TrackBuilder()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        track = builder.build_track()
        expected_dataset = PandasTrackDataset.from_list([track], track_geometry_factory)
        dataset = PandasTrackDataset(track_geometry_factory)

        merged = dataset.add_all(PythonTrackDataset({track.id: track}))

        assert 0 == len(dataset.as_list())
        for actual, expected in zip(merged, expected_dataset):
            assert_equal_track_properties(actual, expected)

    def test_add_nothing(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)

        merged = dataset.add_all(PythonTrackDataset())

        assert 0 == len(merged.as_list())

    def test_add_all(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        third_track = self.__build_track("3")
        expected_dataset = PandasTrackDataset.from_list(
            [first_track, second_track, third_track], track_geometry_factory
        )
        dataset = PandasTrackDataset.from_list([], track_geometry_factory)
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

    def test_add_two_existing_pandas_datasets(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        expected_dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )
        first = PandasTrackDataset.from_list([first_track], track_geometry_factory)
        second = PandasTrackDataset.from_list([second_track], track_geometry_factory)
        merged = cast(PandasTrackDataset, first.add_all(second))

        for actual, expected in zip(merged.as_list(), expected_dataset.as_list()):
            assert_equal_track_properties(actual, expected)
        assert merged._geometry_datasets == {}

    def test_add_all_merge_tracks(
        self,
        first_track: Track,
        first_track_continuing: Track,
        second_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
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
            _convert_tracks([first_track_continuing]),
            track_geometry_factory,
            geometry_datasets,
        )
        dataset_merged_track = cast(
            PandasTrackDataset, dataset.add_all([first_track, second_track])
        )
        expected_merged_track = PythonTrack(
            first_track.id,
            first_track_continuing.classification,
            first_track.detections + first_track_continuing.detections,
        )
        expected_dataset = PandasTrackDataset.from_list(
            [expected_merged_track, second_track], track_geometry_factory
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

    def test_get_by_id(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        returned = dataset.get_for(first_track.id)

        assert returned is not None
        assert_equal_track_properties(returned, first_track)

    def test_get_missing(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)

        returned = dataset.get_for(TrackId("1"))

        assert returned is None

    def test_clear(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        empty_set = dataset.clear()

        assert 0 == len(empty_set.as_list())

    def test_remove(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        tracks_df = _convert_tracks([first_track, second_track])
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PandasTrackDataset.from_dataframe(
            tracks_df,
            track_geometry_factory,
            {RelativeOffsetCoordinate(0, 0): geometry_dataset},
        )

        removed_track_set = cast(PandasTrackDataset, dataset.remove(first_track.id))
        for actual, expected in zip(
            removed_track_set.as_list(),
            PandasTrackDataset.from_list(
                [second_track], track_geometry_factory
            ).as_list(),
        ):
            assert_equal_track_properties(actual, expected)
        geometry_dataset.remove.assert_called_once_with({first_track.id})
        assert removed_track_set._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset,
        }

    def test_len(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )
        assert len(dataset) == 2
        empty_dataset = PandasTrackDataset.from_list([], track_geometry_factory)
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
        self,
        first_track: Track,
        second_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
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

        dataset = PandasTrackDataset(
            track_geometry_factory, tracks_df, geometry_datasets
        )
        result = cast(list[PythonTrackDataset], dataset.split(batches=2))
        assert_track_datasets_equal(
            result[0],
            PandasTrackDataset.from_list([first_track], track_geometry_factory),
        )
        assert_track_datasets_equal(
            result[1],
            PandasTrackDataset.from_list([second_track], track_geometry_factory),
        )
        assert geometry_dataset_no_offset.get_for.call_args_list == [
            call((first_track.id.id,)),
            call((second_track.id.id,)),
        ]
        assert geometry_dataset_with_offset.get_for.call_args_list == [
            call((first_track.id.id,)),
            call((second_track.id.id,)),
        ]

    def test_filter_by_minimum_detection_length(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("1", length=5)
        second_track = self.__build_track("2", length=10)
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        filtered_dataset = dataset.filter_by_min_detection_length(7)
        assert len(filtered_dataset) == 1
        for actual_track, expected_track in zip(filtered_dataset, [second_track]):
            assert_equal_track_properties(actual_track, expected_track)

    def test_apply_to_first_segments(
        self,
        first_track: Track,
        second_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        mock_consumer = Mock()
        event_1 = self.__create_enter_scene_event(first_track)
        event_2 = self.__create_enter_scene_event(second_track)
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        dataset.apply_to_first_segments(mock_consumer)

        mock_consumer.assert_any_call(event_1)
        mock_consumer.assert_any_call(event_2)

    def __create_enter_scene_event(self, track: Track) -> Event:
        return Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=extract_hostname(track.first_detection.video_name),
            occurrence=track.first_detection.occurrence,
            frame_number=track.first_detection.frame,
            section_id=None,
            event_coordinate=ImageCoordinate(
                track.first_detection.x, track.first_detection.y
            ),
            event_type=EventType.ENTER_SCENE,
            direction_vector=calculate_direction_vector(
                track.first_detection.x,
                track.first_detection.y,
                track.detections[1].x,
                track.detections[1].y,
            ),
            video_name=track.first_detection.video_name,
        )

    def test_apply_to_last_segments(
        self,
        first_track: Track,
        second_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        mock_consumer = Mock()
        event_1 = self.__create_leave_scene_event(first_track)
        event_2 = self.__create_leave_scene_event(second_track)
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        dataset.apply_to_last_segments(mock_consumer)

        mock_consumer.assert_any_call(event_1)
        mock_consumer.assert_any_call(event_2)

    def __create_leave_scene_event(self, track: Track) -> Event:
        return Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=extract_hostname(track.last_detection.video_name),
            occurrence=track.last_detection.occurrence,
            frame_number=track.last_detection.frame,
            section_id=None,
            event_coordinate=ImageCoordinate(
                track.last_detection.x, track.last_detection.y
            ),
            event_type=EventType.LEAVE_SCENE,
            direction_vector=calculate_direction_vector(
                track.detections[-2].x,
                track.detections[-2].y,
                track.last_detection.x,
                track.last_detection.y,
            ),
            video_name=track.last_detection.video_name,
        )
