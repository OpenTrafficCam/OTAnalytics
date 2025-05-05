from typing import cast
from unittest.mock import Mock, call

import numpy
import pytest
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
    TrackDoesNotExistError,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import (
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    COLUMNS,
    INDEX_NAMES,
    FilterByIdPandasTrackDataset,
    FilterLastNDetectionsPandasTrackDataset,
    PandasDetection,
    PandasTrack,
    PandasTrackDataset,
    PandasTrackSegmentDataset,
    _convert_tracks,
)
from tests.utils.assertions import (
    assert_equal_detection_properties,
    assert_equal_track_properties,
    assert_track_datasets_equal,
    assert_track_geometry_dataset_add_all_called_correctly,
)
from tests.utils.builders.track_builder import TrackBuilder
from tests.utils.builders.track_dataset_provider import create_mock_geometry_dataset
from tests.utils.builders.track_segment_builder import TrackSegmentDatasetBuilder


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
        expected = self.create_python_track()
        actual = self.create_pandas_track(expected)

        assert_equal_track_properties(actual, expected)

    def create_python_track(self) -> Track:
        builder = TrackBuilder()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        return builder.build_track()

    def create_pandas_track(self, this: Track) -> PandasTrack:
        detections = [detection.to_dict() for detection in this.detections]
        data = DataFrame(detections).set_index([track.OCCURRENCE]).sort_index()
        data[track.TRACK_CLASSIFICATION] = data[track.CLASSIFICATION]
        data[track.ORIGINAL_TRACK_ID] = data[track.TRACK_ID]
        data = data.drop([track.TRACK_ID], axis=1)
        return PandasTrack(_id=this.id.id, _data=data)


class TestPandasTrackSegmentDataset:
    def test_apply(self) -> None:
        consumer = Mock()
        segment_1_dict = {"dummy-key": "segment-1"}
        segment_2_dict = {"dummy-key": "segment-2"}
        expected_segment_1_dict = {"index": 0, "dummy-key": "segment-1"}
        expected_segment_2_dict = {"index": 1, "dummy-key": "segment-2"}
        data = [segment_1_dict, segment_2_dict]
        input = DataFrame(data)
        dataset = PandasTrackSegmentDataset(input)

        dataset.apply(consumer)

        consumer.assert_has_calls(
            [call(expected_segment_1_dict), call(expected_segment_2_dict)]
        )

    def test_apply_without_segments(self) -> None:
        consumer = Mock()
        dataset = PandasTrackSegmentDataset(segments=DataFrame())

        dataset.apply(consumer=consumer)
        consumer.assert_not_called()


