from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    ExportCounts,
)
from OTAnalytics.application.config import (
    CLI_CUTTING_SECTION_MARKER,
    CUTTING_SECTION_MARKER,
)
from OTAnalytics.application.datastore import DetectionMetadata, TrackParser
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.parser.cli_parser import CliMode
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.event_repository import ClearAllEvents
from OTAnalytics.application.use_cases.section_repository import (
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTracks,
    GetTracksWithoutSingleDetections,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.section import (
    LineSection,
    Section,
    SectionId,
    SectionRepository,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
)
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_cli.cli_application import OtAnalyticsCliApplicationStarter
from OTAnalytics.plugin_datastore.polars_track_store import PolarsTrackDataset
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTracksIntersectingSection,
)
from OTAnalytics.plugin_parser.feathers_parser import FeathersParser
from OTAnalytics.plugin_parser.otvision_parser import OtFlowParser
from tests.utils.builders.run_configuration import create_run_config

EXCLUDE_FILTER = [
    OtcClasses.PEDESTRIAN,
    OtcClasses.BICYCLIST,
    OtcClasses.BICYCLIST_WITH_TRAILER,
    OtcClasses.CARGO_BIKE_DRIVER,
    OtcClasses.SCOOTER_DRIVER,
    OtcClasses.OTHER,
]


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


class UseCaseProvider:
    GEOMETRY_FACTORY: TRACK_GEOMETRY_FACTORY = (
        ShapelyTrackGeometryDataset.from_track_dataset
    )

    @property
    def run_config(self) -> RunConfiguration:
        return create_run_config(
            flow_parser=self._flow_parser,
            start_cli=True,
            cli_mode=CliMode.BULK,
            debug=False,
            logfile_overwrite=True,
            track_export=False,
            track_files=[str(f) for f in self._ottrk_files],
            otflow_file=str(self._otflow_file),
            save_dir=self._save_dir,
            event_formats=["otevents"],
            include_classes=list(self._include_classes),
            exclude_classes=list(self._exclude_classes),
        )

    @property
    def sections(self) -> list[Section]:
        return self._section_repository.get_all()

    def __init__(
        self,
        otflow_file: Path,
        ottrk_files: list[Path],
        save_dir: str,
    ) -> None:
        self._otflow_file = otflow_file
        self._ottrk_files = ottrk_files
        self._save_dir = save_dir
        self._include_classes: frozenset[str] = frozenset()
        self._exclude_classes: frozenset[str] = frozenset()
        self._flow_parser = OtFlowParser()
        self._starter = OtAnalyticsCliApplicationStarter(self.run_config)
        track_repository, detection_metadata = self.provide_track_repository(
            self._ottrk_files
        )
        self._track_repository = track_repository
        self._detection_metadata = detection_metadata
        self._section_repository = SectionRepository()
        self._flow_repository = FlowRepository()
        self._event_repository = EventRepository()

        self._parse_otflow(self._otflow_file)

    def _parse_otflow(self, otflow_file: Path) -> None:
        sections, flows = self._flow_parser.parse(otflow_file)
        self._section_repository.add_all(sections)
        self._flow_repository.add_all(flows)

    def get_tracks_intersecting_sections(self) -> TracksIntersectingSections:
        return self._starter.tracks_intersecting_sections

    def get_create_events(self) -> CreateEvents:
        clear_all_events = ClearAllEvents(self._event_repository)
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            self._track_repository
        )
        create_events = self._starter._create_use_case_create_events(
            self._section_repository.get_all,
            clear_all_events,
            get_tracks_without_single_detections,
        )
        return create_events

    def get_export_counts(self) -> ExportCounts:
        return self._starter.export_counts

    def get_cut_tracks(self) -> CutTracksIntersectingSection:
        get_sections_by_id = GetSectionsById(self._section_repository)
        get_tracks = GetAllTracks(self._track_repository)
        clear_all_tracks = ClearAllTracks(self._track_repository)
        add_all_tracks = AddAllTracks(self._track_repository)
        remove_section = RemoveSection(self._section_repository)
        return SimpleCutTracksIntersectingSection(
            get_sections_by_id,
            get_tracks,
            clear_all_tracks,
            add_all_tracks,
            remove_section,
        )

    def add_filters(
        self,
        include_classes: list[str] | list[OtcClasses],
        exclude_classes: list[str] | list[OtcClasses],
    ) -> None:
        self._include_classes = frozenset(include_classes)
        self._exclude_classes = frozenset(exclude_classes)

    def provide_track_repository(
        self, track_files: list[Path]
    ) -> tuple[TrackRepository, DetectionMetadata]:
        parser: TrackParser
        repository = TrackRepository(self.provide_polars_track_dataset())
        parser = FeathersParser(PolarsTrackGeometryDataset.from_track_dataset)
        detection_metadata = _fill_track_repository(parser, repository, track_files)
        return repository, detection_metadata

    def provide_polars_track_dataset(self) -> TrackDataset:
        return PolarsTrackDataset.from_list(
            [], PolarsTrackGeometryDataset.from_track_dataset
        )

    def counting_specification(self, save_dir: Path) -> CountingSpecificationDto:
        return CountingSpecificationDto(
            start=datetime(
                year=2023,
                month=5,
                day=24,
                hour=8,
                minute=0,
                second=0,
                tzinfo=timezone.utc,
            ),
            end=datetime(
                year=2023,
                month=5,
                day=24,
                hour=8,
                minute=15,
                second=0,
                tzinfo=timezone.utc,
            ),
            interval_in_minutes=15,
            modes=list(self._detection_metadata.detection_classes),
            output_file=f"{save_dir / self._otflow_file.with_suffix('.csv').name}",
            output_format="CSV",
            export_mode=OVERWRITE,
        )

    def run_cli(self) -> Callable[[], None]:
        return self._starter.start

    def get_track_parser(self) -> TrackParser:
        return FeathersParser()


