from datetime import datetime
from pathlib import Path

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    ExportCounts,
)
from OTAnalytics.application.datastore import DetectionMetadata, FlowParser, TrackParser
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.section_repository import (
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    GetAllTracks,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    LineSection,
    Section,
    SectionId,
    SectionRepository,
)
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    FilteredPandasTrackDataset,
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTracksIntersectingSection,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    OtFlowParser,
    OttrkParser,
    PythonDetectionParser,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from OTAnalytics.plugin_ui.main_application import ApplicationStarter

NUM_PROCESSES = 1


def _fill_track_repository(
    track_parser: TrackParser,
    track_repository: TrackRepository,
    track_files: list[Path],
) -> DetectionMetadata:
    detection_classes: set[str] = set()
    for track_file in track_files:
        track_parse_result = track_parser.parse(track_file)
        track_repository.add_all(track_parse_result.tracks)
        detection_classes.update(
            track_parse_result.detection_metadata.detection_classes
        )
    return DetectionMetadata(frozenset(detection_classes))


def _parse_otflow(
    flow_parser: FlowParser,
    section_repository: SectionRepository,
    flow_repository: FlowRepository,
    otflow: Path,
) -> None:
    sections, flows = flow_parser.parse(otflow)
    section_repository.add_all(sections)
    flow_repository.add_all(flows)


def _build_tracks_intersecting_sections(
    track_repository: TrackRepository,
) -> TracksIntersectingSections:
    starter = ApplicationStarter()
    get_all_tracks = GetAllTracks(track_repository)
    return starter._create_tracks_intersecting_sections(get_all_tracks)


def _build_create_events(
    track_repository: TrackRepository,
    section_repository: SectionRepository,
    event_repository: EventRepository,
) -> CreateEvents:
    starter = ApplicationStarter()
    clear_all_events = ClearAllEvents(event_repository)
    get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
        track_repository
    )
    get_tracks = GetAllTracks(track_repository)
    add_events = AddEvents(event_repository)
    create_events = starter._create_use_case_create_events(
        section_repository.get_all,
        clear_all_events,
        get_tracks,
        get_tracks_without_single_detections,
        add_events,
        num_processes=NUM_PROCESSES,
    )
    return create_events


def _build_export_events(
    track_repository: TrackRepository,
    section_repository: SectionRepository,
    flow_repository: FlowRepository,
    event_repository: EventRepository,
) -> ExportCounts:
    starter = ApplicationStarter()
    create_events = _build_create_events(
        track_repository, section_repository, event_repository
    )

    return starter._create_export_counts(
        event_repository,
        flow_repository,
        track_repository,
        GetSectionsById(section_repository),
        create_events,
    )


def _build_cut_tracks_intersecting_sections(
    section_repository: SectionRepository,
    track_repository: TrackRepository,
) -> CutTracksIntersectingSection:
    get_sections_by_id = GetSectionsById(section_repository)
    get_tracks = GetAllTracks(track_repository)
    add_all_tracks = AddAllTracks(track_repository)
    remove_tracks = RemoveTracks(track_repository)
    remove_section = RemoveSection(section_repository)
    return SimpleCutTracksIntersectingSection(
        get_sections_by_id,
        get_tracks,
        add_all_tracks,
        remove_tracks,
        remove_section,
    )


@pytest.fixture(scope="module")
def track_file_15min(test_data_dir: Path) -> Path:
    return Path(test_data_dir / "OTCamera19_FR20_2023-05-24_08-00-00.ottrk")


@pytest.fixture(scope="module")
def track_files_2hours(test_data_dir: Path) -> list[Path]:
    return [
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_08-00-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_08-15-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_08-30-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_08-45-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_09-00-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_09-15-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_09-30-00.ottrk"),
        Path(test_data_dir / "OTCamera19_FR20_2023-05-24_09-45-00.ottrk"),
    ]


@pytest.fixture(scope="module")
def otflow_file(test_data_dir: Path) -> Path:
    return test_data_dir / Path("OTCamera19_FR20_2023-05-24.otflow")


@pytest.fixture
def python_track_repository() -> TrackRepository:
    return TrackRepository(PythonTrackDataset())


@pytest.fixture
def pandas_track_repository() -> TrackRepository:
    return TrackRepository(
        PandasTrackDataset(PygeosTrackGeometryDataset.from_track_dataset)
    )


@pytest.fixture
def section_repository() -> SectionRepository:
    return SectionRepository()


@pytest.fixture
def flow_repository() -> FlowRepository:
    return FlowRepository()


