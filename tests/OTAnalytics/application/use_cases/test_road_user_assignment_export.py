from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import RoadUserAssignment
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportRoadUserAssignments,
    RoadUserAssignmentBuilder,
    RoadUserAssignmentBuildError,
)
from OTAnalytics.domain.section import Section
from tests.utils.builders.road_user_assignment import create_road_user_assignment


@pytest.fixture
def _builder() -> RoadUserAssignmentBuilder:
    return RoadUserAssignmentBuilder()


class TestRoadUserAssignmentBuilder:
    def test_add_start_section(self, _builder: RoadUserAssignmentBuilder) -> None:
        section = Mock()
        _builder.add_start_section(section)
        assert _builder._start_section == section

    def test_add_end_section(self, _builder: RoadUserAssignmentBuilder) -> None:
        section = Mock()
        _builder.add_end_section(section)
        assert _builder._end_section == section

    def test_add_max_confidence(self, _builder: RoadUserAssignmentBuilder) -> None:
        confidence = 0.8
        _builder.add_max_confidence(confidence)
        assert _builder._max_confidence == confidence

    def test_build(
        self,
        _builder: RoadUserAssignmentBuilder,
        first_line_section: Section,
        second_line_section: Section,
        first_road_user_assignment: RoadUserAssignment,
    ) -> None:
        _builder.add_start_section(first_line_section)
        _builder.add_end_section(second_line_section)
        _builder.add_max_confidence(0.9)
        result = _builder.build(first_road_user_assignment)
        assert result == create_road_user_assignment(
            first_road_user_assignment, first_line_section, second_line_section
        )

    def test_build_with_start_section_missing(
        self, _builder: RoadUserAssignmentBuilder
    ) -> None:
        _builder.add_end_section(Mock())
        _builder.add_max_confidence(0.9)
        with pytest.raises(RoadUserAssignmentBuildError, match="Start section not set"):
            _builder.build(Mock())

    def test_build_with_end_section_missing(
        self, _builder: RoadUserAssignmentBuilder
    ) -> None:
        _builder.add_start_section(Mock())
        _builder.add_max_confidence(0.9)
        with pytest.raises(RoadUserAssignmentBuildError, match="End section not set"):
            _builder.build(Mock())

    def test_build_with_max_confidence_missing(
        self, _builder: RoadUserAssignmentBuilder
    ) -> None:
        _builder.add_start_section(Mock())
        _builder.add_end_section(Mock())
        with pytest.raises(
            RoadUserAssignmentBuildError, match="Max confidence not set"
        ):
            _builder.build(Mock())


class TestExportRoadUserAssignments:
    def test_export(self) -> None:
        event_repository = Mock()
        flow_repository = Mock()
        create_events = Mock()
        road_user_assigner = Mock()
        exporter_factory = Mock()

        events = Mock()
        event_repository.is_empty.return_value = False
        event_repository.get_all.return_value = events

        flows = Mock()
        flow_repository.get_all.return_value = flows

        assignments = Mock()
        road_user_assigner.assign.return_value = assignments

        exporter = Mock()
        exporter_factory.create.return_value = exporter

        export_road_user_assignments = ExportRoadUserAssignments(
            event_repository,
            flow_repository,
            create_events,
            road_user_assigner,
            exporter_factory,
        )
        specification = Mock()
        specification.save_path = Mock()
        specification.format = "csv"
        specification.mode = OVERWRITE

        export_road_user_assignments.export(specification)

        event_repository.is_empty.assert_called_once()
        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once_with(events, flows)
        exporter_factory.create.assert_called_once_with(specification)
        exporter.export.assert_called_once_with(assignments, OVERWRITE)
