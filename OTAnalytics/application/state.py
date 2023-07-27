from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Generic, Iterable, Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import FlowId, FlowListObserver
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.observer import VALUE, Subject
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
from OTAnalytics.domain.video import Video, VideoListObserver

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

    def select(self, track_id: TrackId | None) -> None:
        """
        Select the given track.

        Args:
            track_id (TrackId | None): track to be selected
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
        """
        track_to_select = tracks[0] if tracks else None
        self.select(track_to_select)


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
            RelativeOffsetCoordinate(0.5, 0.5)
        )
        self.filter_element = ObservableProperty[FilterElement](
            FilterElement(DateRange(None, None), None)
        )
        self.view_width = ObservableProperty[int](default=DEFAULT_WIDTH)
        self.view_height = ObservableProperty[int](default=DEFAULT_HEIGHT)
        self.selected_videos: ObservableProperty[list[Video]] = ObservableProperty[
            list[Video]
        ](default=[])


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

    def notify_videos(self, video: list[Video]) -> None:
        if video:
            image = video[0].get_frame(0)
            self._track_view_state.view_width.set(image.width())
            self._track_view_state.view_height.set(image.height())


class Plotter(ABC):
    """Abstraction to plot the background image."""

    @abstractmethod
    def plot(self) -> Optional[TrackImage]:
        pass


class SelectedVideoUpdate(TrackListObserver, VideoListObserver):
    def __init__(self, datastore: Datastore, track_view_state: TrackViewState) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        all_tracks = self._datastore.get_all_tracks()
        if tracks:
            if video := self._datastore.get_video_for(all_tracks[0].id):
                self._track_view_state.selected_videos.set([video])

    def notify_videos(self, videos: list[Video]) -> None:
        if videos:
            self._track_view_state.selected_videos.set([videos[0]])


class SectionState(SectionListObserver):
    """
    This state represents the currently selected sections.
    """

    def __init__(self) -> None:
        self.selected_sections: ObservableProperty[
            list[SectionId]
        ] = ObservableProperty[list]([])

    def notify_sections(self, sections: list[SectionId]) -> None:
        """
        Notify the state about changes in the section list.

        Args:
            sections (list[SectionId]): newly added sections
        """
        if sections:
            self.selected_sections.set([sections[0]])
        else:
            self.selected_sections.set([])


class FlowState(FlowListObserver):
    """
    This state represents the currently selected flows.
    """

    def __init__(self) -> None:
        self.selected_flows: ObservableProperty[list[FlowId]] = ObservableProperty[
            list
        ]([])

    def notify_flows(self, flows: list[FlowId]) -> None:
        """
        Notify the state about changes in the flow list.

        Args:
            flows (list[FlowId]): newly added flows

        Raises:
            IndexError: if the list of flows is empty
        """
        if flows:
            self.selected_flows.set([flows[0]])
        else:
            self.selected_flows.set([])


class TrackImageUpdater(TrackListObserver, SectionListObserver):
    """
    This class listens to track changes in the repository and updates the background
    image. It takes into account whether the tracks and sections should be shown or not.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        section_state: SectionState,
        flow_state: FlowState,
        plotter: Plotter,
    ) -> None:
        self._datastore = datastore
        self._track_view_state = track_view_state
        self._section_state = section_state
        self._flow_state = flow_state
        self._plotter = plotter
        self._track_view_state.show_tracks.register(self._notify_show_tracks)
        self._track_view_state.track_offset.register(self._notify_track_offset)
        self._track_view_state.filter_element.register(self._notify_filter_element)
        self._section_state.selected_sections.register(self._notify_section_selection)
        self._flow_state.selected_flows.register(self._notify_flow_changed)

    def notify_video(self, video: list[Video]) -> None:
        """
        Will notify this object about changes in the video repository.

        Args:
            video (list[Video]): list of changed video ids
        """
        self._update_image()

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """
        Will notify this object about changes in the track repository.

        Args:
            tracks (list[TrackId]): list of changed track ids
        """
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

    def _notify_section_selection(self, _: list[SectionId]) -> None:
        """Will update the image according to changes of the selected section.

        Args:
            _ (list[SectionId]): current selected section
        """
        self._update()

    def notify_section_changed(self, _: SectionId) -> None:
        self._update()

    def notify_sections(self, sections: list[SectionId]) -> None:
        self._update()

    def _notify_flow_changed(self, _: list[FlowId]) -> None:
        self._update()

    def notify_layers(self, _: bool) -> None:
        """Will update the image

        Args:
            _ (bool): wether layer is enabled or disabled.
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
        self._classifications: ObservableProperty[set[str]] = ObservableProperty[set](
            set()
        )

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

    @property
    def classifications(self) -> set[str]:
        """The current classifications in the track repository.

        Returns:
            set[str]: the classifications.
        """
        return self._classifications.get()

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """Update tracks metadata on track repository changes"""
        self._update_detection_occurrences()
        self._update_classifications(tracks)

    def _update_detection_occurrences(self) -> None:
        """Update the first and last detection occurrences."""
        sorted_detections = sorted(
            self._get_all_track_detections(), key=lambda x: x.occurrence
        )
        if sorted_detections:
            self._first_detection_occurrence.set(sorted_detections[0].occurrence)
            self._last_detection_occurrence.set(sorted_detections[-1].occurrence)

    def _update_classifications(self, new_tracks: list[TrackId]) -> None:
        """Update current classifications."""
        updated_classifications = self._classifications.get().copy()
        if (updated_classifications := self._classifications.get()) is None:
            updated_classifications = set()

        for track_id in new_tracks:
            if track := self._track_repository.get_for(track_id):
                updated_classifications.add(track.classification)
        self._classifications.set(updated_classifications)

    def _get_all_track_detections(self) -> Iterable[Detection]:
        """Get all track detections in the track repository.

        Returns:
            Iterable[Detection]: the track detections.
        """
        detections: list[Detection] = []

        for track in self._track_repository.get_all():
            detections.extend(track.detections)

        return detections


class ActionState:
    """
    This state represents the current state of running actions.
    """

    def __init__(self) -> None:
        self.action_running = ObservableProperty[bool](False)