def retrieve_cutting_sections(sections: Iterable[Section]) -> list[Section]:
    cutting_sections = []
    for section in sections:
        if section.name.startswith(CUTTING_SECTION_MARKER) or section.name.startswith(
            CLI_CUTTING_SECTION_MARKER
        ):
            cutting_sections.append(section)
    return cutting_sections


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
def cutting_section() -> Section:
    coords = [Coordinate(589, 674), Coordinate(883, 290)]

    return LineSection(
        SectionId("#cut"),
        "#cut",
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.5, 0.5)},
        {},
        coords,
    )


@pytest.fixture
def feathers_track_parser() -> TrackParser:
    return FeathersParser()


@pytest.fixture
def use_case_provider_15min(
    otflow_file: Path, track_file_15min: Path, test_data_tmp_dir: Path
) -> UseCaseProvider:
    return UseCaseProvider(otflow_file, [track_file_15min], str(test_data_tmp_dir))


@pytest.fixture
def use_case_provider_2hours(
    otflow_file: Path, track_files_2hours: list[Path], test_data_tmp_dir: Path
) -> UseCaseProvider:
    return UseCaseProvider(otflow_file, track_files_2hours, str(test_data_tmp_dir))


@pytest.fixture
def use_case_provider_15min_filtered(
    otflow_file: Path, track_file_15min: Path, test_data_tmp_dir: Path
) -> UseCaseProvider:
    use_case_provider = UseCaseProvider(
        otflow_file, [track_file_15min], str(test_data_tmp_dir)
    )
    use_case_provider.add_filters([], EXCLUDE_FILTER)
    return use_case_provider


@pytest.fixture
def use_case_provider_2hours_filtered(
    otflow_file: Path, track_files_2hours: list[Path], test_data_tmp_dir: Path
) -> UseCaseProvider:
    use_case_provider = UseCaseProvider(
        otflow_file, track_files_2hours, str(test_data_tmp_dir)
    )
    use_case_provider.add_filters([], EXCLUDE_FILTER)
    return use_case_provider


@pytest.fixture
def use_case_provider_empty(
    otflow_file: Path, test_data_tmp_dir: Path
) -> UseCaseProvider:
    use_case_provider = UseCaseProvider(otflow_file, [], str(test_data_tmp_dir))
    use_case_provider.add_filters([], EXCLUDE_FILTER)
    return use_case_provider


@pytest.fixture
def use_case_provider_empty_filtered(
    otflow_file: Path, test_data_tmp_dir: Path
) -> UseCaseProvider:
    use_case_provider = UseCaseProvider(otflow_file, [], str(test_data_tmp_dir))
    use_case_provider.add_filters([], EXCLUDE_FILTER)
    return use_case_provider


