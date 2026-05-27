from pathlib import Path
from unittest.mock import Mock

from pandas import DataFrame, read_csv

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.config import CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportSpecification,
    RoadUserAssignmentBuilder,
)
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_parser.road_user_assignment_export import (
    CSV_FORMAT,
    RoadUserAssignmentCsvExporter,
)
from tests.utils.builders.event_builder import EventBuilder
from tests.utils.builders.road_user_assignment import create_road_user_assignment

_GEO_COLUMNS = [ras.START_GEO_X, ras.START_GEO_Y, ras.END_GEO_X, ras.END_GEO_Y]


class TestRoadUserAssignmentCsvExporter:
    def test_export(
        self,
        test_data_tmp_dir: Path,
        first_line_section: Section,
        second_line_section: Section,
        first_road_user_assignment: RoadUserAssignment,
        second_road_user_assignment: RoadUserAssignment,
    ) -> None:
        given_specification = create_specification(save_directory=test_data_tmp_dir)
        expected_save_path = create_expected_save_path_from(given_specification)
        mock_factory = Mock()
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
            section_repository, get_all_tracks, builder, given_specification
        )
        exporter.export(
            RoadUserAssignments(
                [first_road_user_assignment, second_road_user_assignment], mock_factory
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
        ).drop(columns=_GEO_COLUMNS)
        actual = read_csv(expected_save_path)
        actual[ras.START_SECTION_ID] = actual[ras.START_SECTION_ID].astype(str)
        actual[ras.END_SECTION_ID] = actual[ras.END_SECTION_ID].astype(str)
        actual[ras.START_SECTION_NAME] = actual[ras.START_SECTION_NAME].astype(str)
        actual[ras.END_SECTION_NAME] = actual[ras.END_SECTION_NAME].astype(str)

        assert actual.equals(expected)

    def test_export_includes_geo_columns_when_present(
        self,
        test_data_tmp_dir: Path,
        first_line_section: Section,
        second_line_section: Section,
    ) -> None:
        given_specification = create_specification(save_directory=test_data_tmp_dir)
        save_path = (
            given_specification.export_directory
            / f"{given_specification.export_filename_stem}"
            f".{CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS}.csv"
        )

        start_builder = EventBuilder(road_user_id="Road User 1", geo_x=10.5, geo_y=20.5)
        start_builder.add_section_id(first_line_section.id.id)
        start_event = start_builder.build_section_event()

        end_builder = EventBuilder(road_user_id="Road User 1", geo_x=11.0, geo_y=21.0)
        end_builder.add_section_id(second_line_section.id.id)
        end_event = end_builder.build_section_event()

        flow = Flow(
            FlowId("flow-1"),
            "flow-1",
            first_line_section.id,
            second_line_section.id,
        )
        assignment = RoadUserAssignment(
            "Road User 1", "car", flow, EventPair(start_event, end_event)
        )

        mock_factory = Mock()
        section_repository = Mock()
        get_all_tracks = Mock()
        track_dataset = Mock()
        track_dataset.get_max_confidences_for.return_value = {"Road User 1": 0.9}
        get_all_tracks.as_dataset.return_value = track_dataset
        section_repository.get.side_effect = [first_line_section, second_line_section]

        exporter = RoadUserAssignmentCsvExporter(
            section_repository,
            get_all_tracks,
            RoadUserAssignmentBuilder(),
            given_specification,
        )
        exporter.export(RoadUserAssignments([assignment], mock_factory), OVERWRITE)

        actual = read_csv(save_path)
        assert ras.START_GEO_X in actual.columns
        assert ras.START_GEO_Y in actual.columns
        assert ras.END_GEO_X in actual.columns
        assert ras.END_GEO_Y in actual.columns
        assert actual[ras.START_GEO_X].iloc[0] == 10.5
        assert actual[ras.START_GEO_Y].iloc[0] == 20.5
        assert actual[ras.END_GEO_X].iloc[0] == 11.0
        assert actual[ras.END_GEO_Y].iloc[0] == 21.0


def create_specification(save_directory: Path) -> ExportSpecification:
    return ExportSpecification(
        export_directory=save_directory,
        export_filename_stem="my_ras",
        format=CSV_FORMAT.name,
        export_mode=OVERWRITE,
    )


def create_expected_save_path_from(specification: ExportSpecification) -> Path:
    return (
        specification.export_directory / f"{specification.export_filename_stem}"
        f".{CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS}.csv"
    )
