from datetime import datetime, timezone
from pathlib import Path

import pytest

from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    AssignmentRecord,
)
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.plugin_parser.road_user_assignment_csv_reader import (
    AssignmentFileError,
    read_assignment_records,
)
from tests.utils.builders.road_user_assignment import (
    ASSIGNMENT_CSV_COLUMNS,
    write_assignment_csv,
)

ROW = {
    ras.FLOW_ID: "f1",
    ras.ROAD_USER_ID: "ru1",
    ras.ROAD_USER_TYPE: "car",
    ras.START_INTERPOLATED_OCCURRENCE: "2026-10-27 06:15:00.000000",
    ras.END_INTERPOLATED_OCCURRENCE: "2026-10-27 06:15:10.000000",
    ras.AVG_SPEED_MPS: "10.0",
    ras.HOSTNAME: "camera",
}


def test_reads_records(tmp_path: Path) -> None:
    path = tmp_path / "chunk.road_user_assignments.csv"
    write_assignment_csv(path, [ROW])

    assert read_assignment_records(path) == [
        AssignmentRecord(
            road_user="ru1",
            flow_id="f1",
            road_user_type="car",
            start_occurrence=datetime(2026, 10, 27, 6, 15, tzinfo=timezone.utc),
            end_occurrence=datetime(2026, 10, 27, 6, 15, 10, tzinfo=timezone.utc),
            avg_speed_mps=10.0,
        )
    ]


def test_empty_speed_is_none(tmp_path: Path) -> None:
    path = tmp_path / "chunk.road_user_assignments.csv"
    write_assignment_csv(path, [{**ROW, ras.AVG_SPEED_MPS: ""}])

    (record,) = read_assignment_records(path)

    assert record.avg_speed_mps is None


def test_header_only_file_gives_no_records(tmp_path: Path) -> None:
    path = tmp_path / "chunk.road_user_assignments.csv"
    write_assignment_csv(path, [])

    assert read_assignment_records(path) == []


def test_missing_column_raises(tmp_path: Path) -> None:
    path = tmp_path / "old.road_user_assignments.csv"
    columns = [c for c in ASSIGNMENT_CSV_COLUMNS if c != ras.ROAD_USER_TYPE]
    write_assignment_csv(path, [ROW], columns)

    with pytest.raises(AssignmentFileError, match=ras.ROAD_USER_TYPE) as error:
        read_assignment_records(path)
    assert path.name in str(error.value)


def test_unparsable_time_raises(tmp_path: Path) -> None:
    path = tmp_path / "chunk.road_user_assignments.csv"
    write_assignment_csv(
        path, [{**ROW, ras.START_INTERPOLATED_OCCURRENCE: "yesterday"}]
    )

    with pytest.raises(AssignmentFileError, match=path.name):
        read_assignment_records(path)


def test_truncated_row_raises_with_file_name(tmp_path: Path) -> None:
    path = tmp_path / "cut.road_user_assignments.csv"
    write_assignment_csv(path, [ROW])
    with path.open("a", encoding="utf-8") as file:
        file.write("f1,ru2,car,2026-10-27 06:16:00.000000\n")

    with pytest.raises(AssignmentFileError, match=path.name):
        read_assignment_records(path)


def test_invalid_encoding_raises_with_file_name(tmp_path: Path) -> None:
    path = tmp_path / "binary.road_user_assignments.csv"
    write_assignment_csv(path, [ROW])
    with path.open("ab") as file:
        file.write(b"\xff\xfe\xfa\n")

    with pytest.raises(AssignmentFileError, match=path.name):
        read_assignment_records(path)
