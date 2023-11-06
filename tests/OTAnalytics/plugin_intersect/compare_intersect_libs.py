import random

from pyparsing import Any

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import TrackId
from tests.OTAnalytics.plugin_intersect.intersect_data import load_data
from tests.OTAnalytics.plugin_intersect.intersect_provider import (
    GeoPandasIntersect,
    GeoPandasSegmentIntersect,
    IntersectProvider,
    OTAIntersect,
    PyGeosIntersect,
    PyGeosPandasIntersect,
    PyGeosPandasSegmentIntersect,
    PyGeosSegmentIntersect,
    ShapelyIntersect,
    ShapelySegmentIntersect,
)
from tests.OTAnalytics.plugin_intersect.validate import (
    ERRORS,
    time,
    validate,
    validate_events,
)

REPEAT = 10
SEED = 42
TEST_INTERSECT = True
TEST_EVENTS = True


@validate
@time
def test_intersect_all(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    mode: int,
    record: bool = False,
) -> set[TrackId]:
    return provider.intersect(
        datastore.get_all_tracks(), datastore.get_all_sections(), mode=mode
    )


@validate_events
@time
def test_events_all(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    mode: int,
    record: bool = False,
) -> list[tuple[float, float]]:
    return provider.events(
        datastore.get_all_tracks(), datastore.get_all_sections(), mode=mode
    )


@validate
@time
def test_intersect_section(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    mode: int,
    sections: list[Section],
    record: bool = False,
) -> set[TrackId]:
    return provider.intersect(datastore.get_all_tracks(), sections, mode=mode)


@validate_events
@time
def test_events_section(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    mode: int,
    sections: list[Section],
    record: bool = False,
) -> list[tuple[float, float]]:
    return provider.events(datastore.get_all_tracks(), sections, mode=mode)


@time
def test_intersect_random_sections(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    mode: int,
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
            datastore,
            name=name,
            provider=provider,
            mode=mode,
            sections=selected,
            record=record,
        )


@time
def test_events_random_sections(
    datastore: Datastore,
    name: str,
    provider: IntersectProvider,
    mode: int,
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
            datastore,
            name=name,
            provider=provider,
            mode=mode,
            sections=selected,
            record=record,
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
        for mode in provider.intersect_modes():
            test_intersect_all(
                datastore, name=name, provider=provider, mode=mode, record=record
            )
            # test_intersect_random_sections(
            #    datastore,
            #    name=name,
            #    provider=provider,
            #    mode=mode,
            #    n=REPEAT,
            #    seed=SEED,
            #    record=record,
            # )

    if TEST_EVENTS:
        for mode in provider.event_modes():
            test_events_all(
                datastore, name=name, provider=provider, mode=mode, record=record
            )
            # test_events_random_sections(
            #    datastore,
            #    name=name,
            #    provider=provider,
            #    mode=mode,
            #    n=REPEAT,
            #    seed=SEED,
            #    record=record,
            # )


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

    test_comlpete(data, ShapelyIntersect)
    test_comlpete(data, ShapelySegmentIntersect)

    # GEOPANDAS
    test_comlpete(data, GeoPandasIntersect)
    test_comlpete(data, GeoPandasSegmentIntersect)

    # PYGEOS
    val.TAG = "UNPREPARED"
    test_comlpete(data, PyGeosIntersect, _prepare=False)
    test_comlpete(data, PyGeosSegmentIntersect, _prepare=False)
    test_comlpete(data, PyGeosPandasIntersect, _prepare=False)
    test_comlpete(data, PyGeosPandasSegmentIntersect, _prepare=False)

    val.TAG = "PREPARED"
    test_comlpete(data, PyGeosIntersect, _prepare=True)
    test_comlpete(data, PyGeosSegmentIntersect, _prepare=True)
    test_comlpete(data, PyGeosPandasIntersect, _prepare=True)
    test_comlpete(data, PyGeosPandasSegmentIntersect, _prepare=True)

    print(f"Found {ERRORS} errors during validation!")
