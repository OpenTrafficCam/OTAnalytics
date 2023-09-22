from abc import abstractmethod
from typing import Callable, Optional, Sequence

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import ObservableProperty, Plotter, TrackViewState
from OTAnalytics.domain.track import TrackImage


class Layer:
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the layer.

        Returns:
            str: the name.
        """
        raise NotImplementedError

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """Disable or enable the layer.

        Args:
            enabled (bool): `True` to enable. `False` to disable.
        """
        raise NotImplementedError

    @abstractmethod
    def is_enabled(self) -> bool:
        """Returns whether layer is enabled."""
        raise NotImplementedError

    @abstractmethod
    def register(self, observer: Callable[[bool], None]) -> None:
        """Register observer to layer to get notifications on layer enabled state
        changes.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset layer enabled state to default value."""
        raise NotImplementedError


class PlottingLayer(Plotter, Layer):
    def __init__(self, name: str, other: Plotter, enabled: bool) -> None:
        self._name = name
        self._other = other
        self._enabled: ObservableProperty[bool] = ObservableProperty[bool](enabled)
        self._default_enabled = enabled

    def plot(self) -> Optional[TrackImage]:
        """Plots layer if enabled.

        Returns:
            Optional[TrackImage]: the image that the layer has been plotted onto.
        """
        return self._other.plot() if self._enabled.get() else None

    def get_name(self) -> str:
        return self._name

    def set_enabled(self, enabled: bool) -> None:
        self._enabled.set(enabled)

    def is_enabled(self) -> bool:
        return self._enabled.get()

    def register(self, observer: Callable[[bool], None]) -> None:
        self._enabled.register(observer)

    def reset(self) -> None:
        """Reset layer enabled state to default value."""
        self._enabled.set(self._default_enabled)


class LayeredPlotter(Plotter):
    def __init__(self, layers: Sequence[PlottingLayer]) -> None:
        self._layers = layers
        self._current_image: Optional[TrackImage] = None

    def plot(self) -> Optional[TrackImage]:
        self._current_image = None
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

    def __init__(self, track_view_state: TrackViewState, datastore: Datastore) -> None:
        self._track_view_state = track_view_state
        self._datastore = datastore

    def plot(self) -> Optional[TrackImage]:
        if videos := self._track_view_state.selected_videos.get():
            if len(videos) > 0:
                return videos[0].get_frame(0)
        return None
