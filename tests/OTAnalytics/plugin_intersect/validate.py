from time import perf_counter

from pyparsing import Any

from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.types import EventType
from tests.OTAnalytics.plugin_intersect.intersect_data import load_data
from tests.OTAnalytics.plugin_intersect.intersect_provider import (
    IntersectProvider,
    OTAIntersect,
    PyGeosIntersect,
    PyGeosPandasCollectionIntersect,
    PyGeosPandasIntersect,
    PyGeosSegmentIntersect,
)

INDENT = 0
ORACLE: dict[str, list[TrackId]] = dict()
SCENARIO: dict[str, int] = dict()
ERRORS = 0


def validate(func: Any) -> Any:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global ORACLE, SCENARIO, ERRORS

        key = "all"
        if "sections" in kwargs:
            key = str([section.id for section in kwargs["sections"]])

        res: list = func(*args, **kwargs)

        if kwargs.get("record", False) and key not in ORACLE:
            ORACLE[key] = res
            SCENARIO[key] = max(SCENARIO.values(), default=0) + 1
            print(
                f"{INDENT*'  '}Recorded results for {SCENARIO[key]}:"
                + f" intersected {len(res)}, hash {hash(tuple(res))}"
            )
        else:
            if key not in ORACLE:
                raise KeyError("No expected results were recorded for {key}")
            expected: list = ORACLE[key]
            try:
                assert len(res) == len(expected)
                assert all(r in expected for r in res)
                assert all(e in res for e in expected)
                print(f"{INDENT*'  '}Valid results for {SCENARIO[key]}!")

            except AssertionError:
                ERRORS += 1
                print(
                    f"{INDENT*'  '}INVALID!! results for {SCENARIO[key]}:"
                    + f" intersected {len(res)} (exp: {len(expected)}),"
                    + f"hash {hash(tuple(res))} (exp {hash(tuple(expected))})"
                )
                print(f"{INDENT*'  '}Key {key}")
                print(f"{INDENT*'  '}Result {res}")
                print(f"{INDENT*'  '}Expected {expected}")

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


def validate_provider(provider: IntersectProvider) -> None:
    data = load_data(skip_tracks=False, size="small")
    provider.use_tracks(data).use_sections(data)

    def validate_intersects(track_id: int, section_id: int, expected: bool) -> None:
        track = data._track_repository.get_for(TrackId(track_id))
        section = data.get_section_for(SectionId(str(section_id)))

        if track and section:
            tracks = [track]
            sections = [section]
            res = provider.intersect(tracks, sections)
            assert (track.id in res) == expected, (
                f"{track.id} in {res} should be {expected} "
                + f"when intersecting {sections}"
                + f"({sections[0].get_offset(EventType.SECTION_ENTER)})"
            )
        else:
            print(f"Could not find track {track_id} or section{section_id}")

    checks = {
        1: [False] * 6 + [True] + [False] * 4,
        2: [True] + [False] * 10,
        3: [True] + [False] * 10,
        4: [False, True] + [False] * 9,
    }

    for section in checks:
        for track, expected in zip(range(1, 12), checks[section]):
            validate_intersects(track, section, expected)


if __name__ == "__main__":
    validate_provider(OTAIntersect())

    validate_provider(PyGeosIntersect(prepare=False))
    validate_provider(PyGeosIntersect(prepare=True))

    validate_provider(PyGeosSegmentIntersect(prepare=False))
    validate_provider(PyGeosSegmentIntersect(prepare=True))

    validate_provider(PyGeosPandasIntersect(prepare=False))
    validate_provider(PyGeosPandasIntersect(prepare=True))

    validate_provider(PyGeosPandasCollectionIntersect(prepare=False))
    validate_provider(PyGeosPandasCollectionIntersect(prepare=True))
    pass
