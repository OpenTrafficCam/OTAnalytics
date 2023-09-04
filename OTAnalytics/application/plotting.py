from abc import abstractmethod
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    ObservableOptionalProperty,
    ObservableProperty,
    Plotter,
    TrackViewState,
)
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
        """Returns wether layer is enabled."""
        raise NotImplementedError

    @abstractmethod
    def register(self, observer: Callable[[bool], None]) -> None:
        """Register observer to layer to get notifications on layer enabled state
        changes.
        """
        raise NotImplementedError


class PlottingLayer(Plotter, Layer):
    def __init__(self, name: str, other: Plotter, enabled: bool) -> None:
        self._name = name
        self._other = other
        self._enabled: ObservableProperty[bool] = ObservableProperty[bool](enabled)

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


class CachedPlotter(Plotter):
    """
    A plotter caching the generated track image.
    It can listen to changes of observable properties to invalidate the cache.
    It can also be registered at subjects via:
        subject.register(cached_plotter.invalidate_cache)
    """

    def __init__(
        self,
        other: Plotter,
        subjects: list[ObservableProperty | ObservableOptionalProperty],
    ) -> None:
        self._other = other
        self._cache: Optional[TrackImage] = None

        for subject in subjects:
            subject.register(self.invalidate_cache)

    def plot(self) -> Optional[TrackImage]:
        if self._cache is None:
            self._cache = self._other.plot()

        return self._cache

    def invalidate_cache(self, _: Any) -> None:
        self._cache = None


ENTITY = TypeVar("ENTITY")
EntityPlotterFactory = Callable[[ENTITY], Plotter]
AvailableEntityProvider = Callable[[], set[ENTITY]]
VisibilitySubject = ObservableProperty[list[ENTITY]]


class DynamicLayersPlotter(Plotter, Generic[ENTITY]):
    """
    A plotter managing entity specific, toggleable, cached plot layers.
    Entities can e.g. be SectionIds or FlowIds.

    An EntityPlotterFactory is used to create delegate plotters for each managed entity.
    The DynamicLayersPlotter listens to changes of the VisibilitySubject
        to toggle the visibility of the entity layers.
    An AvailableEntityProvider is used to check which entities are remaining
        (since entity deletion is notified by "[]" in entity repositories).
    """

    def __init__(
        self,
        plotter_factory: EntityPlotterFactory,
        visibility_subject: VisibilitySubject,
        entity_lookup: AvailableEntityProvider,
    ) -> None:
        self._plotter_factory = plotter_factory
        self._entity_lookup = entity_lookup

        self._layer_mapping: dict[ENTITY, PlottingLayer] = dict()
        self._plotter_mapping: dict[ENTITY, CachedPlotter] = dict()
        # additional plotter mapping could be avoided
        # if PlottingLayer were Generic in the used plotter type

        visibility_subject.register(self.notify_visibility)

    def plot(self) -> Optional[TrackImage]:
        print(
            "plot",
            [
                (layer.get_name(), layer._enabled.get())
                for layer in self._layer_mapping.values()
            ],
        )
        layer_plotter = LayeredPlotter(list(self._layer_mapping.values()))
        return layer_plotter.plot()

    def notify_visibility(self, visible_entities: list[ENTITY]) -> None:
        """Set visibility of given entities to true, others to false."""
        print("update visibility:", visible_entities)
        for entity, layer in self._layer_mapping.items():
            layer.set_enabled(entity in visible_entities)

    def notify_invalidate(self, _: Any) -> None:
        """Invalidate all caches."""
        print("invalidate all:", self._plotter_mapping.values())
        for plotter in self._plotter_mapping.values():
            plotter.invalidate_cache(_)

    def notify_layers_changed(self, entities: list[ENTITY]) -> None:
        """
        Handle change in the set of entities:
        entities = [] indicates deletion
        otherwise entities were added or updated.
        """
        print("layers change:", entities)
        match entities:
            case []:
                self._handle_remove()
            case _:
                self._handle_add_update(entities)

    def _handle_add_update(self, entities: list[ENTITY]) -> None:
        """
        If entity was updated: invalidate cache.
        If entity was added: create new cached plotter + layer for new entity.
        """
        for entity in entities:
            if entity in self._layer_mapping:
                print("invalidate", entity)
                plotter: CachedPlotter = self._plotter_mapping[entity]
                plotter.invalidate_cache(None)
            else:
                print("add", entity)
                plotter = CachedPlotter(self._plotter_factory(entity), [])
                self._plotter_mapping[entity] = plotter
                self._layer_mapping[entity] = PlottingLayer(str(entity), plotter, False)

    def _handle_remove(self) -> None:
        remaining_entities = self._entity_lookup()
        print("handle remove -> remaining:", remaining_entities)

        for entity in self._layer_mapping:
            if entity not in remaining_entities:
                del self._plotter_mapping[entity]
                del self._layer_mapping[entity]
