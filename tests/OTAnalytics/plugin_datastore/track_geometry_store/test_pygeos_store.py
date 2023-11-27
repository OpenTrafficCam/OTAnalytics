from pathlib import Path
from typing import Iterable
from unittest.mock import MagicMock, Mock

import pytest
from pandas import DataFrame
from pygeos import Geometry, get_coordinates, line_locate_point, linestrings, points
from pytest_benchmark.fixture import BenchmarkFixture

from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import Area, LineSection, Section, SectionId
from OTAnalytics.domain.track import (
    IntersectionPoint,
    Track,
    TrackDataset,
    TrackGeometryDataset,
    TrackId,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    BASE_GEOMETRY,
    COLUMNS,
    GEOMETRY,
    PROJECTION,
    TRACK_ID,
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasByMaxConfidence
from OTAnalytics.plugin_parser.otvision_parser import OtFlowParser, OttrkParser
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from tests.conftest import TrackBuilder


def create_pygeos_track(track: Track) -> Geometry:
    return linestrings([(detection.x, detection.y) for detection in track.detections])


def create_track_dataset(tracks: list[Track]) -> TrackDataset:
    dataset = MagicMock()
    dataset.__iter__.return_value = iter(tracks)
    dataset.__len__.return_value = len(tracks)
    return dataset


def create_geometry_dataset_from(tracks: Iterable[Track]) -> PygeosTrackGeometryDataset:
    entries = []
    for track in tracks:
        _id = track.id.id
        geometry = create_pygeos_track(track)
        projection = [
            line_locate_point(geometry, points(p)) for p in get_coordinates(geometry)
        ]
        entries.append((_id, geometry, projection))
    return PygeosTrackGeometryDataset(
        {
            BASE_GEOMETRY: DataFrame.from_records(
                entries,
                columns=[TRACK_ID, GEOMETRY, PROJECTION],
            ).set_index(TRACK_ID)
        }
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
def first_track_merged(first_track: Track) -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("1")
    track_builder.add_xy_bbox(6, 1)
    track_builder.add_frame(6)
    track_builder.add_second(6)
    track_builder.append_detection()

    track_builder.add_xy_bbox(7, 1)
    track_builder.add_frame(7)
    track_builder.add_second(7)
    track_builder.append_detection()

    track_builder.add_xy_bbox(8, 1)
    track_builder.add_frame(8)
    track_builder.add_second(8)
    track_builder.append_detection()

    track_builder.add_xy_bbox(9, 1)
    track_builder.add_frame(9)
    track_builder.add_second(9)
    track_builder.append_detection()

    track_builder.add_xy_bbox(10, 1)
    track_builder.add_frame(10)
    track_builder.add_second(10)
    track_builder.append_detection()
    track = track_builder.build_track()
    merged_track = Mock()
    merged_track.detections = first_track.detections + track.detections
    merged_track.id = first_track.id
    return merged_track


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
    track_builder.add_track_id("not_intersecting_track")
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
def single_detection_track() -> Track:
    detection = Mock()
    detection.x = 1
    detection.y = 1
    detection.w = 1
    detection.h = 1
    track = Mock()
    track.id = TrackId("Single-Detection")
    track.detections = [detection]
    return track


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


@pytest.fixture
def area_section() -> Section:
    name = "area"
    coordinates = [
        Coordinate(1.5, 0.5),
        Coordinate(3, 0.5),
        Coordinate(3, 2),
        Coordinate(1.5, 2),
        Coordinate(1.5, 0.5),
    ]
    return Area(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def not_intersecting_area_section() -> Section:
    name = "not_intersecting_area"
    coordinates = [
        Coordinate(20, 20),
        Coordinate(30, 20),
        Coordinate(30, 30),
        Coordinate(20, 30),
        Coordinate(20, 20),
    ]
    return Area(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


def assert_track_geometry_dataset_equals(
    to_compare: TrackGeometryDataset, other: TrackGeometryDataset
) -> None:
    assert isinstance(to_compare, PygeosTrackGeometryDataset)
    assert isinstance(other, PygeosTrackGeometryDataset)
    assert to_compare._dataset.keys() == other._dataset.keys()  # noqa

    for offset, track_geom in to_compare._dataset.items():  # noqa
        assert track_geom.equals(other._dataset[offset])  # noqa


class TestPygeosTrackGeometryDataset:
    @pytest.fixture
    def simple_track(self) -> Track:
        first_detection = Mock()
        first_detection.x = 1
        first_detection.y = 0
        second_detection = Mock()
        second_detection.x = 2
        second_detection.y = 0
        simple_track = Mock()
        simple_track.id = TrackId("1")
        simple_track.detections = [first_detection, second_detection]
        return simple_track

    def test_from_track_dataset(self, simple_track: Track) -> None:
        track_dataset = create_track_dataset([simple_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        assert isinstance(geometry_dataset, PygeosTrackGeometryDataset)

        expected = create_geometry_dataset_from([simple_track])
        assert_track_geometry_dataset_equals(geometry_dataset, expected)

    def test_add_all_on_empty_dataset(
        self, first_track: Track, second_track: Track
    ) -> None:
        track_dataset = create_track_dataset([])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.add_all([first_track, second_track])
        expected = create_geometry_dataset_from([first_track, second_track])
        assert_track_geometry_dataset_equals(result, expected)

    def test_add_all_on_filled_dataset(
        self, first_track: Track, second_track: Track
    ) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.add_all([second_track])
        expected = create_geometry_dataset_from([first_track, second_track])
        assert_track_geometry_dataset_equals(result, expected)

    def test_add_all_merge_track(
        self, first_track: Track, first_track_merged: Track, second_track: Track
    ) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.add_all([first_track_merged])
        expected = create_geometry_dataset_from([first_track_merged, second_track])
        assert_track_geometry_dataset_equals(result, expected)

    def test_remove_from_filled_dataset(
        self, first_track: Track, second_track: Track
    ) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.remove([first_track.id])
        expected = create_geometry_dataset_from([second_track])
        assert_track_geometry_dataset_equals(result, expected)

    def test_remove_from_empty_dataset(self, first_track: Track) -> None:
        geometry_dataset = PygeosTrackGeometryDataset()
        result = geometry_dataset.remove([first_track.id])
        assert_track_geometry_dataset_equals(result, PygeosTrackGeometryDataset())

    def test_remove_missing(self, first_track: Track, second_track: Track) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.remove([second_track.id])
        expected = create_geometry_dataset_from([first_track])
        assert_track_geometry_dataset_equals(result, expected)

    def test_intersection_points(
        self,
        single_detection_track: Track,
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
        track_dataset = create_track_dataset(
            [single_detection_track, not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.intersection_points(sections, BASE_GEOMETRY)
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

    def test_intersecting_tracks(
        self,
        single_detection_track: Track,
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
        track_dataset = create_track_dataset(
            [single_detection_track, not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.intersecting_tracks(sections, BASE_GEOMETRY)
        assert result == {first_track.id, second_track.id}

    def test_as_dict(self, first_track: Track, second_track: Track) -> None:
        tracks = [first_track, second_track]
        track_dataset = create_track_dataset(tracks)
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        assert isinstance(geometry_dataset, PygeosTrackGeometryDataset)
        result = geometry_dataset.as_dict()
        expected = {
            BASE_GEOMETRY: create_geometry_dataset_from(tracks)
            ._dataset[BASE_GEOMETRY][COLUMNS]
            .to_dict(orient="index")
        }
        assert result == expected

    def test_get_base_geometry(self) -> None:
        base_geometry = Mock()
        geometry_dataset = PygeosTrackGeometryDataset({BASE_GEOMETRY: base_geometry})
        assert geometry_dataset._get_base_geometry() == base_geometry

    def test_empty_on_empty_dataset(self) -> None:
        geometry_dataset = PygeosTrackGeometryDataset()
        assert geometry_dataset.empty

    def test_empty_on_filled_dataset(self, first_track: Track) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        assert isinstance(geometry_dataset, PygeosTrackGeometryDataset)
        assert not geometry_dataset.empty

    def test_get_track_ids(self, first_track: Track) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        assert isinstance(geometry_dataset, PygeosTrackGeometryDataset)
        assert geometry_dataset.track_ids == {first_track.id.id}

    def test_contained_by_sections(
        self,
        first_track: Track,
        second_track: Track,
        not_intersecting_track: Track,
        area_section: Section,
        not_intersecting_area_section: Section,
    ) -> None:
        track_dataset = create_track_dataset(
            [not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.contained_by_sections(
            [not_intersecting_area_section, area_section], BASE_GEOMETRY
        )
        expected = {
            first_track.id: [
                (area_section.id, [False, True, False, False, False]),
            ],
            second_track.id: [
                (area_section.id, [False, True, False, False, False]),
            ],
        }
        assert result == expected


class TestProfiling:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    @pytest.fixture
    def tracks_15min(self, test_data_dir: Path) -> TrackDataset:
        ottrk = test_data_dir / "OTCamera19_FR20_2023-05-24_07-00-00.ottrk"
        ottrk_parser = OttrkParser(PandasDetectionParser(PandasByMaxConfidence()))
        parse_result = ottrk_parser.parse(ottrk)
        return parse_result.tracks

    @pytest.fixture
    def sections(self, test_data_dir: Path) -> Iterable[Section]:
        flow_file = test_data_dir / "OTCamera19_FR20_2023-05-24.otflow"
        flow_parser = OtFlowParser()
        sections, flows = flow_parser.parse(flow_file)
        return sections

    def test_profile(
        self,
        benchmark: BenchmarkFixture,
        tracks_15min: TrackDataset,
        sections: Iterable[Section],
    ) -> None:
        benchmark.pedantic(
            tracks_15min.intersecting_tracks,
            args=(sections,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )
