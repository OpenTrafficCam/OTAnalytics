import pytest
from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, Section, SectionId
from OTAnalytics.domain.track import IntersectionPoint, Track, TrackDataset, TrackId
from OTAnalytics.domain.types import EventType
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


@pytest.fixture
def first_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("1")
    track_builder.add_xy_bbox(1, 1)
    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2, 1)
    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3, 1)
    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(4, 1)
    track_builder.add_frame(4)
    track_builder.add_second(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(5, 1)
    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def second_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("2")
    track_builder.add_xy_bbox(1, 1.5)
    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2, 1.5)
    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3, 1.5)
    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(4, 1.5)
    track_builder.add_frame(4)
    track_builder.add_second(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(5, 1.5)
    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def not_intersecting_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("3")
    track_builder.add_xy_bbox(1, 10)
    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2, 10)
    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3, 10)
    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(4, 10)
    track_builder.add_frame(4)
    track_builder.add_second(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(5, 10)
    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def not_intersecting_section() -> Section:
    name = "first"
    coordinates = [Coordinate(0, 0), Coordinate(0, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def first_section() -> Section:
    name = "first"
    coordinates = [Coordinate(1.5, 0), Coordinate(1.5, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def second_section() -> Section:
    name = "second"
    coordinates = [Coordinate(2.5, 0), Coordinate(2.5, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def third_section() -> Section:
    name = "third"
    coordinates = [Coordinate(3.5, 0), Coordinate(3.5, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
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
        # assert merged == expected_dataset

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
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        removed_track_set = dataset.remove(first_track.id)

        assert PandasTrackDataset.from_list([second_track]) == removed_track_set

    def test_len(self) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        assert len(dataset) == 2

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

    def test_filter_by_minimum_detection_length(self) -> None:
        first_track = self.__build_track("1", length=5)
        second_track = self.__build_track("2", length=10)
        dataset = PandasTrackDataset.from_list([first_track, second_track])

        filtered_dataset = dataset.filter_by_min_detection_length(7)
        assert len(filtered_dataset) == 1
        for actual_track, expected_track in zip(filtered_dataset, [second_track]):
            assert_equal_track_properties(actual_track, expected_track)

    def test_intersection_points(
        self,
        not_intersecting_track: Track,
        first_track: Track,
        second_track: Track,
        not_intersecting_section: Section,
        first_section: Section,
        second_section: Section,
        third_section: Section,
    ) -> None:
        sections = [
            not_intersecting_section,
            first_section,
            second_section,
            third_section,
        ]
        dataset = PandasTrackDataset.from_list(
            [not_intersecting_track, first_track, second_track]
        )
        result = dataset.intersection_points(list(sections))
        assert result == {
            first_track.id: [
                (first_section.id, IntersectionPoint(1)),
                (second_section.id, IntersectionPoint(2)),
                (third_section.id, IntersectionPoint(3)),
            ],
            second_track.id: [
                (first_section.id, IntersectionPoint(1)),
                (second_section.id, IntersectionPoint(2)),
                (third_section.id, IntersectionPoint(3)),
            ],
        }
