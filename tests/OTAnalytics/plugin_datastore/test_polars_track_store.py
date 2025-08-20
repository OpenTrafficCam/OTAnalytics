from unittest.mock import Mock, call

import polars as pl

from OTAnalytics.domain import track
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.plugin_datastore.polars_track_store import (
    COLUMNS,
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsDetection,
    PolarsTrackDataset,
    PolarsTrackSegmentDataset,
    _convert_tracks,
    create_empty_dataframe,
)
from tests.utils.assertions import assert_equal_track_properties
from tests.utils.builders.track_builder import TrackBuilder


class TestPolarsDetection:
    def test_properties(self) -> None:
        track_id = "track_1"
        data = {
            track.CLASSIFICATION: "car",
            track.CONFIDENCE: 0.9,
            track.X: 100.0,
            track.Y: 200.0,
            track.W: 50.0,
            track.H: 30.0,
            track.FRAME: 1,
            track.INTERPOLATED_DETECTION: False,
            track.VIDEO_NAME: "video.mp4",
            track.INPUT_FILE: "input.ottrk",
        }
        occurrence = TrackBuilder().create_detection().occurrence

        detection = PolarsDetection(track_id, data, occurrence)

        assert detection.track_id == TrackId(track_id)
        assert detection.classification == "car"
        assert detection.confidence == 0.9
        assert detection.x == 100.0
        assert detection.y == 200.0
        assert detection.w == 50.0
        assert detection.h == 30.0
        assert detection.frame == 1
        assert not detection.interpolated_detection
        assert detection.video_name == "video.mp4"
        assert detection.input_file == "input.ottrk"
        assert detection.occurrence == occurrence


class TestPolarsTrack:
    def test_properties(self) -> None:
        track = self.create_python_track()
        pandas_track = self.create_polars_track(track)
        assert_equal_track_properties(pandas_track, track)

    def create_python_track(self) -> Track:
        builder = TrackBuilder().add_track_id("1")
        builder.append_detection()
        builder.append_detection()
        builder.append_detection()
        return builder.build_track()

    def create_polars_track(self, track: Track) -> Track:
        dataset = PolarsTrackDataset.from_list([track], Mock())
        return dataset._create_track_flyweight(track.id.id)


class TestPolarsTrackSegmentDataset:
    def test_apply(self) -> None:
        consumer = Mock()
        segments = [
            {"segment_1": "value_1"},
            {"segment_2": "value_2"},
            {"segment_3": "value_3"},
        ]
        df = pl.DataFrame(segments)
        dataset = PolarsTrackSegmentDataset(df)

        dataset.apply(consumer)

        expected_calls = [call(segment) for segment in segments]
        consumer.assert_has_calls(expected_calls)

    def test_apply_without_segments(self) -> None:
        consumer = Mock()
        df = pl.DataFrame()
        dataset = PolarsTrackSegmentDataset(df)

        dataset.apply(consumer)

        consumer.assert_not_called()


