from pathlib import Path
from unittest.mock import Mock

from pandas import DataFrame, read_csv

from OTAnalytics.application.analysis.traffic_counting import (
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    RoadUserAssignmentBuilder,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_parser.road_user_assignment_export import (
    RoadUserAssignmentCsvExporter,
)
from tests.utils.builders.road_user_assignment import create_road_user_assignment


class TestRoadUserAssignmentCsvExporter:
    def test_export(
        self,
        test_data_tmp_dir: Path,
        first_line_section: Section,
        second_line_section: Section,
        first_road_user_assignment: RoadUserAssignment,
        second_road_user_assignment: RoadUserAssignment,
    ) -> None:
        save_path = test_data_tmp_dir / "road_user_assignments.csv"

        section_repository = Mock()
        get_all_tracks = Mock()
        builder = RoadUserAssignmentBuilder()
        track_dataset = Mock()

        track_dataset.get_max_confidences_for.return_value = {
            first_road_user_assignment.road_user: 0.9,
            second_road_user_assignment.road_user: 0.7,
        }
        get_all_tracks.as_dataset.return_value = track_dataset
        section_repository.get.side_effect = [
            first_line_section,
            second_line_section,
            first_line_section,
            second_line_section,
        ]

        exporter = RoadUserAssignmentCsvExporter(
            section_repository, get_all_tracks, builder, save_path
        )
        exporter.export(
            RoadUserAssignments(
                [first_road_user_assignment, second_road_user_assignment]
            ),
            OVERWRITE,
        )
        expected = DataFrame(
            [
                create_road_user_assignment(
                    first_road_user_assignment,
                    first_line_section,
                    second_line_section,
                    0.9,
                ),
                create_road_user_assignment(
                    second_road_user_assignment,
                    first_line_section,
                    second_line_section,
                    0.7,
                ),
            ]
        )
        actual = read_csv(save_path)
        actual[ras.START_SECTION_ID] = actual[ras.START_SECTION_ID].astype(str)
        actual[ras.END_SECTION_ID] = actual[ras.END_SECTION_ID].astype(str)
        actual[ras.START_SECTION_NAME] = actual[ras.START_SECTION_NAME].astype(str)
        actual[ras.END_SECTION_NAME] = actual[ras.END_SECTION_NAME].astype(str)

        assert actual.equals(expected)
