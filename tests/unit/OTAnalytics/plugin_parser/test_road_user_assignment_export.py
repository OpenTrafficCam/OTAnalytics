import csv
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
from pandas import DataFrame, read_csv

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    RoadUserAssignmentBuilder,
)
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_parser.road_user_assignment_export import (
    RoadUserAssignmentCsvExporter,
)
from tests.utils.builders.event_builder import EventBuilder
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
            section_repository, get_all_tracks, builder, save_path
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
        )
        actual = read_csv(save_path)
        actual[ras.START_SECTION_ID] = actual[ras.START_SECTION_ID].astype(str)
        actual[ras.END_SECTION_ID] = actual[ras.END_SECTION_ID].astype(str)
        actual[ras.START_SECTION_NAME] = actual[ras.START_SECTION_NAME].astype(str)
        actual[ras.END_SECTION_NAME] = actual[ras.END_SECTION_NAME].astype(str)

        for col in (ras.FLOW_DISTANCE_M, ras.TRAVEL_TIME_S, ras.AVG_SPEED_MPS):
            expected[col] = expected[col].astype("float64")
            actual[col] = actual[col].astype("float64")

        assert actual.equals(expected)

    def test_export_writes_empty_cells_when_flow_distance_not_configured(
        self,
        test_data_tmp_dir: Path,
        first_line_section: Section,
        second_line_section: Section,
    ) -> None:
        """Unset flow.distance must yield blank CSV cells for distance and avg speed."""
        save_path = test_data_tmp_dir / "road_user_assignments_no_distance.csv"
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=6)
        start_event = EventBuilder(
            section_id=first_line_section.id.id,
            interpolated_occurrence=t0,
        ).build_section_event()
        end_event = EventBuilder(
            section_id=second_line_section.id.id,
            interpolated_occurrence=t1,
        ).build_section_event()
        flow = Flow(
            FlowId("no-dist"),
            "no-dist",
            first_line_section.id,
            second_line_section.id,
            distance=None,
        )
        assignment = RoadUserAssignment(
            "track-1", "car", flow, EventPair(start_event, end_event)
        )

        mock_factory = Mock()
        section_repository = Mock()
        get_all_tracks = Mock()
        builder = RoadUserAssignmentBuilder()
        track_dataset = Mock()
        track_dataset.get_max_confidences_for.return_value = {"track-1": 0.85}
        get_all_tracks.as_dataset.return_value = track_dataset
        section_repository.get.side_effect = [first_line_section, second_line_section]

        exporter = RoadUserAssignmentCsvExporter(
            section_repository, get_all_tracks, builder, save_path
        )
        exporter.export(
            RoadUserAssignments([assignment], mock_factory), OVERWRITE
        )

        text = save_path.read_text(encoding="utf-8")
        rows = list(csv.reader(StringIO(text)))
        assert len(rows) == 2
        header_cells, data_cells = rows
        idx_dist = header_cells.index(ras.FLOW_DISTANCE_M)
        idx_speed = header_cells.index(ras.AVG_SPEED_MPS)
        assert data_cells[idx_dist] == ""
        assert data_cells[idx_speed] == ""

        df = read_csv(save_path)
        assert df[ras.TRAVEL_TIME_S].iloc[0] == 6.0
        assert pd.isna(df[ras.FLOW_DISTANCE_M].iloc[0])
        assert pd.isna(df[ras.AVG_SPEED_MPS].iloc[0])
