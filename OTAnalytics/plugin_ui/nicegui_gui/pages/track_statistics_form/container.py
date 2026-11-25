from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_track_statistics import \
    AbstractFrameTrackStatistics
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager, TrackStatisticKeys)
from OTAnalytics.application.use_cases.track_statistics import TrackStatistics

COLUMN_NAME = "name"
COLUMN_NUMBER = "number"
MARKER_TRACK_STATISTICS = "marker-track-statistics"


def _count_with_percentage(count: int, percentage: float) -> str:
    return f"{count} ({percentage:.1%})"


def map_to_ui(
    resource_manager: ResourceManager, track_statistics: TrackStatistics
) -> list[dict[str, str]]:
    rows: list[tuple[TrackStatisticKeys, str]] = [
        (TrackStatisticKeys.LABEL_ALL_TRACKS, str(track_statistics.track_count)),
        (
            TrackStatisticKeys.LABEL_INSIDE_CUTTING_SECTIONS,
            str(track_statistics.track_count_inside),
        ),
        (
            TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS,
            _count_with_percentage(
                track_statistics.track_count_inside_assigned,
                track_statistics.percentage_inside_assigned,
            ),
        ),
        (
            TrackStatisticKeys.LABEL_TRACKS_NOT_INTERSECTING_SECTIONS,
            _count_with_percentage(
                track_statistics.track_count_inside_not_intersecting,
                track_statistics.percentage_inside_not_intersection,
            ),
        ),
        (
            TrackStatisticKeys.LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED,
            _count_with_percentage(
                track_statistics.track_count_inside_intersecting_but_unassigned,
                track_statistics.percentage_inside_intersecting_but_unassigned,
            ),
        ),
        (
            TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED,
            str(track_statistics.number_of_tracks_to_be_validated),
        ),
        (
            TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS,
            str(track_statistics.number_of_tracks_with_simultaneous_section_events),
        ),
    ]
    return [
        {COLUMN_NAME: resource_manager.get(key), COLUMN_NUMBER: value}
        for key, value in rows
    ]


class TrackStatisticForm(AbstractFrameTrackStatistics):
    """Track statistics as one row of label and value pairs in the status bar."""

    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model
        self._rows = map_to_ui(self._resource_manager, TrackStatistics())
        # Created by `build()`, which runs when a browser asks for the page.
        self._values: list[ui.label] = []
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_statistics(self)

    def build(self) -> None:
        self._values = []
        with ui.row(wrap=False).classes("ota-stats").mark(MARKER_TRACK_STATISTICS):
            ui.label(
                self._resource_manager.get(
                    TrackStatisticKeys.LABEL_TRACK_STATISTIC_FORM_HEADER
                )
            ).classes("ota-stats-title")
            for row in self._rows:
                with ui.row(wrap=False).classes("ota-stat"):
                    ui.label(row[COLUMN_NAME]).classes("ota-stat-label")
                    self._values.append(
                        ui.label(row[COLUMN_NUMBER]).classes("ota-stat-value")
                    )

    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        self._rows = map_to_ui(self._resource_manager, track_statistics)
        for value, row in zip(self._values, self._rows):
            value.set_text(row[COLUMN_NUMBER])
