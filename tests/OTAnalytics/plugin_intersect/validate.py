from time import perf_counter

from pyparsing import Any

from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.types import EventType
from tests.OTAnalytics.plugin_intersect.intersect_data import load_data
from tests.OTAnalytics.plugin_intersect.intersect_provider import (
    GeoPandasIntersect,
    GeoPandasIntersectSingle,
    GeoPandasSegmentIntersect,
    GeoPandasSegmentIntersectSingle,
    IntersectProvider,
    OTAIntersect,
    PyGeosIntersect,
    PyGeosIntersectSingle,
    PyGeosPandasCollectionIntersect,
    PyGeosPandasIntersect,
    PyGeosPandasIntersectSingle,
    PyGeosPandasSegmentsIntersect,
    PyGeosSegmentIntersect,
    PyGeosSegmentIntersectSingle,
    ShapelyIntersect,
    ShapelyIntersectSingle,
)

LOG = False
WARN = False

KEY = ""
TAG = ""
ORACLE: dict[str, list[TrackId]] = dict()
SCENARIOS: dict[str, int] = dict()
ERRORS = 0


def validate(func: Any) -> Any:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global ORACLE, SCENARIOS, ERRORS, LOG, KEY

        key = "all"
        KEY = "all"
        provider = kwargs.get("name", "unknown")

        if "sections" in kwargs:
            key = str([section.id for section in kwargs["sections"]])
            KEY = str(len(kwargs["sections"]))

        res: list = func(*args, **kwargs)

        if kwargs.get("record", False) and key not in ORACLE:
            ORACLE[key] = res
            SCENARIOS[key] = max(SCENARIOS.values(), default=0) + 1
            if LOG:
                print(
                    f"Recorded results for {provider} with {SCENARIOS[key]}:"
                    + f" intersected {len(res)}, hash {hash(tuple(res))}"
                )
        else:
            if key not in ORACLE:
                raise KeyError(f"No expected results were recorded for {key}")
            expected: list = ORACLE[key]
            try:
                assert len(res) == len(expected)
                assert all(r in expected for r in res)
                assert all(e in res for e in expected)
                if LOG:
                    print(f"Valid results for {SCENARIOS[key]}!")

            except AssertionError:
                ERRORS += 1
                if WARN:
                    print(
                        f"INVALID!! results for {provider} with {SCENARIOS[key]}:"
                        + f" intersected {len(res)} (exp: {len(expected)}),"
                        + f"hash {hash(tuple(res))} (exp {hash(tuple(expected))})"
                    )
                    print(f"Key {key}")
                    print(f"Result {res}")
                    print(f"Expected {expected}")

        KEY = ""
        return res

    return inner


def validate_events(func: Any) -> Any:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global ORACLE, SCENARIOS, ERRORS, LOG, KEY

        key = "all-events"
        KEY = "all-events"
        provider = kwargs.get("name", "unknown")

        if "sections" in kwargs:
            key = str([section.id for section in kwargs["sections"]])
            KEY = str(len(kwargs["sections"]))

        res: list = func(*args, **kwargs)

        if kwargs.get("record", False) and key not in ORACLE:
            ORACLE[key] = res
            SCENARIOS[key] = max(SCENARIOS.values(), default=0) + 1
            if LOG:
                print(
                    f"Recorded results for {provider} with events {SCENARIOS[key]}:"
                    + f" intersected {len(res)}, hash {hash(tuple(res))}"
                )
        else:
            if key not in ORACLE:
                raise KeyError(f"No expected results were recorded for {key}")
            expected: list = ORACLE[key]
            try:
                assert len(res) == len(expected)
                for x, y in res:
                    assert any(
                        abs(x - e[0]) < 0.01 and abs(y - e[1]) < 0.01 for e in expected
                    )
                for x, y in expected:
                    assert any(
                        abs(x - r[0]) < 0.01 and abs(y - r[1]) < 0.01 for r in res
                    )
                if LOG:
                    print(f"Valid results for {SCENARIOS[key]}!")

            except AssertionError:
                ERRORS += 1
                if WARN:
                    print(
                        f"INVALID!! results for {provider}"
                        + f"with events {SCENARIOS[key]}:"
                        + f" intersected {len(res)} (exp: {len(expected)}),"
                        + f"hash {hash(tuple(res))} (exp {hash(tuple(expected))})"
                    )
                    print(f"Key {key}")
                    print(f"Result {res}")
                    print(f"Expected {expected}")

        KEY = ""
        return res

    return inner


