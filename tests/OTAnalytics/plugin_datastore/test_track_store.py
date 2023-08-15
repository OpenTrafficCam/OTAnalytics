from pandas import DataFrame, Series, concat

from OTAnalytics.domain.track import Detection, PythonTrackDataset, Track, TrackId
from OTAnalytics.plugin_datastore.track_store import (
    PandasDetection,
    PandasTrack,
    PandasTrackDataset,
)
from tests.conftest import TrackBuilder


def assert_equal_detection_properties(
    pandas_detection: Detection, python_detection: Detection
) -> None:
    assert python_detection.classification == pandas_detection.classification
    assert python_detection.confidence == pandas_detection.confidence
    assert python_detection.x == pandas_detection.x
    assert python_detection.y == pandas_detection.y
    assert python_detection.w == pandas_detection.w
    assert python_detection.h == pandas_detection.h
    assert python_detection.frame == pandas_detection.frame
    assert python_detection.occurrence == pandas_detection.occurrence
    assert python_detection.input_file_path == pandas_detection.input_file_path
    assert (
        python_detection.interpolated_detection
        == pandas_detection.interpolated_detection
    )
    assert python_detection.track_id == pandas_detection.track_id


def assert_equal_track_properties(pandas_track: Track, python_track: Track) -> None:
    assert python_track.id == pandas_track.id
    assert python_track.classification == pandas_track.classification
    for python, pandas in zip(python_track.detections, pandas_track.detections):
        assert_equal_detection_properties(pandas, python)


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
        pandas_track = PandasTrack(data)

        assert_equal_track_properties(pandas_track, python_track)


class TestPandasTrackDataset:
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
        first_detections, first_track = self.__build_track(1)
        second_detections, second_track = self.__build_track(2)
        expected_dataset = PandasTrackDataset(
            concat([DataFrame(first_detections), DataFrame(second_detections)])
        )
        dataset = PandasTrackDataset()
        merged = dataset.add_all(
            PythonTrackDataset(
                {first_track.id: first_track, second_track.id: second_track}
            )
        )

        assert merged == expected_dataset
        assert 0 == len(dataset.as_list())

    def __build_track(self, track_id: int) -> tuple[list[dict], Track]:
        builder = TrackBuilder()
        builder.add_track_id(track_id)
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        first_track = builder.build_track()
        detections = builder.build_serialized_detections()
        return detections, first_track

    def test_get_by_id(self) -> None:
        first_detections, first_track = self.__build_track(1)
        second_detections, second_track = self.__build_track(2)
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        returned = dataset.get_for(first_track.id)

        assert returned is not None
        assert_equal_track_properties(returned, first_track)

    def test_get_missing(self) -> None:
        dataset = PandasTrackDataset()

        returned = dataset.get_for(TrackId(1))

        assert returned is None

    def test_clear(self) -> None:
        first_detections, first_track = self.__build_track(1)
        second_detections, second_track = self.__build_track(2)
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        empty_set = dataset.clear()

        assert 0 == len(empty_set.as_list())
