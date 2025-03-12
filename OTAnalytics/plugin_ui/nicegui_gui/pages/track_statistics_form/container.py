from OTAnalytics.adapter_ui.abstract_frame_track_statistics import (
    AbstractFrameTrackStatistics,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
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
        self._name = "All tracks"
        self._table = CustomTable(
            columns=[
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "Number", "label": "number", "field": "number"},
            ],
            rows=[
                {"name": f"{self._name}", "number": "0"},
                {"name": "Tracks assigned to flows", "number": "0"},
                {"name": "Tracks intersectiong not assignend", "number": "0"},
                {"name": "Number of Tracks with", "number": "0"},
                {"name": "INside cutting", "number": "0"},
                {"name": "Tracks not inside", "number": "0"},
                {"name": "Number of tracks to be va", "number": "0"},
            ],
        )

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_statistics(self)

    def build(self) -> None:
        self._table.build()

    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        update_track_rows = [
            {"name": "All Tracks", "number": f"{track_statistics.track_count}"},
            {
                "name": "Tracks assigned to flows",
                "number": f"{track_statistics.track_count_inside}",
            },
            {
                "name": "Tracks intersectiong not assignend",
                "number": f"{track_statistics.percentage_inside_assigned:.1%}",
            },
            {
                "name": "Number of Tracks with",
                "number": f"{track_statistics.percentage_inside_not_intersection:.1%}",
            },
            {
                "name": "INside cutting",
                "number": f"{track_statistics.percentage_inside_intersecting_but_unassigned:1%}",  # noqa
            },
            {
                "name": "Tracks not inside",
                "number": f"{track_statistics.number_of_tracks_to_be_validated}",
            },
            {
                "name": "Number of tracks to be va",
                "number": f"{track_statistics.number_of_tracks_with_simultaneous_section_events}",  # noqa
            },
        ]
        self._table.update(update_track_rows)
