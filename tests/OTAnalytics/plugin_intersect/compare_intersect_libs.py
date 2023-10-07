import random

from pyparsing import Any

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import TrackId
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
from tests.OTAnalytics.plugin_intersect.validate import (
    ERRORS,
    time,
    validate,
    validate_events,
)

REPEAT = 10
SEED = 42
TEST_INTERSECT = False
TEST_EVENTS = True


@validate
@time
def test_intersect_all(
    datastore: Datastore, name: str, provider: IntersectProvider, record: bool = False
) -> set[TrackId]:
    return provider.intersect(datastore.get_all_tracks(), datastore.get_all_sections())


@validate_events
@time
def test_events_all(
    datastore: Datastore, name: str, provider: IntersectProvider, record: bool = False
) -> list[tuple[float, float]]:
    return provider.events(datastore.get_all_tracks(), datastore.get_all_sections())


@validate
@time
def test_intersect_section(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    sections: list[Section],
    record: bool = False,
) -> set[TrackId]:
    return provider.intersect(
        datastore.get_all_tracks(),
        sections,
    )


@validate_events
@time
def test_events_section(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    sections: list[Section],
    record: bool = False,
) -> list[tuple[float, float]]:
    return provider.events(
        datastore.get_all_tracks(),
        sections,
    )


@time
def test_intersect_random_sections(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    n: int,
    seed: int,
    record: bool = False,
) -> None:
    random.seed(seed)
    msg = ""
    for _ in range(n):
        sections = datastore.get_all_sections()
        k = random.randint(1, len(sections))
        msg += f"{k}, "
        selected = random.sample(sections, k)
        test_intersect_section(
            datastore, name=name, provider=provider, sections=selected, record=record
        )


@time
def test_events_random_sections(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    n: int,
    seed: int,
    record: bool = False,
) -> None:
    random.seed(seed)
    msg = ""
    for _ in range(n):
        sections = datastore.get_all_sections()
        k = random.randint(1, len(sections))
        msg += f"{k}, "
        selected = random.sample(sections, k)
        test_events_section(
            datastore, name=name, provider=provider, sections=selected, record=record
        )


@time
def test_init(
    cons: type[IntersectProvider],
    datastore: Datastore,
    name: str,
    *args: Any,
    **kwargs: Any,
) -> IntersectProvider:
    return cons(datastore, *args, **kwargs)


@time
def run_test(
    datastore: Datastore,
    cons: type[IntersectProvider],
    name: str,
    record: bool = False,
    *args: Any,
    **kwargs: Any,
) -> None:
    provider = test_init(cons, datastore, name=name, *args, **kwargs)

    if TEST_INTERSECT:
        test_intersect_all(datastore, name=name, provider=provider, record=record)
        test_intersect_random_sections(
            datastore, name=name, provider=provider, n=REPEAT, seed=SEED, record=record
        )

    if TEST_EVENTS:
        test_events_all(datastore, name=name, provider=provider, record=record)
        test_events_random_sections(
            datastore, name=name, provider=provider, n=REPEAT, seed=SEED, record=record
        )


def test_comlpete(
    datastore: Datastore,
    cons: type[IntersectProvider],
    record: bool = False,
    *args: Any,
    **kwargs: Any,
) -> None:
    run_test(datastore, cons, name=cons.__name__, record=record, *args, **kwargs)


if __name__ == "__main__":
    import tests.OTAnalytics.plugin_intersect.validate as val

    data = load_data(skip_tracks=False, size="medium")

    val.TAG = ""
    test_comlpete(data, OTAIntersect, record=True)
    test_comlpete(data, ShapelyIntersect, record=True)
    test_comlpete(data, ShapelyIntersectSingle)

    # PYGEOS
    val.TAG = "UNPREPARED"
    test_comlpete(data, PyGeosIntersectSingle, prepare=False)

    exit()
    val.TAG = ""
    test_comlpete(data, OTAIntersect, record=True)
    test_comlpete(data, ShapelyIntersect, record=True)
    test_comlpete(data, ShapelyIntersectSingle)

    # GEOPANDAS
    test_comlpete(data, GeoPandasIntersectSingle)
    test_comlpete(data, GeoPandasIntersect)

    test_comlpete(data, GeoPandasSegmentIntersectSingle)
    test_comlpete(data, GeoPandasSegmentIntersect)

    # PYGEOS
    val.TAG = "UNPREPARED"
    test_comlpete(data, PyGeosIntersectSingle, prepare=False)
    test_comlpete(data, PyGeosIntersect, prepare=False)
    test_comlpete(data, PyGeosSegmentIntersect, prepare=False)
    test_comlpete(data, PyGeosSegmentIntersectSingle, prepare=False)
    test_comlpete(data, PyGeosPandasIntersectSingle, prepare=False)
    test_comlpete(data, PyGeosPandasIntersect, prepare=False)
    test_comlpete(
        data,
        PyGeosPandasSegmentsIntersect,
        prepare=False,
    )
    test_comlpete(
        data,
        PyGeosPandasCollectionIntersect,
        prepare=False,
    )

    val.TAG = "PREPARED"
    test_comlpete(data, PyGeosIntersectSingle, prepare=True)
    test_comlpete(data, PyGeosIntersect, prepare=True)
    test_comlpete(data, PyGeosSegmentIntersect, prepare=True)
    test_comlpete(data, PyGeosSegmentIntersectSingle, prepare=True)
    test_comlpete(data, PyGeosPandasIntersectSingle, prepare=True)
    test_comlpete(data, PyGeosPandasIntersect, prepare=True)
    test_comlpete(
        data,
        PyGeosPandasSegmentsIntersect,
        prepare=True,
    )
    test_comlpete(
        data,
        PyGeosPandasCollectionIntersect,
        prepare=True,
    )

    # todo pygeos segments pandas
    # todo shapely pandas
    # todo shapely segments pandas
    # todo geopandas segments

    print(f"Found {ERRORS} errors during validation!")
