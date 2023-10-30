from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackDataset
from OTAnalytics.plugin_datastore.track_store import (
    PandasDetection,
    PandasTrack,
    PandasTrackDataset,
)
from tests.conftest import (
    TrackBuilder,
    assert_equal_detection_properties,
    assert_equal_track_properties,
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
        detections = builder.build_serialized_detections()
        expected_dataset = PandasTrackDataset(DataFrame(detections))
        dataset = PandasTrackDataset()

        merged = dataset.add_all(PythonTrackDataset({track.id: track}))

        assert 0 == len(dataset.as_list())
        assert merged == expected_dataset

    def test_add_nothing(self) -> None:
        dataset = PandasTrackDataset()

        merged = dataset.add_all(PythonTrackDataset())

        assert 0 == len(merged.as_list())

    def test_add_all(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        expected_dataset = PandasTrackDataset.from_list([first_track, second_track])
        dataset = PandasTrackDataset()
        merged = dataset.add_all(
            PythonTrackDataset(
                {first_track.id: first_track, second_track.id: second_track}
            )
        )

        assert merged == expected_dataset
        for actual, expected in zip(merged.as_list(), expected_dataset.as_list()):
            assert_equal_track_properties(actual, expected)
        assert 0 == len(dataset.as_list())

    def test_add_two_existing_pandas_datasets(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        expected_dataset = PandasTrackDataset.from_list([first_track, second_track])
        first = PandasTrackDataset.from_list([first_track])
        second = PandasTrackDataset.from_list([second_track])
        merged = first.add_all(second)

        assert merged == expected_dataset
        for actual, expected in zip(merged.as_list(), expected_dataset.as_list()):
            assert_equal_track_properties(actual, expected)

    def __build_track(self, track_id: str) -> Track:
        builder = TrackBuilder()
        builder.add_track_id(track_id)
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
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
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        removed_track_set = dataset.remove(first_track.id)

        assert PandasTrackDataset.from_list([second_track]) == removed_track_set

    def test_len(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        assert len(dataset) == 2
