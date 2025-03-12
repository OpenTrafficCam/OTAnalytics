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
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class TrackStatisticForm(AbstractFrameTrackStatistics):

    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model
        self._table = CustomTable(
            columns=[
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "Number", "label": "number", "field": "number"},
            ],
            rows=[
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_ALL_TRACKS)}",  # noqa
                    "number": "0",
                },
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS)}",  # noqa
                    "number": "0",
                },
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED)}",  # noqa
                    "number": "0",
                },
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS)}",  # noqa
                    "number": "0",
                },  # noqa
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_INSIDE_CUTTING_SECTIONS)}",  # noqa
                    "number": "0",
                },
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_NOT_INTERSECTING_SECTIONS)}",  # noqa
                    "number": "0",
                },
                {
                    "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED)}",  # noqa
                    "number": "0",
                },
            ],
        )
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_statistics(self)

    def build(self) -> None:
        self._table.build()

    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        update_track_rows = [
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_ALL_TRACKS)}",  # noqa
                "number": f"{track_statistics.track_count}",
            },
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_ASSIGNED_TO_FLOWS)}",  # noqa
                "number": f"{track_statistics.track_count_inside}",
            },
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_INTERSECTING_NOT_ASSIGNED)}",  # noqa
                "number": f"{track_statistics.percentage_inside_assigned:.1%}",
            },
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_WITH_SIMULTANEOUS_SECTION_EVENTS)}",  # noqa
                "number": f"{track_statistics.percentage_inside_not_intersection:.1%}",
            },
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_INSIDE_CUTTING_SECTIONS)}",  # noqa
                "number": f"{track_statistics.percentage_inside_intersecting_but_unassigned:1%}",  # noqa
            },
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_TRACKS_NOT_INTERSECTING_SECTIONS)}",  # noqa
                "number": f"{track_statistics.number_of_tracks_to_be_validated}",
            },
            {
                "name": f"{self._resource_manager.get(TrackStatisticKeys.LABEL_NUMBER_OF_TRACKS_TO_BE_VALIDATED)}",  # noqa
                "number": f"{track_statistics.number_of_tracks_with_simultaneous_section_events}",  # noqa
            },
        ]
        self._table.update(update_track_rows)