class TestBenchmarkTrackParser:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_load_15min(
        self,
        benchmark: BenchmarkFixture,
        feathers_track_parser: TrackParser,
        track_file_15min: Path,
    ) -> None:
        benchmark.pedantic(
            feathers_track_parser.parse,
            args=(track_file_15min,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestBenchmarkTracksIntersectingSections:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self, benchmark: BenchmarkFixture, use_case_provider_15min: UseCaseProvider
    ) -> None:
        use_case = use_case_provider_15min.get_tracks_intersecting_sections()
        benchmark.pedantic(
            use_case,
            args=(use_case_provider_15min.sections,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours(
        self, benchmark: BenchmarkFixture, use_case_provider_2hours: UseCaseProvider
    ) -> None:
        use_case = use_case_provider_2hours.get_tracks_intersecting_sections()
        benchmark.pedantic(
            use_case,
            args=(use_case_provider_2hours.sections,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_15min_filtered(
        self,
        benchmark: BenchmarkFixture,
        use_case_provider_15min_filtered: UseCaseProvider,
    ) -> None:
        use_case = use_case_provider_15min_filtered.get_tracks_intersecting_sections()
        benchmark.pedantic(
            use_case,
            args=(use_case_provider_15min_filtered.sections,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestBenchmarkCreateEvents:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self, benchmark: BenchmarkFixture, use_case_provider_15min: UseCaseProvider
    ) -> None:
        use_case = use_case_provider_15min.get_create_events()
        benchmark.pedantic(
            use_case,
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_15min_filtered(
        self,
        benchmark: BenchmarkFixture,
        use_case_provider_15min_filtered: UseCaseProvider,
    ) -> None:
        use_case = use_case_provider_15min_filtered.get_create_events()
        benchmark.pedantic(
            use_case,
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
        test_data_tmp_dir: Path,
        use_case_provider_15min: UseCaseProvider,
    ) -> None:
        use_case = use_case_provider_15min.get_export_counts()
        specification = use_case_provider_15min.counting_specification(
            test_data_tmp_dir
        )
        benchmark.pedantic(
            use_case.export,
            args=(specification,),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_15min_filtered(
        self,
        benchmark: BenchmarkFixture,
        test_data_tmp_dir: Path,
        use_case_provider_15min_filtered: UseCaseProvider,
    ) -> None:
        use_case = use_case_provider_15min_filtered.get_export_counts()
        specification = use_case_provider_15min_filtered.counting_specification(
            test_data_tmp_dir
        )
        benchmark.pedantic(
            use_case.export,
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
        use_case_provider_15min: UseCaseProvider,
        cutting_section: Section,
    ) -> None:
        # TODO: Replace current cutting section from the one in the test dataset
        use_case = use_case_provider_15min.get_cut_tracks()
        benchmark.pedantic(
            use_case,
            args=(cutting_section, True),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_15min_filtered(
        self,
        benchmark: BenchmarkFixture,
        use_case_provider_15min_filtered: UseCaseProvider,
        cutting_section: Section,
    ) -> None:
        # TODO: Replace current cutting section from the one in the test dataset
        use_case = use_case_provider_15min_filtered.get_cut_tracks()
        benchmark.pedantic(
            use_case,
            args=(cutting_section, True),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )


class TestPipelineBenchmark:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    def test_15min(
        self, benchmark: BenchmarkFixture, use_case_provider_15min: UseCaseProvider
    ) -> None:
        use_case = use_case_provider_15min.run_cli()
        benchmark.pedantic(
            use_case,
            args=(),
            rounds=self.ROUNDS,
            iterations=5,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_15min_filtered(
        self,
        benchmark: BenchmarkFixture,
        use_case_provider_15min_filtered: UseCaseProvider,
    ) -> None:
        use_case = use_case_provider_15min_filtered.run_cli()
        benchmark.pedantic(
            use_case,
            args=(),
            rounds=self.ROUNDS,
            iterations=5,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours(
        self, benchmark: BenchmarkFixture, use_case_provider_2hours: UseCaseProvider
    ) -> None:
        use_case = use_case_provider_2hours.run_cli()
        benchmark.pedantic(
            use_case,
            args=(),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )

    def test_2hours_filtered(
        self,
        benchmark: BenchmarkFixture,
        use_case_provider_2hours_filtered: UseCaseProvider,
    ) -> None:
        use_case = use_case_provider_2hours_filtered.run_cli()
        benchmark.pedantic(
            use_case,
            args=(),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )
