from typing import Any

from customtkinter import CTkLabel, ThemeManager

from OTAnalytics.adapter_ui.abstract_frame_track_statistics import (
    AbstractFrameTrackStatistics,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.use_cases.track_statistics import TrackStatistics
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY

INITIAL_VALUE_OF_TRACK_STATISTIC: str = "Please update flow highlighting"


class FrameTrackStatistics(AbstractCTkFrame, AbstractFrameTrackStatistics):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._is_initialized = False
        self._viewmodel = viewmodel
        self.default_border_color = ThemeManager.theme["CTkEntry"]["border_color"]
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()
        self._is_initialized = True

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_statistics(self)

    def _get_widgets(self) -> None:
        self._label_all_tracks = CTkLabel(
            master=self, text="All tracks:", anchor="nw", justify="right"
        )
        self._label_all_tracks_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )
        self._label_inside_tracks = CTkLabel(
            master=self, text="Inside cutting section:", anchor="nw", justify="right"
        )
        self._label_inside_tracks_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )
        self._label_assigned_tracks = CTkLabel(
            master=self, text="Tracks assigned to flows:", anchor="nw", justify="right"
        )
        self._label_assigned_tracks_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )
        self._label_not_intersection_tracks = CTkLabel(
            master=self,
            text="Tracks not intersecting sections:",
            anchor="nw",
            justify="right",
        )
        self._label_not_intersection_tracks_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )
        self._label_intersecting_not_assigned_tracks = CTkLabel(
            master=self,
            text="Tracks intersecting not assigned:",
            anchor="nw",
            justify="right",
        )
        self._label_intersecting_not_assigned_tracks_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )
        self._label_number_of_tracks_to_be_validated = CTkLabel(
            master=self,
            text="Number of tracks to be validated:",
            anchor="nw",
            justify="right",
        )
        self._label_number_of_tracks_to_be_validated_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )
        self._label_number_of_simultaneous_section_events = CTkLabel(
            master=self,
            text="Number of tracks with simultaneous section events:",
            anchor="nw",
            justify="right",
        )
        self._label_number_of_simultaneous_section_events_value = CTkLabel(
            master=self,
            text=INITIAL_VALUE_OF_TRACK_STATISTIC,
            anchor="nw",
            justify="right",
        )

    def _place_widgets(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure((1, 3), weight=1)
        for index, label in enumerate(
            [
                self._label_all_tracks,
                self._label_all_tracks_value,
                self._label_inside_tracks,
                self._label_inside_tracks_value,
                self._label_assigned_tracks,
                self._label_assigned_tracks_value,
                self._label_not_intersection_tracks,
                self._label_not_intersection_tracks_value,
                self._label_intersecting_not_assigned_tracks,
                self._label_intersecting_not_assigned_tracks_value,
                self._label_number_of_tracks_to_be_validated,
                self._label_number_of_tracks_to_be_validated_value,
                self._label_number_of_simultaneous_section_events,
                self._label_number_of_simultaneous_section_events_value,
            ]
        ):
            label.grid(
                row=int(index / 4),
                column=int(index % 4),
                padx=PADX,
                pady=0,
                sticky=STICKY,
            )

    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        self._label_all_tracks_value.configure(text=f"{track_statistics.track_count}")
        self._label_inside_tracks_value.configure(
            text=f"{track_statistics.track_count_inside}"
        )
        self._label_assigned_tracks_value.configure(
            text=f"{track_statistics.track_count_inside_assigned} "
            f"({track_statistics.percentage_inside_assigned:.1%}) "
        )
        self._label_not_intersection_tracks_value.configure(
            text=f"{track_statistics.track_count_inside_not_intersecting} "
            f"({track_statistics.percentage_inside_not_intersection:.1%}) "
        )
        self._label_intersecting_not_assigned_tracks_value.configure(
            text=f"{track_statistics.track_count_inside_intersecting_but_unassigned} "
            f"({track_statistics.percentage_inside_intersecting_but_unassigned:.1%}) "
        )
        self._label_number_of_tracks_to_be_validated_value.configure(
            text=str(track_statistics.number_of_tracks_to_be_validated)
        )
        self._label_number_of_simultaneous_section_events_value.configure(
            text=str(track_statistics.number_of_tracks_with_simultaneous_section_events)
        )