class TestPolarsTrackDataset:
    def _create_dataset(self, size: int) -> list[Track]:
        return [self.__build_track(f"track_{i}") for i in range(size)]

    def test_use_track_classificator(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        calculator = Mock()
        builder = TrackBuilder().add_track_id("1")
        builder.append_detection()
        builder.append_detection()
        tracks = [builder.build_track()]
        dataset = _convert_tracks(tracks)
        calculator.calculate.return_value = pl.DataFrame(
            {track.TRACK_ID: ["1"], track.TRACK_CLASSIFICATION: ["car"]}
        )

        track_dataset = PolarsTrackDataset.from_dataframe(
            dataset, track_geometry_factory, calculator=calculator
        )

        assert track_dataset
        calculator.calculate.assert_called_once()

    def test_add(self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        dataset = PolarsTrackDataset.from_list([first_track], track_geometry_factory)

        result = dataset.add_all([second_track])

        assert len(result) == 2
        track_ids = {track_id.id for track_id in result.track_ids}
        assert track_ids == {"first", "second"}

    def test_add_nothing(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("first")
        dataset = PolarsTrackDataset.from_list([first_track], track_geometry_factory)

        result = dataset.add_all([])

        assert result == dataset

    def test_add_all(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        third_track = self.__build_track("third")
        dataset = PolarsTrackDataset.from_list([first_track], track_geometry_factory)

        result = dataset.add_all([second_track, third_track])

        assert len(result) == 3
        track_ids = {track_id.id for track_id in result.track_ids}
        assert track_ids == {"first", "second", "third"}

    def test_add_two_existing_polars_datasets(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        first_dataset = PolarsTrackDataset.from_list(
            [first_track], track_geometry_factory
        )
        second_dataset = PolarsTrackDataset.from_list(
            [second_track], track_geometry_factory
        )

        result = first_dataset.add_all(second_dataset)

        assert len(result) == 2
        track_ids = {track_id.id for track_id in result.track_ids}
        assert track_ids == {"first", "second"}

    def test_add_all_merge_tracks(
        self,
        car_track: Track,
        car_track_continuing: Track,
        pedestrian_track: Track,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        # Test that adding tracks with same ID merges them properly
        dataset = PolarsTrackDataset.from_list([car_track], track_geometry_factory)

        result = dataset.add_all([car_track_continuing, pedestrian_track])

        # Should have 2 unique tracks (car merged, pedestrian separate)
        assert len(result) == 2
        track_ids = {track_id.id for track_id in result.track_ids}
        expected_track_ids = {car_track.id.id, pedestrian_track.id.id}
        assert track_ids == expected_track_ids

    def __build_track(self, track_id: str, length: int = 5) -> Track:
        builder = TrackBuilder().add_track_id(track_id)
        for i in range(length):
            builder.append_detection()
        return builder.build_track()

    def test_get_for(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        dataset = PolarsTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        result = dataset.get_for(TrackId("first"))

        assert result is not None
        assert result.id == TrackId("first")

    def test_get_for_missing_id(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY, car_track: Track
    ) -> None:
        dataset = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        result = dataset.get_for(TrackId("missing"))
        assert result is None

    def test_get_for_missing_id_on_empty_dataset(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory)
        result = dataset.get_for(TrackId("missing"))
        assert result is None

    def test_clear(self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        dataset = PolarsTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        result = dataset.clear()

        assert len(result) == 0
        assert result.empty

    def test_remove(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        third_track = self.__build_track("third")
        dataset = PolarsTrackDataset.from_list(
            [first_track, second_track, third_track], track_geometry_factory
        )

        result = dataset.remove(TrackId("second"))

        assert len(result) == 2
        track_ids = {track_id.id for track_id in result.track_ids}
        assert track_ids == {"first", "third"}

    def test_remove_multiple(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("first")
        second_track = self.__build_track("second")
        third_track = self.__build_track("third")
        fourth_track = self.__build_track("fourth")
        dataset = PolarsTrackDataset.from_list(
            [first_track, second_track, third_track, fourth_track],
            track_geometry_factory,
        )

        result = dataset.remove_multiple({TrackId("second"), TrackId("fourth")})

        assert len(result) == 2
        track_ids = {track_id.id for track_id in result.track_ids}
        assert track_ids == {"first", "third"}

    def test_len(self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY) -> None:
        tracks = self._create_dataset(3)
        dataset = PolarsTrackDataset.from_list(tracks, track_geometry_factory)
        assert len(dataset) == 3

    def test_first_occurrence(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        expected_first = min(
            car_track.first_detection.occurrence,
            pedestrian_track.first_detection.occurrence,
        )
        assert dataset.first_occurrence == expected_first

    def test_last_occurrence(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        expected_last = max(
            car_track.last_detection.occurrence,
            pedestrian_track.last_detection.occurrence,
        )
        assert dataset.last_occurrence == expected_last

    def test_first_occurrence_on_empty_dataset(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory)
        assert dataset.first_occurrence is None

    def test_last_occurrence_on_empty_dataset(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory)
        assert dataset.last_occurrence is None

    def test_classifications(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        expected = frozenset(
            {car_track.classification, pedestrian_track.classification}
        )
        assert dataset.classifications == expected

    def test_classifications_on_empty_dataset(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory)
        assert dataset.classifications == frozenset()

    def test_track_ids(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        )
        expected = frozenset({car_track.id, pedestrian_track.id})
        assert dataset.track_ids == expected

    def test_empty(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY, car_track: Track
    ) -> None:
        empty_dataset = PolarsTrackDataset(track_geometry_factory)
        assert empty_dataset.empty

        non_empty_dataset = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        )
        assert not non_empty_dataset.empty

    def test_initializing_empty_dataset_has_correct_columns(self) -> None:
        empty_df = create_empty_dataframe()
        expected_columns = set(COLUMNS)
        actual_columns = set(empty_df.columns)
        assert actual_columns == expected_columns

    def test_create_test_flyweight_with_single_detection(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        track = self.__build_track("test_track", 1)
        dataset = PolarsTrackDataset.from_list([track], track_geometry_factory)

        result = dataset.get_for(track.id)

        assert result is not None
        assert result.id == track.id
        assert len(result.detections) == 1


def test_convert_tracks() -> None:
    builder = TrackBuilder().add_track_id("1")
    builder.append_detection()
    builder.append_detection()
    built_track = builder.build_track()

    result = _convert_tracks([built_track])

    assert not result.is_empty()
    assert len(result) == 2  # 2 detections
    assert track.TRACK_ID in result.columns
    assert track.OCCURRENCE in result.columns


def test_create_empty_dataframe() -> None:
    result = create_empty_dataframe()

    assert result.is_empty()
    expected_columns = set(COLUMNS)
    actual_columns = set(result.columns)
    assert actual_columns == expected_columns
