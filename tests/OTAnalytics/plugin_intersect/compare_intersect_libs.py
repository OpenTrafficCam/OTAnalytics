import random

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import TrackId
from tests.OTAnalytics.plugin_intersect.intersect_data import load_data
from tests.OTAnalytics.plugin_intersect.intersect_provider import (
    GeoPandasIntersect,
    IntersectProvider,
    OTAIntersect,
    PyGeosIntersect,
    PyGeosPandasCollectionIntersect,
    PyGeosPandasIntersect,
    PyGeosSegmentIntersect,
    ShapelyIntersect,
)
from tests.OTAnalytics.plugin_intersect.validate import ERRORS, time, validate

REPEAT = 10
SEED = 42


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
    random.seed(seed)
    msg = ""
    for _ in range(n):
        sections = datastore.get_all_sections()
        k = random.randint(1, len(sections))
        msg += f"{k}, "
        selected = random.sample(sections, k)
        test_intersect_section(datastore, provider, sections=selected, record=record)
    print("Tested section counts: " + msg)


@time
def test_ota_shapely(datastore: Datastore) -> None:
    provider = OTAIntersect(datastore)

    test_intersect_all(datastore, provider, record=True)
    test_intersect_random_sections(
        datastore, provider, n=REPEAT, seed=SEED, record=True
    )


@time
def test_pygeos(datastore: Datastore) -> None:
    provider = PyGeosIntersect(datastore, prepare=False)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_segments(datastore: Datastore) -> None:
    provider = PyGeosSegmentIntersect(datastore, prepare=False)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_prepare(datastore: Datastore) -> None:
    provider = PyGeosIntersect(datastore, prepare=True)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_segments_prepare(datastore: Datastore) -> None:
    provider = PyGeosSegmentIntersect(datastore, prepare=True)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_pandas(datastore: Datastore) -> None:
    provider = PyGeosPandasIntersect(datastore, prepare=True)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_pandas_prepare(datastore: Datastore) -> None:
    provider = PyGeosPandasIntersect(datastore, prepare=True)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_pandas_collection(datastore: Datastore) -> None:
    provider = PyGeosPandasCollectionIntersect(datastore, prepare=False)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_pygeos_pandas_collection_prepare(datastore: Datastore) -> None:
    provider = PyGeosPandasCollectionIntersect(datastore, prepare=True)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_geopandas(datastore: Datastore) -> None:
    provider = GeoPandasIntersect(datastore)

    test_intersect_all(datastore, provider)
    test_intersect_random_sections(datastore, provider, n=REPEAT, seed=SEED)


@time
def test_shapely(datastore: Datastore) -> None:
    provider = ShapelyIntersect(datastore)

    test_intersect_all(datastore, provider, record=True)
    test_intersect_random_sections(
        datastore, provider, n=REPEAT, seed=SEED, record=True
    )


if __name__ == "__main__":
    data = load_data(skip_tracks=False, size="medium")

    print()
    print()
    test_shapely(data)
    print()
    print()
    test_geopandas(data)
    print()
    print()
    test_pygeos(data)
    print()
    print()
    test_pygeos_prepare(data)
    print()
    print()
    test_pygeos_pandas(data)
    print()
    print()
    test_pygeos_pandas_prepare(data)

    # todo pygeos segments pandas
    # todo shapely pandas
    # todo shapely segments pandas
    # todo geopandas segments

    # print()
    # print()
    # test_pygeos_segments(data)
    # print()
    # print()
    # test_pygeos_segments_prepare(data)

    print()
    print()
    test_pygeos_pandas_collection(data)
    print()
    print()
    test_pygeos_pandas_collection_prepare(data)

    print(f"Found {ERRORS} errors during validation!")
