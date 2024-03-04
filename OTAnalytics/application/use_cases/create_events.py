from abc import ABC, abstractmethod
from typing import Callable

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.config import CLI_CUTTING_SECTION_MARKER
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.track_repository import (
    GetTracksWithoutSingleDetections,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.section import Section, SectionRepository, SectionType


class CreateIntersectionEvents(ABC):
    """Interface defining use case to create intersection events and add them to the
    event repository.
    """

    @abstractmethod
    def __call__(self) -> None:
        raise NotImplementedError


class CreateSceneEvents(ABC):
    """
    Interface defining the use case to create scene enter and leave events and save
    them to the event repository.
    """

    @abstractmethod
    def __call__(self) -> None:
        raise NotImplementedError


SectionProvider = Callable[[], list[Section]]


class FilterOutCuttingSections:
    """
    A filter that removes cutting sections from a list of sections.

    Args:
      other (SectionProvider): The provider of the sections to be filtered.
    """

    def __init__(self, other: SectionProvider) -> None:
        self._other = other

    def __call__(self) -> list[Section]:
        """
        Returns a new list of sections without cutting sections.

        Returns:
          A list of sections, filtered out any cutting sections.
        """
        return self.filter()

    def filter(self) -> list[Section]:
        """
        Returns a new list of sections, filtered out any cutting sections.

        Returns:
          A list of sections, excluding any cutting sections.
        """
        return [
            _section
            for _section in self._other()
            if not _section.name.startswith(CLI_CUTTING_SECTION_MARKER)
            and _section.get_type() != SectionType.CUTTING
        ]


class MissingEventsSectionProvider:
    """
    Calculates the section to be intersected with. All sections which have already
    been intersected are retrieved from the event repository.

    Args:
        section_repository (SectionRepository): section repository to get all
            sections from
        event_repository (EventRepository): event repository to calculate
            the sections to intersect
    """

    def __init__(
        self, section_repository: SectionRepository, event_repository: EventRepository
    ):
        self._section_repository = section_repository
        self._event_repository = event_repository

    def __call__(self) -> list[Section]:
        all = self._section_repository.get_all()
        return self._event_repository.retain_missing(all)


class SimpleCreateIntersectionEvents(CreateIntersectionEvents):
    """Intersect tracks with sections to create intersection events and add them to the
    event repository.


    Args:
        run_intersect (RunIntersect): use case to intersect tracks with sections
        datastore (Datastore): the datastore containing tracks, sections and events
    """

    def __init__(
        self,
        run_intersect: RunIntersect,
        section_provider: SectionProvider,
        add_events: AddEvents,
    ) -> None:
        self._run_intersect = run_intersect
        self._section_provider = section_provider
        self._add_events = add_events

    def __call__(self) -> None:
        """Runs the intersection of tracks with sections in the repository."""
        sections = self._section_provider()
        if not sections:
            return
        events = self._run_intersect(sections)
        section_ids = [section.id for section in sections]
        self._add_events(events, section_ids)


class SimpleCreateSceneEvents(CreateSceneEvents):
    """Create scene enter and leave events and add them to the event repository.

    Args:
        get_tracks (GetTracksWithoutSingleDetections): use case to get tracks with at
          least two detections from track repository.
        scene_action_detector (SceneActionDetector): use case to detect scene events.
        add_events (AddEvents): use case to add events to event repository.
    """

    def __init__(
        self,
        get_tracks: GetTracksWithoutSingleDetections,
        scene_action_detector: SceneActionDetector,
        add_events: AddEvents,
    ) -> None:
        self._get_tracks = get_tracks
        self._scene_action_detector = scene_action_detector
        self._add_events = add_events

    def __call__(self) -> None:
        """Create scene enter and leave events and save them to the event repository."""
        tracks = self._get_tracks.as_dataset()
        events = self._scene_action_detector.detect(tracks)
        self._add_events(events)


class CreateEvents:
    def __init__(
        self,
        clear_all_events: ClearAllEvents,
        create_intersection_events: CreateIntersectionEvents,
        create_scene_events: CreateSceneEvents,
    ) -> None:
        self._clear_event_repository = clear_all_events
        self._create_intersection_events = create_intersection_events
        self._create_scene_events = create_scene_events

    def __call__(self) -> None:
        """
        Intersect all tracks with all sections and write the events into the event
        repository.
        """
        self._create_intersection_events()
        self._create_scene_events()
