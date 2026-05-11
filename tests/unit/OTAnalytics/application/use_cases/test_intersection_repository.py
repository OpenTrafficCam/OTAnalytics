from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
)
from OTAnalytics.application.use_cases.intersection_repository import (
    ClearAllIntersections,
)
from OTAnalytics.domain.section import SectionId, SectionRepositoryEvent
from OTAnalytics.domain.track import TrackId


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


@pytest.fixture
def intersection_repository() -> Mock:
    return Mock(spec=IntersectionRepository)


class TestClearAllIntersections:
    def test_notify_section(
        self,
        intersection_repository: Mock,
        section_id_1: SectionId,
    ) -> None:
        use_case = ClearAllIntersections(intersection_repository)

        use_case.on_section_changed(section_id_1)

        intersection_repository.remove.assert_called_once_with({section_id_1})

    def test_notify_sections(
        self,
        intersection_repository: Mock,
        section_id_1: SectionId,
        section_id_2: SectionId,
    ) -> None:
        use_case = ClearAllIntersections(intersection_repository)
        sections = [section_id_1, section_id_2]

        use_case.notify_sections(SectionRepositoryEvent.create_removed(sections))

        intersection_repository.remove.assert_called_once_with(set(sections))
