from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import Mock, call

import polars as pl
import pytest

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.section import LineSection, Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_GEO_X,
    END_GEO_Y,
    START_GEO_X,
    START_GEO_Y,
    IncompatibleGeoreferenceMetadataError,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.polars_track_id_set import PolarsTrackIdSet
from OTAnalytics.plugin_datastore.polars_track_store import (
    COLUMNS,
    GEO_COLUMNS,
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsDetection,
    PolarsTrackDataset,
    PolarsTrackSegmentDataset,
    _convert_tracks,
    create_empty_dataframe,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat
from tests.utils.assertions import assert_equal_track_properties
from tests.utils.builders.track_builder import (
    TrackBuilder,
    mark_last_detection_finished,
)


def create_line_section(
    section_id: str, coordinates: list[tuple[float, float]]
) -> Section:
    section = Mock(spec=LineSection)
    section.get_coordinates.return_value = [
        Coordinate(coord[0], coord[1]) for coord in coordinates
    ]
    # Provide the relative_offset_coordinates mapping expected by get_section_offset
    section.relative_offset_coordinates = {
        EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.0, 0.0)
    }
    # Keep legacy helper for any code paths expecting get_offset(event_type)
    section.get_offset.return_value = RelativeOffsetCoordinate(0.0, 0.0)
    section.id = SectionId(section_id)
    return section


@dataclass
class ContainedBySectionTestCase:
    tracks: list[Track]
    sections: list[Section]
    expected_result: dict[TrackId, list[tuple[SectionId, list[bool]]]]


