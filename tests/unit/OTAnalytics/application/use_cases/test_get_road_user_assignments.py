from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignmentRepository,
    RoadUserAssignmentRepositoryEvent,
)
from OTAnalytics.application.use_cases.assignment_repository import (
    GetRoadUserAssignments,
)
from OTAnalytics.domain.event import EventRepositoryEvent
from OTAnalytics.domain.observer import Subject
from OTAnalytics.plugin_datastore.polars_track_id_set import PolarsTrackIdSetFactory


class TestGetRoadUserAssignments:
    def test_get(self) -> None:
        given = configure_existing_assignments(setup())
        target = create_target(given)

        actual = target.get_as_list()

        assert actual == given.assignments_as_list
        given.assignment_repository.is_empty.assert_called_once()
        given.assignment_repository.get_all_as_list.assert_called_once()
        given.create_assignments.assert_called_once()

    def test_no_recursion_when_get_called_during_creation(self) -> None:
        """
        Fix bug OP#8949
        Test that recursive calls to get_as_list during assignment creation
        don't cause infinite recursion.
        """
        given = configure_existing_assignments(setup())
        target = create_target(given)

        call_count_side_effect = 0

        def mock_create_assignments_side_effect() -> None:
            nonlocal call_count_side_effect
            call_count_side_effect += 1
            result = target.get_as_list()
            assert result == given.assignments_as_list

        given.create_assignments.side_effect = mock_create_assignments_side_effect

        actual = target.get_as_list()

        assert actual == given.assignments_as_list
        assert call_count_side_effect == 1
        given.assignment_repository.is_empty.assert_called_once()
        assert given.assignment_repository.get_all_as_list.call_count == 2
        given.create_assignments.assert_called_once()

    def test_keep_empty_result(self) -> None:
        """Creating no assignments must not create them again on every read."""
        repository = create_empty_repository()
        create_assignments = Mock()
        target = GetRoadUserAssignments(repository, create_assignments)

        target.get_as_list()
        target.get_as_list()

        create_assignments.assert_called_once()

    def test_create_again_after_repository_changed(self) -> None:
        repository = create_empty_repository()
        create_assignments = Mock()
        target = GetRoadUserAssignments(repository, create_assignments)
        target.get_as_list()

        repository.clear()
        target.get_as_list()

        assert create_assignments.call_count == 2

    def test_keep_result_when_creation_changes_repository(self) -> None:
        repository = create_empty_repository()
        create_assignments = Mock(side_effect=lambda: repository.add_all([]))
        target = GetRoadUserAssignments(repository, create_assignments)

        target.get_as_list()
        target.get_as_list()

        create_assignments.assert_called_once()

    def test_create_again_after_events_added(self) -> None:
        repository = create_empty_repository()
        create_assignments = Mock()
        target = GetRoadUserAssignments(repository, create_assignments)
        target.get_as_list()

        target.notify_events(EventRepositoryEvent(added=[Mock()], removed=[]))
        target.get_as_list()

        assert create_assignments.call_count == 2

    def test_keep_empty_result_when_events_removed(self) -> None:
        repository = create_empty_repository()
        create_assignments = Mock()
        target = GetRoadUserAssignments(repository, create_assignments)
        target.get_as_list()

        target.notify_events(EventRepositoryEvent(added=[], removed=[Mock()]))
        target.get_as_list()

        create_assignments.assert_called_once()


def create_empty_repository() -> RoadUserAssignmentRepository:
    return RoadUserAssignmentRepository(
        PolarsTrackIdSetFactory(), Subject[RoadUserAssignmentRepositoryEvent]()
    )


@dataclass
class Given:
    assignments_as_list: list[Mock]
    assignment_repository: Mock
    create_assignments: Mock


def setup() -> Given:
    assignments_as_list = [Mock(), Mock()]

    assignment_repository = Mock(spec=RoadUserAssignmentRepository)
    assignment_repository.is_empty.return_value = False

    create_assignments = Mock()

    return Given(
        assignments_as_list=assignments_as_list,
        assignment_repository=assignment_repository,
        create_assignments=create_assignments,
    )


def configure_existing_assignments(given: Given) -> Given:
    given.assignment_repository.get_all_as_list.return_value = given.assignments_as_list
    given.assignment_repository.is_empty.return_value = True
    return given


def create_target(given: Given) -> GetRoadUserAssignments:
    return GetRoadUserAssignments(
        given.assignment_repository, given.create_assignments, True
    )
