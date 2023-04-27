from abc import ABC, abstractmethod
from typing import Iterable, Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import Plotter, TrackViewState
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track, TrackImage


class TrackPlotter(ABC):
    """
    Abstraction to plot the background image.
    """

    @abstractmethod
    def plot(
        self,
        tracks: Iterable[Track],
        sections: Iterable[Section],
        width: int,
        height: int,
        filter_classes: Iterable[str] = (
            "car",
            "motorcycle",
            "person",
            "truck",
            "bicycle",
            "train",
        ),
        num_min_frames: int = 30,
        start_time: str = "",
        end_time: str = "2022-09-15 07:05:00",
        start_end: bool = True,
        plot_sections: bool = True,
        alpha: float = 0.1,
        offset: Optional[RelativeOffsetCoordinate] = RelativeOffsetCoordinate(0, 0),
    ) -> TrackImage:
        pass


class PlotterPrototype(Plotter):
    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        track_plotter: TrackPlotter,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._track_plotter = track_plotter

    def plot(self) -> Optional[TrackImage]:
        if track := next(iter(self._datastore.get_all_tracks())):
            if new_image := self._datastore.get_image_of_track(track.id):
                if self._track_view_state.show_tracks.get():
                    track_image = self._track_plotter.plot(
                        self._datastore.get_all_tracks(),
                        self._datastore.get_all_sections(),
                        width=new_image.width(),
                        height=new_image.height(),
                        offset=self._track_view_state.track_offset.get(),
                    )
                    return new_image.add(track_image)
                else:
                    return new_image
        return None