@pytest.fixture
def contained_by_section_test_case(
    straight_track: Track, complex_track: Track, closed_track: Track
) -> ContainedBySectionTestCase:
    # Straight track starts outside section
    first_section = create_line_section(
        "1", [(1.5, 0.5), (1.5, 1.5), (2.5, 1.5), (2.5, 0.5), (1.5, 0.5)]
    )
    # Straight track starts inside section
    second_section = create_line_section(
        "2", [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)]
    )
    # Straight track is inside section
    third_section = create_line_section(
        "3", [(0.0, 0.0), (0.0, 2.0), (4.0, 2.0), (4.0, 0.0), (0.0, 0.0)]
    )
    # Straight track starts outside stays inside section
    fourth_section = create_line_section(
        "4", [(1.5, 0.5), (1.5, 1.5), (4.0, 1.5), (4.0, 0.5), (1.5, 0.5)]
    )
    # Complex track starts outside section with multiple intersections
    fifth_section = create_line_section(
        "5",
        [(1.5, 0.5), (1.5, 2.5), (2.5, 2.5), (2.5, 0.5), (1.5, 0.5)],
    )
    # Complex track starts inside section with multiple intersections
    sixth_section = create_line_section(
        "6", [(0.5, 0.5), (0.5, 2.5), (1.5, 2.5), (1.5, 0.5), (0.5, 0.5)]
    )
    # Closed track
    seventh_section = create_line_section(
        "7", [(1.5, 0.5), (1.5, 2.0), (2.5, 2.0), (2.5, 0.5), (1.5, 0.5)]
    )
    # Not contained track
    eighth_section = create_line_section(
        "not-contained", [(3.0, 1.0), (3.0, 2.0), (4.0, 2.0), (4.0, 1.0), (3.0, 1.0)]
    )
    expected = {
        straight_track.id: [
            (first_section.id, [False, True, False]),
            (second_section.id, [True, False, False]),
            (third_section.id, [True, True, True]),
            (fourth_section.id, [False, True, True]),
            (fifth_section.id, [False, True, False]),
            (sixth_section.id, [True, False, False]),
            (seventh_section.id, [False, True, False]),
        ],
        complex_track.id: [
            (first_section.id, [False, True, False, False, False, False]),
            (second_section.id, [True, False, False, False, False, False]),
            (third_section.id, [True, True, True, True, False, False]),
            (fourth_section.id, [False, True, False, False, False, False]),
            (fifth_section.id, [False, True, True, False, False, True]),
            (sixth_section.id, [True, False, False, True, True, False]),
            (seventh_section.id, [False, True, True, False, False, False]),
        ],
        closed_track.id: [
            (first_section.id, [False, True, False, False, False]),
            (second_section.id, [True, False, False, False, True]),
            (third_section.id, [True, True, False, False, True]),
            (fourth_section.id, [False, True, False, False, False]),
            (fifth_section.id, [False, True, True, False, False]),
            (sixth_section.id, [True, False, False, True, True]),
            (seventh_section.id, [False, True, False, False, False]),
        ],
    }
    return ContainedBySectionTestCase(
        [straight_track, complex_track, closed_track],
        [
            first_section,
            second_section,
            third_section,
            fourth_section,
            fifth_section,
            sixth_section,
            seventh_section,
            eighth_section,
        ],
        expected,
    )


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

    def test_split_finished(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        unfinished_track = self.__build_track("unfinished")
        finished_track = mark_last_detection_finished(self.__build_track("finished"))
        dataset = PolarsTrackDataset.from_list(
            [unfinished_track, finished_track], track_geometry_factory
        )

        finished, remaining = dataset.split_finished()

        finished_ids = {track_id.id for track_id in finished.track_ids}
        remaining_ids = {track_id.id for track_id in remaining.track_ids}
        assert finished_ids == {finished_track.id.id}
        assert remaining_ids == {unfinished_track.id.id}

    def test_split_finished_empty_dataset(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory)

        finished, remaining = dataset.split_finished()

        assert finished.empty
        assert remaining.empty

    def test_split_finished_without_finished_tracks(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = self.__build_track("1")
        second_track = self.__build_track("2")
        dataset = PolarsTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        finished, remaining = dataset.split_finished()

        assert finished.empty
        remaining_ids = {track_id.id for track_id in remaining.track_ids}
        assert remaining_ids == {first_track.id.id, second_track.id.id}

    def test_split_finished_without_remaining_tracks(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        first_track = mark_last_detection_finished(self.__build_track("1"))
        second_track = mark_last_detection_finished(self.__build_track("2"))
        dataset = PolarsTrackDataset.from_list(
            [first_track, second_track], track_geometry_factory
        )

        finished, remaining = dataset.split_finished()

        finished_ids = {track_id.id for track_id in finished.track_ids}
        assert finished_ids == {first_track.id.id, second_track.id.id}
        assert remaining.empty

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

        result = dataset.remove_multiple(
            PolarsTrackIdSet({TrackId("second"), TrackId("fourth")})
        )

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
        expected = PolarsTrackIdSet({car_track.id, pedestrian_track.id})
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

    def test_contained_by_sections(
        self,
        contained_by_section_test_case: ContainedBySectionTestCase,
    ) -> None:
        unused_offset = RelativeOffsetCoordinate(0, 0)
        track_dataset = PolarsTrackDataset.from_list(
            contained_by_section_test_case.tracks,
            PolarsTrackGeometryDataset.from_track_dataset,
        )
        result = track_dataset.contained_by_sections(
            contained_by_section_test_case.sections, unused_offset
        )
        expected_result = contained_by_section_test_case.expected_result
        for track_id in expected_result:
            result_data = result[track_id]
            expected_data = expected_result[track_id]
            assert result_data == expected_data
        assert result == expected_result

    def test_cut_with_section_no_null_track_ids_with_single_detection(
        self,
        car_track: Track,
        single_detection_track: Track,
    ) -> None:
        """
        Regression test for a bug where cut_with_section produced null TRACK_IDs
        after the join on ROW_ID (notably for single-detection tracks with no segments).
        Ensure that TRACK_IDs are backfilled and contain no nulls.
        """
        dataset = PolarsTrackDataset.from_list(
            [car_track, single_detection_track],
            PolarsTrackGeometryDataset.from_track_dataset,
        )

        # A simple vertical line; intersections are not required for this check,
        # we only need segment creation to run and the join to occur
        section = create_line_section("cut", [(2.5, 0.0), (2.5, 3.0)])
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        result_dataset, _ = dataset.cut_with_section(section, offset)
        df = result_dataset.get_data()

        # Assert no null TRACK_ID values remain after cut
        assert df.filter(pl.col(track.TRACK_ID).is_null()).is_empty()

        # And the single-detection track is still present in the result
        unique_ids = df.get_column(track.TRACK_ID).unique().to_list()
        assert single_detection_track.id.id in unique_ids


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


@dataclass
class PolarsDetectionGeoGiven:
    """Holds PolarsDetection instances for geo coordinate tests."""

    detection_with_geo: PolarsDetection
    detection_without_geo: PolarsDetection


GEO_X = 449245.82
GEO_Y = 5699325.96


def create_polars_detection_geo_given() -> PolarsDetectionGeoGiven:
    """Creates a PolarsDetectionGeoGiven with and without geo keys in row data."""
    occurrence = datetime(2024, 1, 1, tzinfo=timezone.utc)
    row_with = {
        track.CLASSIFICATION: "car",
        track.CONFIDENCE: 0.9,
        track.X: 100.0,
        track.Y: 200.0,
        track.W: 0.0,
        track.H: 0.0,
        track.FRAME: 1,
        track.INTERPOLATED_DETECTION: False,
        track.VIDEO_NAME: "cam.mp4",
        track.INPUT_FILE: "cam.otdet",
        track.GEO_X: GEO_X,
        track.GEO_Y: GEO_Y,
    }
    row_without = {
        k: v for k, v in row_with.items() if k not in (track.GEO_X, track.GEO_Y)
    }
    return PolarsDetectionGeoGiven(
        detection_with_geo=PolarsDetection("track-1", row_with, occurrence),
        detection_without_geo=PolarsDetection("track-1", row_without, occurrence),
    )


class TestPolarsDetectionGeoCoordinates:
    def test_geo_x_returns_value_when_key_present(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_with_geo.geo_x == GEO_X

    def test_geo_y_returns_value_when_key_present(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_with_geo.geo_y == GEO_Y

    def test_geo_x_returns_none_when_key_absent(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_without_geo.geo_x is None

    def test_geo_y_returns_none_when_key_absent(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_without_geo.geo_y is None


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


class TestPolarsTrackDatasetGeoreferenceMetadata:
    def test_georeference_metadata_is_none_by_default(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        assert dataset.georeference_metadata is None

    def test_with_georeference_metadata_returns_new_dataset_with_metadata(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        updated = dataset.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        assert updated.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_with_georeference_metadata_does_not_mutate_original(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        dataset.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        assert dataset.georeference_metadata is None

    def test_from_dataframe_empty_input_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        empty_df = pl.DataFrame()
        result = PolarsTrackDataset.from_dataframe(
            empty_df,
            track_geometry_factory,
            georeference_metadata=SAMPLE_GEOREFERENCE_METADATA,
        )
        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_split_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        batches = dataset.split(2)

        assert all(
            batch.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA
            for batch in batches
        )

    def test_remove_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.remove(car_track.id)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_remove_multiple_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.remove_multiple(PolarsTrackIdSet([car_track.id.id]))

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_filter_by_min_detection_length_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.filter_by_min_detection_length(1)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_clear_drops_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.clear()

        assert result.georeference_metadata is None

    def test_split_finished_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        # All detections are unfinished → split returns (empty_finished, self_remaining)
        empty_finished, remaining = dataset.split_finished()

        assert empty_finished.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA
        assert remaining.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_split_finished_with_finished_tracks_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        finished_track = mark_last_detection_finished(car_track)
        dataset = PolarsTrackDataset.from_list(
            [finished_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        finished, remaining = dataset.split_finished()

        assert finished.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA
        assert remaining.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_revert_cuts_for_preserves_georeference_metadata(
        self,
        car_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track], PolarsTrackGeometryDataset.from_track_dataset
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        # Vertical section at x=1.5 intersects car_track (1,1)→(2,2)
        section = create_line_section("revert_cut", [(1.5, 0.0), (1.5, 3.0)])
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        cut_dataset, original_ids = dataset.cut_with_section(section, offset)
        cut_dataset = cut_dataset.with_georeference_metadata(
            SAMPLE_GEOREFERENCE_METADATA
        )

        result_dataset, _, _ = cut_dataset.revert_cuts_for(original_ids)

        assert result_dataset.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_remove_by_original_ids_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result_dataset, _ = dataset.remove_by_original_ids(PolarsTrackIdSet([]))

        assert result_dataset.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_cut_with_section_preserves_georeference_metadata(
        self,
        car_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track], PolarsTrackGeometryDataset.from_track_dataset
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        # A vertical section that does not intersect the car track coordinates
        section = create_line_section("cut_meta", [(100.0, 0.0), (100.0, 10.0)])
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        result_dataset, _ = dataset.cut_with_section(section, offset)

        assert result_dataset.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA


ALTERNATE_GEOREFERENCE_METADATA = GeoreferenceMetadata(
    geo_min_x=1.0,
    geo_min_y=1.0,
    geo_max_x=101.0,
    geo_max_y=101.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)


class TestPolarsTrackDatasetAddAllGeoreferenceValidation:
    def test_add_all_to_empty_inherits_incoming_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        empty = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        incoming = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = empty.add_all(incoming)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_add_all_to_empty_with_no_incoming_metadata_keeps_none(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        empty = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        incoming = PolarsTrackDataset.from_list([car_track], track_geometry_factory)

        result = empty.add_all(incoming)

        assert result.georeference_metadata is None

    def test_add_all_with_matching_metadata_succeeds(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = current.add_all(incoming)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_add_all_with_mismatched_metadata_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(ALTERNATE_GEOREFERENCE_METADATA)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all(incoming)

    def test_add_all_populated_without_metadata_and_incoming_with_metadata_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all(incoming)

    def test_add_all_populated_with_metadata_and_incoming_without_metadata_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all(incoming)

    def test_add_all_both_without_metadata_succeeds(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )

        result = current.add_all(incoming)

        assert result.georeference_metadata is None

    def test_add_all_populated_with_metadata_and_plain_track_list_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        """Passing a raw list of Track objects into a populated metadata-bearing
        dataset is unsafe: raw tracks carry no metadata, so the merge would
        silently dilute the georeferenced invariant. The strict equality
        check raises.
        """
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all([pedestrian_track])

    def test_add_all_empty_incoming_is_noop_even_with_mismatched_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        """An empty incoming dataset never triggers validation: there is no
        detection to merge, so the metadata invariant cannot be violated.
        The current dataset is returned unchanged.
        """
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        empty_incoming = PolarsTrackDataset(
            track_geometry_factory=track_geometry_factory
        ).with_georeference_metadata(ALTERNATE_GEOREFERENCE_METADATA)

        result = current.add_all(empty_incoming)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA


class TestPolarsTrackDatasetAddAllGeoNullPadding:
    @pytest.fixture
    def dataset_without_geo_cols(
        self, car_track: Track, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> PolarsTrackDataset:
        return PolarsTrackDataset.from_list([car_track], track_geometry_factory)

    @pytest.fixture
    def dataset_with_geo_cols(
        self,
        pedestrian_track: Track,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> PolarsTrackDataset:
        ped_base = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )
        df_ped = ped_base.get_data().with_columns(
            pl.lit(3.0).alias(track.GEO_X),
            pl.lit(4.0).alias(track.GEO_Y),
        )
        return PolarsTrackDataset.from_dataframe(df_ped, track_geometry_factory)

    def test_add_with_geo_pads_null_into_incoming_without_geo_and_vice_versa(
        self,
        dataset_without_geo_cols: PolarsTrackDataset,
        dataset_with_geo_cols: PolarsTrackDataset,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        with_geo_on_without = dataset_without_geo_cols.add_all(dataset_with_geo_cols)
        without_geo_on_with = dataset_with_geo_cols.add_all(dataset_without_geo_cols)
        for actual in [with_geo_on_without, without_geo_on_with]:
            actual_data = actual.get_data()
            assert track.GEO_X in actual_data.columns
            assert track.GEO_Y in actual_data.columns
            car_rows = actual_data.filter(pl.col(track.TRACK_ID) == car_track.id.id)
            ped_rows = actual_data.filter(
                pl.col(track.TRACK_ID) == pedestrian_track.id.id
            )
            assert car_rows[track.GEO_X].is_null().all()
            assert car_rows[track.GEO_Y].is_null().all()
            assert (ped_rows[track.GEO_X] == 3.0).all()
            assert (ped_rows[track.GEO_Y] == 4.0).all()


GEO_X_VALUES = [449250.0, 449260.0, 449270.0]
GEO_Y_VALUES = [5855000.0, 5855010.0, 5855020.0]
VIDEO_NAME_VALUE = "myhostname_something.mp4"
INPUT_FILE_VALUE = "myhostname_something.ottrk"


def _build_segment_dataset(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    *,
    include_geo: bool,
) -> PolarsTrackDataset:
    """Build a PolarsTrackDataset for segment geo column tests.

    Args:
        track_geometry_factory: Factory used to construct the dataset.
        include_geo: When True, the dataset includes geo_x and geo_y columns.

    Returns:
        A PolarsTrackDataset backed by a minimal single-track DataFrame.
    """
    base: dict = {
        track.TRACK_ID: ["1", "1", "1"],
        track.TRACK_CLASSIFICATION: ["car", "car", "car"],
        track.CLASSIFICATION: ["car", "car", "car"],
        track.CONFIDENCE: [0.9, 0.9, 0.9],
        track.X: [10.0, 20.0, 30.0],
        track.Y: [5.0, 5.0, 5.0],
        track.W: [5.0, 5.0, 5.0],
        track.H: [5.0, 5.0, 5.0],
        track.FRAME: [1, 2, 3],
        track.OCCURRENCE: [
            datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2022, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
            datetime(2022, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
        ],
        track.INTERPOLATED_DETECTION: [False, False, False],
        track.VIDEO_NAME: [VIDEO_NAME_VALUE] * 3,
        track.INPUT_FILE: [INPUT_FILE_VALUE] * 3,
        track.ORIGINAL_TRACK_ID: ["1", "1", "1"],
        ottrk_dataformat.FIRST: [True, False, False],
        ottrk_dataformat.FINISHED: [False, False, True],
    }
    if include_geo:
        base[track.GEO_X] = GEO_X_VALUES
        base[track.GEO_Y] = GEO_Y_VALUES
    return PolarsTrackDataset.from_dataframe(pl.DataFrame(base), track_geometry_factory)


@dataclass
class GivenSegmentGeo:
    """Holds PolarsTrackDataset instances for segment geo column tests."""

    dataset_with_geo: PolarsTrackDataset
    dataset_without_geo: PolarsTrackDataset


def create_given_segment_geo(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
) -> GivenSegmentGeo:
    """Create GivenSegmentGeo with and without geo columns for testing."""
    return GivenSegmentGeo(
        dataset_with_geo=_build_segment_dataset(
            track_geometry_factory, include_geo=True
        ),
        dataset_without_geo=_build_segment_dataset(
            track_geometry_factory, include_geo=False
        ),
    )


def setup_default_segment_geo(given: GivenSegmentGeo) -> GivenSegmentGeo:
    """Return the given instance unchanged (no default configuration needed)."""
    return given


def create_target_segment_geo(given: GivenSegmentGeo) -> PolarsTrackDataset:
    """Return the dataset with geo columns as the system under test."""
    return given.dataset_with_geo


def create_target_segment_geo_without_geo(given: GivenSegmentGeo) -> PolarsTrackDataset:
    """Return the dataset without geo columns as the system under test."""
    return given.dataset_without_geo


class TestGetSegmentsPreservesGeoColumns:
    def test_first_segments_include_start_geo_columns(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        given = setup_default_segment_geo(
            create_given_segment_geo(track_geometry_factory)
        )
        target = create_target_segment_geo(given)

        rows: list[dict] = []
        target.get_first_segments().apply(rows.append)

        assert rows[0][START_GEO_X] == GEO_X_VALUES[0]
        assert rows[0][START_GEO_Y] == GEO_Y_VALUES[0]

    def test_last_segments_include_end_geo_columns(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        given = setup_default_segment_geo(
            create_given_segment_geo(track_geometry_factory)
        )
        target = create_target_segment_geo(given)

        rows: list[dict] = []
        target.get_last_segments().apply(rows.append)

        assert rows[0][END_GEO_X] == GEO_X_VALUES[-1]
        assert rows[0][END_GEO_Y] == GEO_Y_VALUES[-1]

    def test_segments_without_geo_data_have_no_geo_keys(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        given = setup_default_segment_geo(
            create_given_segment_geo(track_geometry_factory)
        )
        target = create_target_segment_geo_without_geo(given)

        rows: list[dict] = []
        target.get_first_segments().apply(rows.append)

        assert START_GEO_X not in rows[0]
        assert START_GEO_Y not in rows[0]


@dataclass
class GivenMergeAll:
    dataset_a: PolarsTrackDataset
    dataset_b: PolarsTrackDataset


def create_given_merge_all(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    car_track: Track,
    pedestrian_track: Track,
) -> GivenMergeAll:
    ds_a = PolarsTrackDataset.from_list(
        [car_track], track_geometry_factory
    ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
    ds_b = PolarsTrackDataset.from_list(
        [pedestrian_track], track_geometry_factory
    ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
    return GivenMergeAll(dataset_a=ds_a, dataset_b=ds_b)


def setup_default_merge_all(given: GivenMergeAll) -> GivenMergeAll:
    return given


def create_target_merge_all(given: GivenMergeAll) -> PolarsTrackDataset:
    return PolarsTrackDataset.merge_all([given.dataset_a, given.dataset_b])


class TestPolarsTrackDatasetMergeAll:
    def test_raises_on_empty_list(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        with pytest.raises(ValueError, match="No datasets to merge"):
            PolarsTrackDataset.merge_all([])

    def test_combines_tracks_from_all_datasets(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        given = setup_default_merge_all(
            create_given_merge_all(track_geometry_factory, car_track, pedestrian_track)
        )
        target = create_target_merge_all(given)

        assert len(target) == 2

    def test_result_carries_shared_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        given = setup_default_merge_all(
            create_given_merge_all(track_geometry_factory, car_track, pedestrian_track)
        )
        target = create_target_merge_all(given)

        assert target.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_raises_on_incompatible_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        different_metadata = GeoreferenceMetadata(
            geo_min_x=0.0,
            geo_min_y=0.0,
            geo_max_x=1.0,
            geo_max_y=1.0,
            birds_eye_view_width=100,
            birds_eye_view_height=100,
            padding=0,
            crs="EPSG:4326",
        )
        ds_a = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        ds_b = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(different_metadata)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            PolarsTrackDataset.merge_all([ds_a, ds_b])

    def test_result_has_none_metadata_when_all_datasets_have_none(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        ds_a = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        ds_b = PolarsTrackDataset.from_list([pedestrian_track], track_geometry_factory)

        result = PolarsTrackDataset.merge_all([ds_a, ds_b])

        assert result.georeference_metadata is None

    def test_all_empty_datasets_returns_empty_with_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        ds_a = PolarsTrackDataset(track_geometry_factory).with_georeference_metadata(
            SAMPLE_GEOREFERENCE_METADATA
        )
        ds_b = PolarsTrackDataset(track_geometry_factory).with_georeference_metadata(
            SAMPLE_GEOREFERENCE_METADATA
        )

        result = PolarsTrackDataset.merge_all([ds_a, ds_b])

        assert result.empty
        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_single_dataset_returns_equivalent_result(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        ds = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = PolarsTrackDataset.merge_all([ds])

        assert len(result) == 1
        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_empty_datasets_are_skipped_in_concat_but_metadata_is_validated(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        ds_with_tracks = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        ds_empty = PolarsTrackDataset(
            track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = PolarsTrackDataset.merge_all([ds_with_tracks, ds_empty])

        assert len(result) == 1
        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_geo_columns_preserved_when_all_datasets_have_them(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        ds_a_base = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        ds_b_base = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )
        df_a = ds_a_base.get_data().with_columns(
            pl.lit(1.0).alias(track.GEO_X),
            pl.lit(2.0).alias(track.GEO_Y),
        )
        df_b = ds_b_base.get_data().with_columns(
            pl.lit(3.0).alias(track.GEO_X),
            pl.lit(4.0).alias(track.GEO_Y),
        )
        ds_a = PolarsTrackDataset.from_dataframe(df_a, track_geometry_factory)
        ds_b = PolarsTrackDataset.from_dataframe(df_b, track_geometry_factory)

        result = PolarsTrackDataset.merge_all([ds_a, ds_b])

        assert track.GEO_X in result.get_data().columns
        assert track.GEO_Y in result.get_data().columns

    def test_geo_columns_null_padded_when_only_some_datasets_have_them(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        ds_a_base = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        ds_b_base = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )
        df_a = ds_a_base.get_data().with_columns(
            pl.lit(1.0).alias(track.GEO_X),
            pl.lit(2.0).alias(track.GEO_Y),
        )
        ds_a = PolarsTrackDataset.from_dataframe(df_a, track_geometry_factory)
        ds_b = ds_b_base  # no geo columns

        result = PolarsTrackDataset.merge_all([ds_a, ds_b])

        data = result.get_data()
        assert track.GEO_X in data.columns
        assert track.GEO_Y in data.columns
        car_rows = data.filter(pl.col(track.TRACK_ID) == car_track.id.id)
        pedestrian_rows = data.filter(pl.col(track.TRACK_ID) == pedestrian_track.id.id)
        assert (car_rows[track.GEO_X] == 1.0).all()
        assert (car_rows[track.GEO_Y] == 2.0).all()
        assert pedestrian_rows[track.GEO_X].is_null().all()
        assert pedestrian_rows[track.GEO_Y].is_null().all()


class TestDatasetHasCompleteGeoValues:
    def test_returns_true_when_geo_columns_present_and_all_non_null(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        ds = _build_segment_dataset(track_geometry_factory, include_geo=True)
        assert dataset_has_complete_geo_values(ds) is True

    def test_returns_false_when_geo_columns_absent(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        ds = _build_segment_dataset(track_geometry_factory, include_geo=False)
        assert dataset_has_complete_geo_values(ds) is False

    def test_returns_false_when_geo_columns_present_but_contain_nulls(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        ds_a_base = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        ds_b_base = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )
        df_a = ds_a_base.get_data().with_columns(
            pl.lit(1.0).alias(track.GEO_X),
            pl.lit(2.0).alias(track.GEO_Y),
        )
        ds_a = PolarsTrackDataset.from_dataframe(df_a, track_geometry_factory)
        ds_b = ds_b_base
        mixed = PolarsTrackDataset.merge_all([ds_a, ds_b])
        assert dataset_has_complete_geo_values(mixed) is False

    def test_returns_false_for_empty_dataset(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        ds = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        assert dataset_has_complete_geo_values(ds) is False


def dataset_has_complete_geo_values(dataset: PolarsTrackDataset) -> bool:
    df = dataset.get_data()
    if df.is_empty():
        return False
    for col in GEO_COLUMNS:
        if col not in df.columns:
            return False
        if df[col].is_null().any():
            return False
    return True