def time(func: Any) -> Any:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global KEY, TAG

        name = kwargs.get("name", "unknown")

        start = perf_counter()
        res = func(*args, **kwargs)
        end = perf_counter()

        print(f"{name};{TAG};{KEY};{func.__name__};{end-start}")
        return res

    return inner


def validate_provider(provider: IntersectProvider) -> None:
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

    def validate_events(
        track_id: int,
        section_id: int,
        expected: list[tuple[float, float]],
        by_track: bool,
    ) -> None:
        track = data._track_repository.get_for(TrackId(track_id))
        section = data.get_section_for(SectionId(str(section_id)))

        if track and section:
            tracks = [track]
            sections = [section]
            res = provider.events(tracks, sections, by_track=by_track)

            assert len(res) == len(expected), (
                f"Actual number of events {len(res)}"
                + f" does not match expected number of events {len(expected)}:"
                + f" {res} != {expected}"
            )

            for x, y in res:
                assert any(
                    abs(x - e[0]) < 0.01 and abs(y - e[1]) < 0.01 for e in expected
                ), f"Actual result {(x,y)} not in list of expected results {expected}!"

        else:
            print(f"Could not find track {track_id} or section{section_id}")

    checks = {
        1: [False] * 6 + [True] + [False] * 4,
        2: [True] + [False] * 10,
        3: [True] + [False] * 10,
        4: [False, True] + [False] * 9,
    }

    expected_events = {
        (7, 1): [(96.69334411621094, 104.02690887451172)],
        (1, 2): [(220.67544555664062, 134.31570434570312)],
        (1, 3): [(421.63275146484375, 120.36776733398438)],
        (2, 4): [
            (615.552490234375, 155.39981079101562),
            (648.2918701171875, 100.17164611816406),
        ],
    }
    for section in checks:
        for track, expected in zip(range(1, 12), checks[section]):
            validate_intersects(track, section, expected)

            events = expected_events.get((track, section), [])
            validate_events(track, section, events, by_track=True)
            validate_events(track, section, events, by_track=False)


if __name__ == "__main__":
    data = load_data(skip_tracks=False, size="small")

    validate_provider(OTAIntersect(data))
    validate_provider(ShapelyIntersectSingle(data))
    validate_provider(ShapelyIntersect(data))

    validate_provider(PyGeosIntersectSingle(data, prepare=False))
    validate_provider(PyGeosIntersectSingle(data, prepare=True))
    exit(1)

    # todo X pandas X segments

    validate_provider(PyGeosIntersect(data, prepare=False))
    validate_provider(PyGeosIntersect(data, prepare=True))

    validate_provider(PyGeosSegmentIntersect(data, prepare=False))
    validate_provider(PyGeosSegmentIntersect(data, prepare=True))
    validate_provider(PyGeosSegmentIntersectSingle(data, prepare=False))
    validate_provider(PyGeosSegmentIntersectSingle(data, prepare=True))

    validate_provider(PyGeosPandasIntersect(data, prepare=False))
    validate_provider(PyGeosPandasIntersect(data, prepare=True))
    validate_provider(PyGeosPandasIntersectSingle(data, prepare=False))
    validate_provider(PyGeosPandasIntersectSingle(data, prepare=True))

    validate_provider(PyGeosPandasSegmentsIntersect(data, prepare=False))
    validate_provider(PyGeosPandasSegmentsIntersect(data, prepare=True))

    # todo single

    validate_provider(PyGeosPandasCollectionIntersect(data, prepare=False))
    validate_provider(PyGeosPandasCollectionIntersect(data, prepare=True))
    # todo single

    validate_provider(GeoPandasIntersect(data))
    validate_provider(GeoPandasIntersectSingle(data))
    validate_provider(GeoPandasSegmentIntersect(data))
    validate_provider(GeoPandasSegmentIntersectSingle(data))

    pass
