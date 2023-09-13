import random
from pathlib import Path
from time import perf_counter
from typing import Any

from pandas import DataFrame

from OTAnalytics.adapter_ui.default_values import TRACK_LENGTH_LIMIT
from OTAnalytics.application.datastore import Datastore, TrackToVideoRepository
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.section import Section, SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackId,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_parser.otvision_parser import (
    CachedVideoParser,
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PandasTrackProvider,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
    PullingProgressbarBuilder,
    PullingProgressbarPopupBuilder,
)
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader
from tests.OTAnalytics.plugin_intersect.intersect_provider import (
    IntersectProvider,
    OTAIntersect,
    PyGeosIntersect,
    PyGeosPandasIntersect,
    PyGeosSegmentIntersect,
)

INDENT = 0
ORACLE: dict[str, list[TrackId]] = dict()
SCENARIO: dict[str, int] = dict()

REPEAT = 2
SEED = 42


def validate(func: Any) -> Any:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global ORACLE, SCENARIO

        key = "all"
        if "sections" in kwargs:
            key = str([section.id for section in kwargs["sections"]])

        res: list = func(*args, **kwargs)

        if kwargs.get("record", False) and key not in ORACLE:
            ORACLE[key] = res
            SCENARIO[key] = max(SCENARIO.values(), default=0) + 1
            print(f"{INDENT*'  '}Recorded results for {SCENARIO[key]}")
        else:
            if key not in ORACLE:
                raise KeyError("No expected results were recorded for {key}")
            expected: list = ORACLE[key]
            assert len(res) == len(expected)
            assert all(r in expected for r in res)
            assert all(e in res for e in expected)
            print(f"{INDENT*'  '}Valid results for {SCENARIO[key]}!")

        return res

    return inner


def time(func: Any) -> Any:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global INDENT
        indent = INDENT * "  "
        print(indent + f"{func.__name__}[")
        INDENT += 1
        start = perf_counter()
        res = func(*args, **kwargs)
        end = perf_counter()

        print(f"{indent}] {func.__name__} took {end-start} s")
        INDENT -= 1
        return res

    return inner


def create_data_store() -> Datastore:
    track_repository = TrackRepository()
    section_repository = SectionRepository()
    flow_repository = FlowRepository()
    event_repository = EventRepository()
    track_to_video_repository = TrackToVideoRepository()
    video_repository = VideoRepository()

    flow_parser = OtFlowParser()
    event_list_parser = OtEventListParser()
    video_parser = CachedVideoParser(SimpleVideoParser(MoviepyVideoReader()))
    track_video_parser = OttrkVideoParser(video_parser)
    track_parser = OttrkParser(
        CalculateTrackClassificationByMaxConfidence(),
        track_repository,
        track_length_limit=TRACK_LENGTH_LIMIT,
    )
    config_parser = OtConfigParser(video_parser, flow_parser)

    progressbar = PullingProgressbarBuilder(PullingProgressbarPopupBuilder())

    return Datastore(
        track_repository,
        track_parser,
        section_repository,
        flow_parser,
        flow_repository,
        event_repository,
        event_list_parser,
        track_to_video_repository,
        video_repository,
        video_parser,
        track_video_parser,
        progressbar,
        config_parser,
    )


def load_data(skip_tracks: bool, size: str = "small") -> Datastore:
    small_path = Path(
        r"D:\ptm\OTAnalytics\tests\data\Testvideo_"
        + "Cars-Truck_FR20_2020-01-01_00-00-00.ottrk"
    )

    paths = dict(
        small=small_path,
        medium=Path(r"D:\ptm\data\Standard_SCUEHQ_FR30_2022-09-15_07-00-00.ottrk"),
        # large=Path(r"D:\ptm\data\Standard_SCUEHQ_FR30_2022-09-15_07-00-00.ottrk"),
    )
    path = paths.get(size, paths["small"])

    print("loading data")
    datastore = create_data_store()
    if not skip_tracks:
        datastore.load_track_file(path)
        print("finished loading tracks")

    datastore.load_otflow(Path(r"D:\ptm\data\flows.otflow"))
    print("finished loading sections/flows")

    return datastore


def tracks_as_dataframe(datastore: Datastore) -> DataFrame:
    track_provider = PandasTrackProvider(datastore, NoProgressbarBuilder())
    return track_provider.get_data()


# @time
# def tracks_to_segment_linestrings_bulk(tracks: list[Track]):
#    return pygeos.linestrings(
#        [
#            [(f.x, f.y), (s.x, s.y)]
#            for track in tracks
#            for f, s in zip(track.detections[:-1], track.detections[1:])
#        ]
#    )


@time
def test_load(datastore: Datastore, provider: IntersectProvider) -> None:
    provider.use_sections(datastore).use_tracks(datastore)


@validate
@time
def test_intersect_all(
    datastore: Datastore, provider: IntersectProvider, record: bool = False
) -> set[TrackId]:
    return provider.intersect(datastore.get_all_tracks(), datastore.get_all_sections())


@validate
@time
def test_intersect_section(
    datastore: Datastore,
    provider: IntersectProvider,
    sections: list[Section],
    record: bool = False,
) -> set[TrackId]:
    return provider.intersect(
        datastore.get_all_tracks(),
        sections,
    )


@time
def test_intersect_random_sections(
    datastore: Datastore,
    provider: IntersectProvider,
    n: int,
    seed: int,
    record: bool = False,
) -> None:
    global INDENT
    random.seed(seed)
    msg = ""
    for _ in range(n):
        sections = datastore.get_all_sections()
        k = random.randint(1, len(sections))
        msg += f"{k}, "
        selected = random.sample(sections, k)
        test_intersect_section(datastore, provider, sections=selected, record=record)
    print(f"{INDENT*'  '}Tested section counts: " + msg)


@time
def test_ota_shapely(datastore: Datastore) -> None:
    provider = OTAIntersect()

    test_load(datastore, provider)
    test_intersect_all(datastore, provider, record=True)
    test_intersect_random_sections(
        datastore, provider, n=REPEAT, seed=SEED, record=True
    )


@time
def test_pygeos(datastore: Datastore) -> None:
    provider = PyGeosIntersect(prepare=False)

    test_load(datastore, provider)
    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_segments(datastore: Datastore) -> None:
    provider = PyGeosSegmentIntersect(prepare=False)

    test_load(datastore, provider)
    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_prepare(datastore: Datastore) -> None:
    provider = PyGeosIntersect(prepare=True)

    test_load(datastore, provider)
    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_segments_prepare(datastore: Datastore) -> None:
    provider = PyGeosSegmentIntersect(prepare=True)

    test_load(datastore, provider)
    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_pandas(datastore: Datastore) -> None:
    provider = PyGeosPandasIntersect(prepare=True)

    test_load(datastore, provider)
    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_pandas_prepare(datastore: Datastore) -> None:
    provider = PyGeosPandasIntersect(prepare=True)

    test_load(datastore, provider)
    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


# apply each segment between detections as linestring
# apply whole track as linestring

# pygeos
# Geometry -> Linestring / multilinestring
# crosses -> boolean
# intersection
# shortest_line


if __name__ == "__main__":
    data = load_data(skip_tracks=False, size="medium")

    print()
    test_ota_shapely(data)
    print()
    test_pygeos(data)
    print()
    test_pygeos_prepare(data)
    print()
    test_pygeos_pandas(data)
    print()
    test_pygeos_pandas_prepare(data)
    print()
    test_pygeos_segments(data)
    print()
    test_pygeos_segments_prepare(data)
