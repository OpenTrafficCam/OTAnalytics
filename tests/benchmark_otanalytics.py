from pathlib import Path
from typing import Iterable, TypedDict

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.datastore import (
    FlowParser,
    TrackParser,
    TrackToVideoRepository,
)
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.application.use_cases.track_repository import (
    GetAllTracks,
    GetTracksWithoutSingleDetections,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    ByMaxConfidence,
    Track,
    TrackFileRepository,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_datastore.track_store import PandasByMaxConfidence
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_parser.otvision_parser import (
    OtFlowParser,
    OttrkParser,
    PythonDetectionParser,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from OTAnalytics.plugin_ui.main_application import ApplicationStarter

NUM_PROCESSES = 1


@pytest.fixture
def ottrk_file(test_data_dir: Path) -> Path:
    return Path(test_data_dir / "OTCamera19_FR20_2023-05-24_00-30-00.ottrk")


@pytest.fixture
def ottrk_file_2hours(test_data_dir: Path) -> Path:
    return Path(test_data_dir / "OTCamera19_FR20_2023-05-24_11-15-00.ottrk")


@pytest.fixture
def otflow_file(test_data_dir: Path) -> Path:
    return test_data_dir / Path("OTCamera19_FR20_2023-05-24.otflow")


@pytest.fixture
def track_repository() -> TrackRepository:
    return TrackRepository()


@pytest.fixture
def section_repository() -> SectionRepository:
    return SectionRepository()


@pytest.fixture
def video_repository() -> VideoRepository:
    return VideoRepository()


@pytest.fixture
def track_to_video_repository() -> TrackToVideoRepository:
    return TrackToVideoRepository()


@pytest.fixture
def flow_repository() -> FlowRepository:
    return FlowRepository()


@pytest.fixture
def event_repository() -> EventRepository:
    return EventRepository()


@pytest.fixture
def starter() -> ApplicationStarter:
    return ApplicationStarter()


@pytest.fixture
def get_sections_by_id(section_repository: SectionRepository) -> GetSectionsById:
    return GetSectionsById(section_repository)


@pytest.fixture
def get_all_tracks(track_repository: TrackRepository) -> GetAllTracks:
    return GetAllTracks(track_repository)


@pytest.fixture
def get_tracks_without_single_detections(
    track_repository: TrackRepository,
) -> GetTracksWithoutSingleDetections:
    return GetTracksWithoutSingleDetections(track_repository)


@pytest.fixture
def add_events(event_repository: EventRepository) -> AddEvents:
    return AddEvents(event_repository)


@pytest.fixture
def clear_events(event_repository: EventRepository) -> ClearAllEvents:
    return ClearAllEvents(event_repository)


@pytest.fixture
def create_events(
    starter: ApplicationStarter,
    section_repository: SectionRepository,
    clear_events: ClearAllEvents,
    get_tracks_without_single_detections: GetTracksWithoutSingleDetections,
    add_events: AddEvents,
) -> CreateEvents:
    return starter._create_use_case_create_events(
        section_repository,
        clear_events,
        get_tracks_without_single_detections,
        add_events,
        num_processes=NUM_PROCESSES,
    )


@pytest.fixture()
def track_file_repository() -> TrackFileRepository:
    return TrackFileRepository()


@pytest.fixture
def python_ottrk_parser(track_repository: TrackRepository) -> TrackParser:
    detection_parser = PythonDetectionParser(ByMaxConfidence(), track_repository)
    return OttrkParser(detection_parser)


@pytest.fixture
def pandas_ottrk_parser(track_repository: TrackRepository) -> TrackParser:
    calculator = PandasByMaxConfidence()
    detection_parser = PandasDetectionParser(calculator)
    return OttrkParser(detection_parser)


@pytest.fixture
def otflow_parser() -> FlowParser:
    return OtFlowParser()


@pytest.fixture
def tracks_intersecting_sections(
    starter: ApplicationStarter,
    track_repository: TrackRepository,
) -> TracksIntersectingSections:
    get_all_tracks = GetTracksWithoutSingleDetections(track_repository)
    return starter._create_tracks_intersecting_sections(
        get_all_tracks, ShapelyIntersector()
    )


class TrackCount(TypedDict):
    id: str
    det_count: int


def get_track_counts(tracks: Iterable[Track]) -> list[TrackCount]:
    counts: list[TrackCount] = []
    for track in tracks:
        # trackcount = TrackCount(id=track.id.id, det_count=len(track.detections))
        counts.append(
            {"id": track.id.id, "det_count": len(track.detections)},
        )
    return sorted(counts, key=lambda count: count["det_count"])


def filter_detection_count_ge(
    counts: list[TrackCount], thresh: int
) -> list[TrackCount]:
    return [count for count in counts if count["det_count"] >= thresh]


class TestProfile:
    def test_load_ottrks_with_python_parser(
        self,
        benchmark: BenchmarkFixture,
        python_ottrk_parser: TrackParser,
        ottrk_file: Path,
    ) -> None:
        benchmark.pedantic(python_ottrk_parser.parse, args=(ottrk_file,))

    def test_load_ottrks_with_pandas_parser(
        self,
        benchmark: BenchmarkFixture,
        pandas_ottrk_parser: TrackParser,
        ottrk_file: Path,
    ) -> None:
        benchmark.pedantic(pandas_ottrk_parser.parse, args=(ottrk_file,))

    def test_create_events(
        self,
        benchmark: BenchmarkFixture,
        create_events: CreateEvents,
        clear_events: ClearAllEvents,
        python_ottrk_parser: OttrkParser,
        otflow_parser: FlowParser,
        track_repository: TrackRepository,
        flow_repository: FlowRepository,
        section_repository: SectionRepository,
        ottrk_file: Path,
        otflow_file: Path,
    ) -> None:
        track_parse_result = python_ottrk_parser.parse(ottrk_file)
        track_repository.add_all(track_parse_result.tracks)
        sections, flows = otflow_parser.parse(otflow_file)
        section_repository.add_all(sections)
        flow_repository.add_all(flows)

        benchmark.pedantic(
            create_events, setup=clear_events, rounds=5, iterations=1, warmup_rounds=1
        )

    def test_tracks_intersecting_sections(
        self,
        benchmark: BenchmarkFixture,
        python_ottrk_parser: TrackParser,
        otflow_parser: FlowParser,
        track_repository: TrackRepository,
        tracks_intersecting_sections: TracksIntersectingSections,
        ottrk_file: Path,
        otflow_file: Path,
    ) -> None:
        track_parse_result = python_ottrk_parser.parse(ottrk_file)
        track_repository.add_all(track_parse_result.tracks)
        sections, _ = otflow_parser.parse(otflow_file)

        benchmark.pedantic(
            tracks_intersecting_sections,
            args=(sections,),
            rounds=2,
            iterations=4,
            warmup_rounds=1,
        )

    def test_load_ottrks_with_python_parser_2hour(
        self,
        benchmark: BenchmarkFixture,
        python_ottrk_parser: TrackParser,
        ottrk_file_2hours: Path,
    ) -> None:
        benchmark.pedantic(python_ottrk_parser.parse, args=(ottrk_file_2hours,))

    def test_load_ottrks_with_pandas_parser_2hour(
        self,
        benchmark: BenchmarkFixture,
        pandas_ottrk_parser: TrackParser,
        ottrk_file_2hours: Path,
    ) -> None:
        benchmark.pedantic(pandas_ottrk_parser.parse, args=(ottrk_file_2hours,))

    def test_create_events_2hour(
        self,
        benchmark: BenchmarkFixture,
        create_events: CreateEvents,
        clear_events: ClearAllEvents,
        python_ottrk_parser: OttrkParser,
        otflow_parser: FlowParser,
        track_repository: TrackRepository,
        flow_repository: FlowRepository,
        section_repository: SectionRepository,
        ottrk_file_2hours: Path,
        otflow_file: Path,
    ) -> None:
        track_parse_result = python_ottrk_parser.parse(ottrk_file_2hours)
        track_repository.add_all(track_parse_result.tracks)
        sections, flows = otflow_parser.parse(otflow_file)
        section_repository.add_all(sections)
        flow_repository.add_all(flows)

        benchmark.pedantic(
            create_events, setup=clear_events, rounds=5, iterations=1, warmup_rounds=1
        )

    def test_tracks_intersecting_sections_2hour(
        self,
        benchmark: BenchmarkFixture,
        python_ottrk_parser: TrackParser,
        otflow_parser: FlowParser,
        track_repository: TrackRepository,
        tracks_intersecting_sections: TracksIntersectingSections,
        ottrk_file_2hours: Path,
        otflow_file: Path,
    ) -> None:
        track_parse_result = python_ottrk_parser.parse(ottrk_file_2hours)
        track_repository.add_all(track_parse_result.tracks)
        sections, _ = otflow_parser.parse(otflow_file)

        benchmark.pedantic(
            tracks_intersecting_sections,
            args=(sections,),
            rounds=2,
            iterations=4,
            warmup_rounds=1,
        )
