from OTAnalytics.adapter_ui.abstract_frame_track_statistics import (
    AbstractFrameTrackStatistics,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackStatisticKeys,
)
from OTAnalytics.application.use_cases.track_statistics import TrackStatistics
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import CustomTable

COLUMN_NAME = "name"
COLUMN_NUMBER = "number"


def map_to_ui(
    resource_manager: ResourceManager, track_statistics: TrackStatistics
) -> list[dict[str, str]]:
    return [
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_ALL_TRACKS)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.track_count}",
        },
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.track_count_inside}",
        },
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.percentage_inside_assigned:.1%}",
        },
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.percentage_inside_not_intersection:.1%}",
        },
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_INSIDE_CUTTING_SECTIONS)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.percentage_inside_intersecting_but_unassigned:.1%}",  # noqa
        },
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_NOT_INTERSECTING_SECTIONS)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.number_of_tracks_to_be_validated}",
        },
        {
            COLUMN_NAME: f"{resource_manager.get(TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED)}",  # noqa
            COLUMN_NUMBER: f"{track_statistics.number_of_tracks_with_simultaneous_section_events}",  # noqa
        },
    ]


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:
    return [
        {
            "name": COLUMN_NAME,
            "label": resource_manager.get(TrackStatisticKeys.COLUMN_NAME),
            "field": "name",
        },
        {
            "name": COLUMN_NUMBER,
            "label": resource_manager.get(TrackStatisticKeys.COLUMN_NUMBER),
            "field": "number",
        },
    ]


class TrackStatisticForm(AbstractFrameTrackStatistics):

    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model
        self._table = CustomTable(
            columns=create_columns(self._resource_manager),
            rows=map_to_ui(self._resource_manager, TrackStatistics()),
            title=self._resource_manager.get(
                TrackStatisticKeys.TABLE_TRACK_STATISTICS_TITLE
            ),
        )
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_statistics(self)

    def build(self) -> None:
        self._table.build()

    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        update_track_rows = map_to_ui(self._resource_manager, track_statistics)
        self._table.update(update_track_rows)