class TestPandasTrackDataset:
    def _create_dataset(self, size: int) -> TrackDataset:
        tracks = []
        for i in range(1, size + 1):
            tracks.append(self.__build_track(str(i)))

        dataset = PandasTrackDataset.from_list(
            tracks, ShapelyTrackGeometryDataset.from_track_dataset
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

        merged = dataset.add_all(
            PythonTrackDataset(
                ShapelyTrackGeometryDataset.from_track_dataset, {track.id: track}
            )
        )

        assert 0 == len(dataset.as_list())
        for actual, expected in zip(merged, expected_dataset):
            assert_equal_track_properties(actual, expected)

    def test_add_nothing(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)

        merged = dataset.add_all(
            PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        )

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
                    ShapelyTrackGeometryDataset.from_track_dataset,
                    {second_track.id: second_track, third_track.id: third_track},
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
        car_track: Track,
        car_track_continuing: Track,
        pedestrian_track: Track,
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
            _convert_tracks([car_track_continuing]),
            track_geometry_factory,
            geometry_datasets,
        )
        dataset_merged_track = cast(
            PandasTrackDataset, dataset.add_all([car_track, pedestrian_track])
        )
        expected_merged_track = PythonTrack(
            car_track.id,
            car_track.id,
            car_track_continuing.classification,
            car_track.detections + car_track_continuing.detections,
        )
        expected_dataset = PandasTrackDataset.from_list(
            [expected_merged_track, pedestrian_track], track_geometry_factory
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

    def test_get_for(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        returned = dataset.get_for(first_track.id)

        assert returned is not None
        assert_equal_track_properties(returned, first_track)

    def test_get_for_missing_id(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY, car_track: Track
    ) -> None:
        dataset = PandasTrackDataset.from_list([car_track], track_geometry_factory)
        returned = dataset.get_for(TrackId("Foobar"))
        assert returned is None

    def test_get_for_missing_id_on_empty_dataset(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
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
        geometry_dataset.remove.assert_called_once_with([first_track.id.id])
        assert removed_track_set._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset,
        }

    def test_remove_multiple(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        third_track = self.__build_track("3")
        all_track_ids = frozenset([first_track.id, second_track.id, third_track.id])
        track_ids_to_remove = {first_track.id, second_track.id}
        tracks_df = _convert_tracks([first_track, second_track, third_track])
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PandasTrackDataset.from_dataframe(
            tracks_df,
            track_geometry_factory,
            {RelativeOffsetCoordinate(0, 0): geometry_dataset},
        )
        assert len(dataset) == 3
        assert dataset.track_ids == all_track_ids

        removed_track_set = cast(
            PandasTrackDataset,
            dataset.remove_multiple(track_ids_to_remove),
        )
        assert_equal_track_properties(list(removed_track_set)[0], third_track)
        assert set(geometry_dataset.remove.call_args_list[0][0][0]) == {
            first_track.id.id,
            second_track.id.id,
        }
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
        car_track: Track,
        pedestrian_track: Track,
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
        tracks_df = _convert_tracks([car_track, pedestrian_track])
        dataset = PandasTrackDataset.from_dataframe(
            tracks_df, track_geometry_factory, geometry_datasets
        )
        result = cast(list[PythonTrackDataset], dataset.split(batches=2))
        assert_track_datasets_equal(
            result[0],
            PandasTrackDataset.from_list([car_track], track_geometry_factory),
        )
        assert_track_datasets_equal(
            result[1],
            PandasTrackDataset.from_list([pedestrian_track], track_geometry_factory),
        )
        assert geometry_dataset_no_offset.get_for.call_args_list == [
            call([car_track.id.id]),
            call([pedestrian_track.id.id]),
        ]
        assert geometry_dataset_with_offset.get_for.call_args_list == [
            call([car_track.id.id]),
            call([pedestrian_track.id.id]),
        ]

    def test_filter_by_minimum_detection_length(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("1", length=5)
        second_track = self.__build_track("2", length=10)
        dataset = PandasTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        filtered_dataset = dataset.filter_by_min_detection_length(10)
        assert len(filtered_dataset) == 1
        for actual_track, expected_track in zip(filtered_dataset, [second_track]):
            assert_equal_track_properties(actual_track, expected_track)

    def test_get_first_segments(
        self,
        car_track: Track,
        pedestrian_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        pandas_track_segment_dataset_builder: TrackSegmentDatasetBuilder,
    ) -> None:
        pandas_track_segment_dataset_builder.add_first_segments(
            [car_track, pedestrian_track]
        )
        segments = pandas_track_segment_dataset_builder.build()

        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )

        actual = dataset.get_first_segments()

        assert actual == segments

    def test_get_last_segments(
        self,
        car_track: Track,
        pedestrian_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        pandas_track_segment_dataset_builder: TrackSegmentDatasetBuilder,
    ) -> None:
        pandas_track_segment_dataset_builder.add_last_segments(
            [car_track, pedestrian_track]
        )
        track_segments = pandas_track_segment_dataset_builder.build()
        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )

        actual = dataset.get_last_segments()

        assert actual == track_segments

    def test_first_occurrence(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        assert dataset.first_occurrence == car_track.first_detection.occurrence
        assert dataset.first_occurrence == pedestrian_track.first_detection.occurrence

    def test_last_occurrence(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        assert dataset.last_occurrence == pedestrian_track.last_detection.occurrence

    def test_first_occurrence_on_empty_dataset(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)
        assert dataset.first_occurrence is None

    def test_last_occurrence_on_empty_dataset(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)
        assert dataset.last_occurrence is None

    def test_classifications(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PandasTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        assert dataset.classifications == frozenset(
            [car_track.classification, pedestrian_track.classification]
        )

    def test_classifications_on_empty_dataset(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)
        assert dataset.classifications == frozenset()

    def test_cut_with_section(
        self,
        cutting_section_test_case: tuple[
            LineSection, list[Track], list[Track], set[TrackId]
        ],
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        (
            cutting_section,
            input_tracks,
            expected_tracks,
            expected_original_track_ids,
        ) = cutting_section_test_case
        expected_dataset = PandasTrackDataset.from_list(
            expected_tracks, track_geometry_factory
        )

        dataset = PandasTrackDataset.from_list(input_tracks, track_geometry_factory)
        cut_track_dataset, original_track_ids = dataset.cut_with_section(
            cutting_section, RelativeOffsetCoordinate(0, 0)
        )
        assert original_track_ids == expected_original_track_ids
        assert_track_datasets_equal(cut_track_dataset, expected_dataset)

    def test_cut_with_section_no_tracks(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PandasTrackDataset.from_list([], track_geometry_factory)
        cut_track_dataset, original_track_ids = dataset.cut_with_section(
            Mock(), RelativeOffsetCoordinate(0, 0)
        )
        assert cut_track_dataset == dataset
        assert original_track_ids == set()

    def test_track_ids(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PandasTrackDataset(track_geometry_factory)
        assert dataset.track_ids == frozenset()
        updated_dataset = dataset.add_all([car_track, pedestrian_track])
        assert updated_dataset.track_ids == frozenset(
            [car_track.id, pedestrian_track.id]
        )

    def test_empty(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY, car_track: Track
    ) -> None:
        empty_dataset = PandasTrackDataset(track_geometry_factory)
        assert empty_dataset.empty
        filled_dataset = empty_dataset.add_all([car_track])
        assert not filled_dataset.empty

    def test_get_max_confidences_for(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        empty_dataset = PandasTrackDataset(track_geometry_factory)
        with pytest.raises(TrackDoesNotExistError):
            empty_dataset.get_max_confidences_for([car_track.id.id])
        filled_dataset = empty_dataset.add_all([car_track, pedestrian_track])

        car_id = car_track.id.id
        pedestrian_id = pedestrian_track.id.id

        result = filled_dataset.get_max_confidences_for([car_id, pedestrian_id])
        assert result == {car_id: 0.8, pedestrian_id: 0.9}

    def test_create_test_flyweight_with_single_detection(
        self, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> None:
        track_builder = TrackBuilder()
        track_builder.append_detection()
        single_detection_track = track_builder.build_track()
        dataset = PandasTrackDataset.from_list(
            [single_detection_track], track_geometry_factory
        )
        result = dataset._create_track_flyweight(single_detection_track.id.id)
        assert_equal_track_properties(result, single_detection_track)

    def test_initializing_empty_dataset_has_correct_columns_index(self) -> None:
        """
        #Bugfix https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/5291

        @bug by randy-seng
        """  # noqa
        target = PandasTrackDataset(track_geometry_factory=Mock())
        actual = target.get_data()
        assert actual.index.names == INDEX_NAMES
        assert INDEX_NAMES not in actual.columns.to_list()
        assert set(COLUMNS) - set(INDEX_NAMES) == set(actual.columns.to_list())


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