@pytest.fixture
def event_repository() -> EventRepository:
    return EventRepository()


@pytest.fixture
def clear_events(event_repository: EventRepository) -> ClearAllEvents:
    return ClearAllEvents(event_repository)


@pytest.fixture
def python_track_parser(python_track_repository: TrackRepository) -> TrackParser:
    detection_parser = PythonDetectionParser(ByMaxConfidence(), python_track_repository)
    return OttrkParser(detection_parser)


@pytest.fixture
def pandas_track_parser() -> TrackParser:
    calculator = PandasByMaxConfidence()
    detection_parser = PandasDetectionParser(
        calculator, PygeosTrackGeometryDataset.from_track_dataset
    )
    return OttrkParser(detection_parser)


@pytest.fixture(scope="function")
def python_track_repo_15min(
    track_file_15min: Path,
) -> tuple[TrackRepository, DetectionMetadata]:
    track_repository = TrackRepository(PythonTrackDataset())
    track_parser = OttrkParser(
        PythonDetectionParser(ByMaxConfidence(), track_repository)
    )
    detection_metadata = _fill_track_repository(
        track_parser, track_repository, [track_file_15min]
    )
    return track_repository, detection_metadata


@pytest.fixture(scope="function")
def python_track_repo_2hours(
    track_files_2hours: list[Path],
) -> tuple[TrackRepository, DetectionMetadata]:
    track_repository = TrackRepository(PythonTrackDataset())
    track_parser = OttrkParser(
        PythonDetectionParser(ByMaxConfidence(), track_repository)
    )
    detection_metadata = _fill_track_repository(
        track_parser, track_repository, track_files_2hours
    )
    return track_repository, detection_metadata


@pytest.fixture(scope="function")
def pandas_track_repo_15min(
    track_file_15min: Path,
) -> tuple[TrackRepository, DetectionMetadata]:
    track_repository = TrackRepository(
        PandasTrackDataset(PygeosTrackGeometryDataset.from_track_dataset)
    )
    track_parser = OttrkParser(
        PandasDetectionParser(
            PandasByMaxConfidence(), PygeosTrackGeometryDataset.from_track_dataset
        )
    )
    detection_metadata = _fill_track_repository(
        track_parser, track_repository, [track_file_15min]
    )
    return track_repository, detection_metadata


@pytest.fixture(scope="function")
def pandas_track_repo_2hours(
    track_files_2hours: list[Path],
) -> tuple[TrackRepository, DetectionMetadata]:
    track_repository = TrackRepository(
        FilteredPandasTrackDataset(
            PandasTrackDataset(PygeosTrackGeometryDataset.from_track_dataset),
            frozenset(["pedestrian"]),
            frozenset(),
        )
    )
    track_parser = OttrkParser(
        PandasDetectionParser(
            PandasByMaxConfidence(), PygeosTrackGeometryDataset.from_track_dataset
        )
    )
    detection_metadata = _fill_track_repository(
        track_parser, track_repository, track_files_2hours
    )
    return track_repository, detection_metadata


@pytest.fixture
def section_flow_repo_setup(
    section_repository: SectionRepository,
    flow_repository: FlowRepository,
    otflow_file: Path,
) -> tuple[SectionRepository, FlowRepository]:
    _parse_otflow(OtFlowParser(), section_repository, flow_repository, otflow_file)
    return section_repository, flow_repository


@pytest.fixture
def cutting_section() -> Section:
    coords = [Coordinate(589, 674), Coordinate(883, 290)]

    return LineSection(
        SectionId("#cut"),
        "#cut",
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.5, 0.5)},
        {},
        coords,
    )


