from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Generic, Iterable, Optional, TypeVar

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import SectionId, SectionListObserver
from OTAnalytics.domain.track import (
    Detection,
    TrackId,
    TrackImage,
    TrackListObserver,
    TrackObserver,
    TrackRepository,
    TrackSubject,
)
from OTAnalytics.domain.video import Video

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600


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


class Subject(Generic[VALUE]):
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[Callable[[VALUE], None]] = set()

    def register(self, observer: Callable[[VALUE], None]) -> None:
        """
        Listen to events.

        Args:
            observer (Observer[VALUE]): listener to add
        """
        self.observers.add(observer)

    def notify(self, value: VALUE) -> None:
        """
        Notifies observers about the changed value.

        Args:
            value (Optional[VALUE]): changed value
        """
        [observer(value) for observer in self.observers]


class ObservableProperty(Generic[VALUE]):
    """
    Represents a property of the given type that informs its observers about
    changes.
    """

    def __init__(self, default: VALUE) -> None:
        self._property: VALUE = default
        self._subject: Subject[VALUE] = Subject[VALUE]()

    def register(self, observer: Callable[[VALUE], None]) -> None:
        """
        Listen to property changes.

        Args:
            observer (Observer[VALUE]): observer to be notified about changes
        """
        self._subject.register(observer)

    def set(self, value: VALUE) -> None:
        """
        Change the current value of the property

        Args:
            value (VALUE): new value to be set
        """
        if self._property != value:
            self._property = value
            self._subject.notify(value)

    def get(self) -> VALUE:
        """
        Get the current value of the property.

        Returns:
            VALUE: current value
        """
        return self._property


class ObservableOptionalProperty(Generic[VALUE]):
    """
    Represents an optional property of the given type that informs its observers about
    changes.
    """

    def __init__(self, default: Optional[VALUE] = None) -> None:
        self._property: Optional[VALUE] = default
        self._subject: Subject[Optional[VALUE]] = Subject[Optional[VALUE]]()

    def register(self, observer: Callable[[Optional[VALUE]], None]) -> None:
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

    def get_or_default(self, default: VALUE) -> VALUE:
        """
        Get the current value if present. Otherwise return the given default value.

        Args:
            default (VALUE): value to return in absence of the property value

        Returns:
            VALUE: value or default value
        """
        return self._property if self._property else default


class TrackViewState:
    """
    This state represents the information to be shown on the ui.

    Args:
        filter_element_state (FilterElementState): the filter element state
    """

    def __init__(self) -> None:
        self.background_image = ObservableOptionalProperty[TrackImage]()
        self.show_tracks = ObservableOptionalProperty[bool]()
        self.track_offset = ObservableOptionalProperty[RelativeOffsetCoordinate](
            RelativeOffsetCoordinate(0, 0)
        )
        self.filter_element = ObservableProperty[FilterElement](
            FilterElement(DateRange(None, None), [])
        )
        self.view_width = ObservableProperty[int](default=DEFAULT_WIDTH)
        self.view_height = ObservableProperty[int](default=DEFAULT_HEIGHT)
        self.selected_video: ObservableOptionalProperty[
            Video
        ] = ObservableOptionalProperty[Video]()


class TrackPropertiesUpdater:
    """
    This class listens to track changes and updates the width and height of the view
    state.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state

    def notify_video(self, video: Optional[Video]) -> None:
        if video:
            image = video.get_frame(0)
            self._track_view_state.view_width.set(image.width())
            self._track_view_state.view_height.set(image.height())


class Plotter(ABC):
    """Abstraction to plot the background image."""

    @abstractmethod
    def plot(self) -> Optional[TrackImage]:
        pass


class SelectedVideoUpdate(TrackListObserver):
    def __init__(self, datastore: Datastore, track_view_state: TrackViewState) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        all_tracks = self._datastore.get_all_tracks()
        if tracks:
            video = self._datastore.get_video_for(all_tracks[0].id)
            self._track_view_state.selected_video.set(video)


class TrackImageUpdater(TrackListObserver):
    """
    This class listens to track changes in the repository and updates the background
    image. It takes into account whether the tracks and sections should be shown or not.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        plotter: Plotter,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._plotter = plotter
        self._track_view_state.selected_video.register(self.notify_video)
        self._track_view_state.show_tracks.register(self._notify_show_tracks)
        self._track_view_state.track_offset.register(self._notify_track_offset)
        self._track_view_state.filter_element.register(self._notify_filter_element)

    def notify_video(self, video: Optional[Video]) -> None:
        """
        Will notify this object about changes in the video repository.

        Args:
            video (list[Video]): list of changed video ids

        Raises:
            IndexError: if the list is empty
        """
        self._update_image()

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
        self._update_image()

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
            offset (Optional[RelativeOffsetCoordinate]): current value
        """
        self._update()

    def _notify_filter_element(self, _: FilterElement) -> None:
        """
        Will update the image according to changes of the filter element.

        Args:
            _ (FilterElement): current filter element
        """
        self._update()

    def _update(self) -> None:
        """
        Update the image if at least one track is available.
        """
        self._update_image()

    def _update_image(self) -> None:
        """
        Updates the current background image with or without tracks and sections.

        Args:
            track_id (TrackId): track id used to get the video image
        """
        self._track_view_state.background_image.set(self._plotter.plot())


class SectionState(SectionListObserver):
    """
    This state represents the currently selected section.
    """

    def __init__(self) -> None:
        self.selected_section = ObservableOptionalProperty[SectionId]()
        self.selected_flow = ObservableOptionalProperty[str]()

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
        self.selected_flow.set(None)


class TracksMetadata(TrackListObserver):
    """Contains relevant information on the currently loaded tracks.

    Listens to changes in the `TrackRepository` and updates the tracks metadata

    Args:
        TrackListObserver (TracListObserver): extends the TrackListObserver interface
        track_repository (TrackRepository): the track repository
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository
        self._first_detection_occurrence: ObservableOptionalProperty[
            datetime
        ] = ObservableOptionalProperty[datetime]()
        self._last_detection_occurrence: ObservableOptionalProperty[
            datetime
        ] = ObservableOptionalProperty[datetime]()

    @property
    def first_detection_occurrence(self) -> Optional[datetime]:
        """The track's first detection occurrence in the track repository.

        Returns:
            Optional[datetime]: first detection occurrence. `None` if track repository
                is empty.
        """
        return self._first_detection_occurrence.get()

    @property
    def last_detection_occurrence(self) -> Optional[datetime]:
        """The track's last detection occurrence in the track repository.

        Returns:
            Optional[datetime]: last detection occurrence. `None` if track repository
                is empty.
        """
        return self._last_detection_occurrence.get()

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """Update tracks metadata on track repository changes"""
        self._update_detection_occurrences()

    def _update_detection_occurrences(self) -> None:
        """Update the first and last detection occurrences."""
        sorted_detections = sorted(
            self._get_all_track_detections(), key=lambda x: x.occurrence
        )
        self._first_detection_occurrence.set(sorted_detections[0].occurrence)
        self._last_detection_occurrence.set(sorted_detections[-1].occurrence)

    def _get_all_track_detections(self) -> Iterable[Detection]:
        """Get all track detections in the track repository.

        Returns:
            Iterable[Detection]: the track detections.
        """
        detections: list[Detection] = []

        for track in self._track_repository.get_all():
            detections.extend(track.detections)

        return detections
