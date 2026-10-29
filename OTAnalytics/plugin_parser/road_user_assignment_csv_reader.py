"""Reads road user assignment CSV files for restoring traffic statistics."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from OTAnalytics.application.analysis.traffic_statistics.day_statistics import (
    AssignmentRecord,
)
from OTAnalytics.application.export_formats import road_user_assignments as ras

REQUIRED_COLUMNS = (
    ras.FLOW_ID,
    ras.ROAD_USER_ID,
    ras.ROAD_USER_TYPE,
    ras.START_INTERPOLATED_OCCURRENCE,
    ras.END_INTERPOLATED_OCCURRENCE,
    ras.AVG_SPEED_MPS,
)


class AssignmentFileError(ValueError):
    """Raised if a road user assignment file cannot be read."""


def read_assignment_records(path: Path) -> list[AssignmentRecord]:
    """Read the assignments of a road user assignment CSV file.

    Times in the file have no timezone and are UTC. An empty speed cell (flow
    without distance) becomes None.

    Raises:
        AssignmentFileError: if a required column is missing or a value cannot
            be parsed.
    """
    try:
        with path.open(encoding="utf-8", newline="") as file:
            return _read_rows(path, csv.DictReader(file))
    except UnicodeDecodeError as cause:
        raise AssignmentFileError(f"{path} is not UTF-8: {cause}") from cause


def _read_rows(path: Path, reader: csv.DictReader) -> list[AssignmentRecord]:
    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise AssignmentFileError(f"{path} lacks the column(s) {missing}.")
    records = []
    for row_number, row in enumerate(reader, start=2):
        try:
            records.append(_to_record(row))
        except (ValueError, TypeError) as cause:
            raise AssignmentFileError(f"{path} row {row_number}: {cause}") from cause
    return records


def _to_record(row: dict[str, str]) -> AssignmentRecord:
    speed = row[ras.AVG_SPEED_MPS]
    return AssignmentRecord(
        road_user=row[ras.ROAD_USER_ID],
        flow_id=row[ras.FLOW_ID],
        road_user_type=row[ras.ROAD_USER_TYPE],
        start_occurrence=_parse_time(row[ras.START_INTERPOLATED_OCCURRENCE]),
        end_occurrence=_parse_time(row[ras.END_INTERPOLATED_OCCURRENCE]),
        avg_speed_mps=float(speed) if speed else None,
    )


def _parse_time(value: str) -> datetime:
    return datetime.strptime(value, ras.DATE_TIME_FORMAT).replace(tzinfo=timezone.utc)