class TestBenchmarkTrackParser:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_load_15min(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_parser: TrackParser,
        track_file_15min: Path,
    ) -> None:
        benchmark.pedantic(
            pandas_track_parser.parse,
            args=(track_file_15min,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_load_2hours(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_parser: TrackParser,
        track_files_2hours: list[Path],
    ) -> None:
        def _parse_2hours(parser: TrackParser, ottrk_files: list[Path]) -> None:
            for ottrk_file in ottrk_files:
                parser.parse(ottrk_file)

        benchmark.pedantic(
            _parse_2hours,
            args=(
                pandas_track_parser,
                track_files_2hours,
            ),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestBenchmarkTracksIntersectingSections:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_15min: tuple[TrackRepository, DetectionMetadata],
        section_flow_repo_setup: tuple[SectionRepository, FlowRepository],
    ) -> None:
        track_repository, _ = pandas_track_repo_15min
        section_repository, flow_repository = section_flow_repo_setup
        use_case = _build_tracks_intersecting_sections(track_repository)

        benchmark.pedantic(
            use_case,
            args=(section_repository.get_all(),),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_2hours: tuple[TrackRepository, DetectionMetadata],
        section_flow_repo_setup: tuple[SectionRepository, FlowRepository],
    ) -> None:
        track_repository, _ = pandas_track_repo_2hours
        section_repository, flow_repository = section_flow_repo_setup
        use_case = _build_tracks_intersecting_sections(track_repository)
        benchmark.pedantic(
            use_case,
            args=(section_repository.get_all(),),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestBenchmarkCreateEvents:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_15min: tuple[TrackRepository, DetectionMetadata],
        section_flow_repo_setup: tuple[SectionRepository, FlowRepository],
        event_repository: EventRepository,
        clear_events: ClearAllEvents,
    ) -> None:
        track_repository, _ = pandas_track_repo_15min
        section_repository, flow_repository = section_flow_repo_setup
        create_events = _build_create_events(
            track_repository, section_repository, event_repository
        )
        benchmark.pedantic(
            create_events,
            setup=clear_events,
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_2hours: tuple[TrackRepository, DetectionMetadata],
        section_flow_repo_setup: tuple[SectionRepository, FlowRepository],
        event_repository: EventRepository,
        clear_events: ClearAllEvents,
    ) -> None:
        track_repository, _ = pandas_track_repo_2hours
        section_repository, flow_repository = section_flow_repo_setup
        create_events = _build_create_events(
            track_repository, section_repository, event_repository
        )
        benchmark.pedantic(
            create_events,
            setup=clear_events,
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestBenchmarkExportCounting:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_15min: tuple[TrackRepository, DetectionMetadata],
        section_flow_repo_setup: tuple[SectionRepository, FlowRepository],
        event_repository: EventRepository,
        test_data_tmp_dir: Path,
        otflow_file: Path,
    ) -> None:
        track_repository, detection_metadata = pandas_track_repo_15min
        section_repository, flow_repository = section_flow_repo_setup
        export_events = _build_export_events(
            track_repository,
            section_repository,
            flow_repository,
            event_repository,
        )
        specification = CountingSpecificationDto(
            start=datetime(2023, 5, 24, 8, 0, 0),
            end=datetime(2023, 5, 24, 8, 15, 0),
            interval_in_minutes=15,
            modes=list(detection_metadata.detection_classes),
            output_file=f"{test_data_tmp_dir / otflow_file.with_suffix('.csv').name}",
            output_format="CSV",
        )
        benchmark.pedantic(
            export_events.export,
            args=(specification,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_2hours: tuple[TrackRepository, DetectionMetadata],
        section_flow_repo_setup: tuple[SectionRepository, FlowRepository],
        event_repository: EventRepository,
        test_data_tmp_dir: Path,
        otflow_file: Path,
    ) -> None:
        track_repository, detection_metadata = pandas_track_repo_2hours
        section_repository, flow_repository = section_flow_repo_setup
        export_events = _build_export_events(
            track_repository,
            section_repository,
            flow_repository,
            event_repository,
        )
        specification = CountingSpecificationDto(
            start=datetime(2023, 5, 24, 8, 0, 0),
            end=datetime(2023, 5, 24, 8, 15, 0),
            interval_in_minutes=15,
            modes=list(detection_metadata.detection_classes),
            output_file=f"{test_data_tmp_dir / otflow_file.with_suffix('.csv').name}",
            output_format="CSV",
        )
        benchmark.pedantic(
            export_events.export,
            args=(specification,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestBenchmarkCuttingSection:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_15min: tuple[TrackRepository, DetectionMetadata],
        cutting_section: Section,
    ) -> None:
        track_repository, _ = pandas_track_repo_15min
        section_repository = SectionRepository()
        section_repository.add(cutting_section)
        cut_tracks_intersecting_section = _build_cut_tracks_intersecting_sections(
            section_repository, track_repository
        )
        benchmark.pedantic(
            cut_tracks_intersecting_section,
            args=(cutting_section,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours(
        self,
        benchmark: BenchmarkFixture,
        pandas_track_repo_2hours: tuple[TrackRepository, DetectionMetadata],
        cutting_section: Section,
    ) -> None:
        track_repository, _ = pandas_track_repo_2hours
        section_repository = SectionRepository()
        section_repository.add(cutting_section)
        cut_tracks_intersecting_section = _build_cut_tracks_intersecting_sections(
            section_repository, track_repository
        )
        benchmark.pedantic(
            cut_tracks_intersecting_section,
            args=(cutting_section,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )
