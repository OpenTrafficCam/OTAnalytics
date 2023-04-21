from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, Optional, TypeVar

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId, SectionListObserver
from OTAnalytics.domain.track import (
    Track,
    TrackId,
    TrackImage,
    TrackListObserver,
    TrackObserver,
    TrackSubject,
)


class TrackState(TrackListObserver):
    """
    This state represents the currently selected track.
    """

    def __init__(self) -> None:
        self.selected_track: Optional[TrackId] = None
        self.observers: TrackSubject = TrackSubject()

    def register(self, observer: TrackObserver) -> None:
        """
        Listen to changes of the currently selected track.

        Args:
            observer (TrackObserver): listener to be notified about changes
        """
        self.observers.register(observer)

    def select(self, track_id: TrackId) -> None:
        """
        Select the given track.

        Args:
            track_id (TrackId): track to be selected
        """
        if self.selected_track != track_id:
            self.selected_track = track_id
            self._notify_observers()

    def _notify_observers(self) -> None:
        """
        Notify observers about the currently selected track.
        """
        self.observers.notify(self.selected_track)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """
        Notify the state about changes in the track list.

        Args:
            tracks (list[TrackId]): newly added tracks

        Raises:
            IndexError: if the list of tracks is empty
        """
        if not tracks:
            raise IndexError("No tracks to select")
        self.select(tracks[0])


VALUE = TypeVar("VALUE")
Observer = Callable[[Optional[VALUE]], None]


class Subject(Generic[VALUE]):
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[Observer[VALUE]] = set()

    def register(self, observer: Observer[VALUE]) -> None:
        """
        Listen to events.

        Args:
            observer (Observer[VALUE]): listener to add
        """
        self.observers.add(observer)

    def notify(self, value: Optional[VALUE]) -> None:
        """
        Notifies observers about the changed value.

        Args:
            value (Optional[VALUD]): changed value
        """
        [observer(value) for observer in self.observers]


class ObservableProperty(Generic[VALUE]):
    """
    Represents a property of the given type that informs its observers about changes.
    """

    def __init__(self, default: Optional[VALUE] = None) -> None:
        self._property: Optional[VALUE] = default
        self._subject: Subject[VALUE] = Subject[VALUE]()

    def register(self, observer: Observer[VALUE]) -> None:
        """
        Listen to property changes.

        Args:
            observer (Observer[VALUE]): observer to be notified about changes
        """
        self._subject.register(observer)

    def set(self, value: Optional[VALUE]) -> None:
        """
        Change the current value of the property

        Args:
            value (Optional[VALUE]): new value to be set
        """
        if self._property != value:
            self._property = value
            self._subject.notify(value)

    def get(self) -> Optional[VALUE]:
        """
        Get the current value of the property.

        Returns:
            Optional[VALUE]: current value
        """
        return self._property


class TrackViewState:
    """
    This state represents the information to be shown on the ui.
    """

    def __init__(self) -> None:
        self.background_image = ObservableProperty[TrackImage]()
        self.show_tracks = ObservableProperty[bool]()
        self.track_offset = ObservableProperty[RelativeOffsetCoordinate](
            RelativeOffsetCoordinate(0, 0)
        )


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


class TrackImageUpdater(TrackListObserver):
    """
    This class listens to track changes in the repository and updates the background
    image. It takes into account whether the tracks and sections should be shown or not.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        track_plotter: TrackPlotter,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._track_plotter = track_plotter
        self._track_view_state.show_tracks.register(self._notify_show_tracks)
        self._track_view_state.track_offset.register(self._notify_track_offset)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """
        Will notify this object about changes in the track repository.

        Args:
            tracks (list[TrackId]): list of changed track ids

        Raises:
            IndexError: if the list is empty
        """
        if not tracks:
            raise IndexError("No tracks changed")
        self._update_image(tracks[0])

    def _notify_show_tracks(self, show_tracks: Optional[bool]) -> None:
        """
        Will update the image according to changes of the show tracks property.

        Args:
            show_tracks (Optional[bool]): current value
        """
        self._update()

    def _notify_track_offset(self, offset: Optional[RelativeOffsetCoordinate]) -> None:
        """
        Will update the image according to changes of the track offset property.

        Args:
            offset (Optional[RelativeOffsetCoordinate]): curren value
        """
        self._update()

    def _update(self) -> None:
        """
        Update the image if at least one track is available.
        """
        if track := next(iter(self._datastore.get_all_tracks())):
            self._update_image(track.id)

    def _update_image(self, track_id: TrackId) -> None:
        """
        Updates the current background image with or without tracks and sections.

        Args:
            track_id (TrackId): track id used to get the video image
        """
        if new_image := self._datastore.get_image_of_track(track_id):
            if self._track_view_state.show_tracks.get():
                track_image = self._track_plotter.plot(
                    self._datastore.get_all_tracks(),
                    self._datastore.get_all_sections(),
                    width=new_image.width(),
                    height=new_image.height(),
                    offset=self._track_view_state.track_offset.get(),
                )
                combined_image = new_image.add(track_image)
                self._track_view_state.background_image.set(combined_image)
            else:
                self._track_view_state.background_image.set(new_image)


class SectionState(SectionListObserver):
    """
    This state represents the currently selected section.
    """

    def __init__(self) -> None:
        self.selected_section = ObservableProperty[SectionId]()

    def notify_sections(self, sections: list[SectionId]) -> None:
        """
        Notify the state about changes in the section list.

        Args:
            sections (list[SectionId]): newly added sections

        Raises:
            IndexError: if the list of sections is empty
        """
        if not sections:
            raise IndexError("No section to select")
        self.selected_section.set(sections[0])
