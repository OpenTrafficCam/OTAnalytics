from typing import Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import Plotter
from OTAnalytics.domain.track import TrackImage


class LayeredPlotter(Plotter):
    def __init__(self, layers: list[Plotter]) -> None:
        self._layers = layers
        self._current_image: Optional[TrackImage] = None

    def plot(self) -> Optional[TrackImage]:
        for layer in self._layers:
            if current_layer := layer.plot():
                self.__add(current_layer)
        return self._current_image

    def __add(self, image: TrackImage) -> None:
        if self._current_image:
            self._current_image = self._current_image.add(image)
        else:
            self._current_image = image


class TrackBackgroundPlotter(Plotter):
    """Plot video frame as background."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore

    def plot(self) -> Optional[TrackImage]:
        if track := next(iter(self._datastore.get_all_tracks())):
            return self._datastore.get_image_of_track(track.id)
        return None
