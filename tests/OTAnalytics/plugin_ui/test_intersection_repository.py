import pytest

from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.plugin_ui.intersection_repository import PythonIntersectionRepository


@pytest.fixture
def track_id_1() -> TrackId:
    return TrackId("1")


@pytest.fixture
def track_id_2() -> TrackId:
    return TrackId("2")


@pytest.fixture
def section_id_1() -> SectionId:
    return SectionId("section-1")


@pytest.fixture
def section_id_2() -> SectionId:
    return SectionId("section-2")


class TestPythonIntersectionRepository:
    def test_store(self, section_id_1: SectionId, track_id_1: TrackId) -> None:
        intersections = {section_id_1: {track_id_1}}
        repository = PythonIntersectionRepository()

        repository.store(intersections)
        stored_intersections = repository.get({section_id_1})

        assert stored_intersections == intersections

    def test_clear(self, section_id_1: SectionId, track_id_1: TrackId) -> None:
        intersections = {section_id_1: {track_id_1}}
        repository = PythonIntersectionRepository()
        repository.store(intersections)

        repository.clear()

        assert repository.get_all() == {}

    def test_remove(
        self,
        section_id_1: SectionId,
        section_id_2: SectionId,
        track_id_1: TrackId,
        track_id_2: TrackId,
    ) -> None:
        intersections = {section_id_1: {track_id_1}, section_id_2: {track_id_2}}
        repository = PythonIntersectionRepository()
        repository.store(intersections)

        repository.remove({section_id_1})

        assert repository.get_all() == {section_id_2: {track_id_2}}

    def test_remove_missing(self, section_id_1: SectionId) -> None:
        repository = PythonIntersectionRepository()

        repository.remove({section_id_1})

        assert repository.get_all() == {}

    def test_get(
        self,
        section_id_1: SectionId,
        section_id_2: SectionId,
        track_id_1: TrackId,
        track_id_2: TrackId,
    ) -> None:
        intersections = {section_id_1: {track_id_1}, section_id_2: {track_id_2}}
        repository = PythonIntersectionRepository()
        repository.store(intersections)
        actual = repository.get({section_id_1, section_id_2})
        assert actual == intersections
        assert repository.get({SectionId("None")}) == {}
