import bisect
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Generic, Optional

from OTAnalytics.application.config import DEFAULT_TRACK_OFFSET
from OTAnalytics.application.datastore import Datastore, VideoMetadata
from OTAnalytics.application.playback import SkipTime
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import EventRepositoryEvent
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import FlowId, FlowListObserver
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.observer import VALUE, Subject
from OTAnalytics.domain.section import (
    SectionId,
    SectionListObserver,
    SectionRepositoryEvent,
    SectionType,
)
from OTAnalytics.domain.track import TrackId, TrackImage
from OTAnalytics.domain.track_repository import (
    TrackListObserver,
    TrackObserver,
    TrackRepository,
    TrackRepositoryEvent,
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

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """
        Notify the state about changes in the track list.

        Args:
            track_event (TrackRepositoryEvent): newly added or removed tracks.
        """
        track_to_select = next(iter(track_event.added)) if track_event.added else None
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
    """This state represents the information to be shown on the ui."""

    def __init__(self) -> None:
        self.background_image = ObservableOptionalProperty[TrackImage]()
        self.track_offset = ObservableOptionalProperty[RelativeOffsetCoordinate](
            DEFAULT_TRACK_OFFSET
        )
        self.filter_element = ObservableProperty[FilterElement](
            FilterElement(DateRange(None, None), None)
        )
        self.view_width = ObservableProperty[int](default=DEFAULT_WIDTH)
        self.view_height = ObservableProperty[int](default=DEFAULT_HEIGHT)
        self.selected_videos: ObservableProperty[list[Video]] = ObservableProperty[
            list[Video]
        ](default=[])
        self.skip_time = ObservableProperty[SkipTime](SkipTime(1, 1))

    def reset(self) -> None:
        """Reset to default settings."""
        self.selected_videos.set([])
        self.background_image.set(None)
        self.view_width.set(DEFAULT_WIDTH)
        self.view_height.set(DEFAULT_HEIGHT)
        self.filter_element.set(FilterElement(DateRange(None, None), None))
        self.track_offset.set(DEFAULT_TRACK_OFFSET)


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

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        all_tracks = self._datastore.get_all_tracks()
        if track_event.added:
            first_track = next(iter(all_tracks))
            if video := self._datastore.get_video_for(first_track.id):
                self._track_view_state.selected_videos.set([video])

    def notify_videos(self, videos: list[Video]) -> None:
        if videos:
            self._track_view_state.selected_videos.set([videos[0]])


class SectionState(SectionListObserver):
    """
    This state represents the currently selected sections.
    """

    def __init__(self, get_sections_by_id: GetSectionsById) -> None:
        self.selected_sections: ObservableProperty[list[SectionId]] = (
            ObservableProperty[list]([])
        )
        self._get_sections_by_id = get_sections_by_id

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        """
        Notify the state about changes in the section list.

        Args: section_event (SectionRepositoryEvent): notification about section
            repository changes.
        """
        if not section_event.added:
            self.selected_sections.set([])
            return

        no_cutting_sections = [
            section
            for section in self._get_sections_by_id(section_event.added)
            if section.get_type() != SectionType.CUTTING
        ]
        if no_cutting_sections:
            self.selected_sections.set([no_cutting_sections[0].id])
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

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """
        Will notify this object about changes in the track repository.

        Args:
            track_event (list[TrackId]): list of changed track ids
        """
        self._update_image()

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

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        self._update()

    def notify_events(self, _: EventRepositoryEvent) -> None:
        self._update()

    def _notify_flow_changed(self, _: list[FlowId]) -> None:
        self._update()

    def notify_layers(self, _: bool) -> None:
        """Will update the image

        Args:
            _ (bool): whether layer is enabled or disabled.
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
        """
        self._track_view_state.background_image.set(self._plotter.plot())


class VideosMetadata:
    def __init__(self) -> None:
        self._metadata: dict[datetime, VideoMetadata] = {}
        self._first_video_start: Optional[datetime] = None
        self._last_video_end: Optional[datetime] = None

    def update(self, metadata: VideoMetadata) -> None:
        """
        Update the stored metadata.
        """
        if metadata.start in self._metadata.keys():
            raise ValueError(
                f"metadata with start date {metadata.start} already exists."
            )
        self._metadata[metadata.start] = metadata
        self._metadata = dict(sorted(self._metadata.items()))
        self._update_start_end_by(metadata)

    def _update_start_end_by(self, metadata: VideoMetadata) -> None:
        if (not self._first_video_start) or metadata.start < self._first_video_start:
            self._first_video_start = metadata.start
        if (not self._last_video_end) or metadata.end > self._last_video_end:
            self._last_video_end = metadata.end

    def get_metadata_for(self, current: datetime) -> Optional[VideoMetadata]:
        """
        Find the metadata for the given datetime. If the datetime matches exactly a
        start time of a video, the corresponding VideoMetadata is returned. Otherwise,
        the metadata of the video containing the datetime will be returned.
        """
        if current in self._metadata:
            return self._metadata[current]
        keys = list(self._metadata.keys())
        key = bisect.bisect_left(keys, current) - 1
        metadata = self._metadata[keys[key]]
        if metadata.start <= current <= metadata.end:
            return metadata
        return None

    @property
    def first_video_start(self) -> Optional[datetime]:
        return self._first_video_start

    @property
    def last_video_end(self) -> Optional[datetime]:
        return self._last_video_end


class TracksMetadata(TrackListObserver):
    """Contains relevant information on the currently loaded tracks.

    Listens to changes in the `TrackRepository` and updates the tracks metadata

    Args:
        track_repository (TrackRepository): the track repository
    """

    def __init__(
        self,
        track_repository: TrackRepository,
        include_classes: frozenset[str] = frozenset(),
        exclude_classes: frozenset[str] = frozenset(),
    ) -> None:
        self._track_repository = track_repository
        self._include_classes = include_classes
        self._exclude_classes = exclude_classes
        self._first_detection_occurrence: ObservableOptionalProperty[datetime] = (
            ObservableOptionalProperty[datetime]()
        )
        self._last_detection_occurrence: ObservableOptionalProperty[datetime] = (
            ObservableOptionalProperty[datetime]()
        )
        self._classifications: ObservableProperty[frozenset[str]] = ObservableProperty[
            frozenset
        ](frozenset())
        self._detection_classifications: ObservableProperty[frozenset[str]] = (
            ObservableProperty[frozenset](frozenset([]))
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
    def classifications(self) -> frozenset[str]:
        """The current classifications in the track repository.

        Returns:
            set[str]: the classifications.
        """
        return self._classifications.get()

    @property
    def filtered_detection_classifications(self) -> frozenset[str]:
        """The filtered detection classifications.

        Considers include-classes and exclude-classes filter.

        Returns:
            set[str]: the classifications.
        """
        if self._include_classes:
            return self._include_classes
        elif self._exclude_classes:
            return self.detection_classifications - self._exclude_classes
        else:
            return self.detection_classifications

    @property
    def detection_classifications(self) -> frozenset[str]:
        """The classifications used by the detection model.

        Returns:
            set[str]: the classifications.
        """
        return self._detection_classifications.get()

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """Update tracks metadata on track repository changes"""
        self._update_detection_occurrences()
        self._update_classifications()

    def _update_detection_occurrences(self) -> None:
        """Update the first and last detection occurrences."""
        self._first_detection_occurrence.set(self._track_repository.first_occurrence)
        self._last_detection_occurrence.set(self._track_repository.last_occurrence)

    def _update_classifications(self) -> None:
        """Update current classifications."""
        self._classifications.set(self._track_repository.classifications)

    def update_detection_classes(self, new_classes: frozenset[str]) -> None:
        """Update the classifications used by the detection model."""
        updated_classes = self._detection_classifications.get().union(new_classes)
        self._detection_classifications.set(updated_classes)


class ActionState:
    """
    This state represents the current state of running actions.
    """

    def __init__(self) -> None:
        self.action_running = ObservableProperty[bool](False)
