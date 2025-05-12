from typing import Iterable

from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import (
    SectionId,
    SectionListObserver,
    SectionRepositoryEvent,
)
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent
from OTAnalytics.domain.types import EventType


class AddEvents:
    """Add events to the repository."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def __call__(
        self, events: Iterable[Event], sections: list[SectionId] | None = None
    ) -> None:
        if sections is None:
            sections = []
        if events:
            self._event_repository.add_all(events, sections)


class ClearAllEvents(SectionListObserver, TrackListObserver):
    """Clears the event repository also on section state changes.

    Args:
        event_repository (EventRepository): the event repository
    """

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def __call__(self) -> None:
        self.clear()

    def clear(self) -> None:
        self._event_repository.clear()

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        self._event_repository.remove(list(section_event.removed))

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        self.clear()

    def on_section_changed(self, section_id: SectionId) -> None:
        self._event_repository.remove([section_id])

    def on_tracks_cut(self, _: CutTracksDto) -> None:
        self.clear()


class GetAllEnterSectionEvents:
    """Get all enter section events from the event repository"""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def get(self) -> Iterable[Event]:
        return self._event_repository.get(event_types=[EventType.SECTION_ENTER])


class RemoveEventsByRoadUserId(TrackListObserver):
    """
    Use case to handle the removal of events associated with specific road user IDs.

    This class is responsible for interacting with an `EventRepository` to manage
    the deletion of events that are linked to one or multiple road user IDs.

    Args:
        event_repository (EventRepository): The repository instance that implements data
            access operations for events.
    """

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def remove_multiple(self, road_user_ids: Iterable[TrackId]) -> None:
        """
        Removes multiple road user events associated with the given road user IDs.

        This method interacts with the event repository to remove all events
        associated with the provided road user IDs.

        Args:
            road_user_ids (Iterable[TrackId]): A collection of road user IDs whose
                events should be removed.
        """
        self._event_repository.remove_events_by_road_user_ids(road_user_ids)

    def notify_tracks(self, event: TrackRepositoryEvent) -> None:
        self.remove_multiple(event.removed)
