from unittest.mock import Mock

import pytest

from OTAnalytics.application.export_formats import track_statistics as ts
from OTAnalytics.application.export_formats.export_mode import INITIAL_MERGE
from OTAnalytics.application.use_cases.track_statistics_export import (
    ExportTrackStatistics,
    TrackStatisticsBuilder,
)


@pytest.fixture
def _builder() -> TrackStatisticsBuilder:
    return TrackStatisticsBuilder()


class TestTrackStatisticsBuilder:
    def test_build(
        self,
        _builder: TrackStatisticsBuilder,
    ) -> None:
        track_statistics = Mock()
        track_statistics.track_count = 10
        track_statistics.track_count_outside = 1
        track_statistics.track_count_inside = 9
        track_statistics.track_count_inside_not_intersecting = 1
        track_statistics.track_count_inside_intersecting_but_unassigned = 3
        track_statistics.track_count_inside_assigned = 5
        track_statistics.percentage_inside_assigned = 5.0 / 9
        track_statistics.number_of_tracks_to_be_validated = 23
        track_statistics.number_of_tracks_with_simultaneous_section_events = 0

        result = _builder.build(track_statistics)

        assert result == {
            ts.TRACK_COUNT: track_statistics.track_count,
            ts.TRACK_COUNT_OUTSIDE: track_statistics.track_count_outside,
            ts.TRACK_COUNT_INSIDE: track_statistics.track_count_inside,
            ts.TRACK_COUNT_INSIDE_NOT_INTERSECTING: track_statistics.track_count_inside_not_intersecting,  # noqa
            ts.TRACK_COUNT_INSIDE_INTERSECTING_BUT_UNASSIGNED: track_statistics.track_count_inside_intersecting_but_unassigned,  # noqa
            ts.TRACK_COUNT_INSIDE_ASSIGNED: track_statistics.track_count_inside_assigned,  # noqa
            ts.PERCENTAGE_INSIDE_ASSIGNED: track_statistics.percentage_inside_assigned,  # noqa
            ts.PERCENTAGE_INSIDE_NOT_INTERSECTING: track_statistics.percentage_inside_not_intersection,  # noqa
            ts.PERCENTAGE_INSIDE_INTERSECTING_BUT_UNASSIGNED: track_statistics.percentage_inside_intersecting_but_unassigned,  # noqa
            ts.NUMBER_OF_TRACKS_TO_BE_VALIDATED: track_statistics.number_of_tracks_to_be_validated,  # noqa
            ts.NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_ENTER_SECTION_EVENTS: track_statistics.number_of_tracks_with_simultaneous_section_events,  # noqa
        }


class TestExportTrackStatistics:
    def test_export(self) -> None:
        calculate_track_statistics = Mock()
        track_statistics = Mock()
        calculate_track_statistics.get_statistics.return_value = track_statistics

        exporter_factory = Mock()
        exporter = Mock()
        exporter_factory.create.return_value = exporter

        export_track_statistics = ExportTrackStatistics(
            calculate_track_statistics,
            exporter_factory,
        )

        specification = Mock()
        specification.export_mode = INITIAL_MERGE

        export_track_statistics.export(specification)

        calculate_track_statistics.get_statistics.assert_called_once()
        exporter_factory.create.assert_called_once_with(specification)
        exporter.export.assert_called_once_with(
            track_statistics, specification.export_mode
        )
