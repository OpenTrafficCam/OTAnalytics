from abc import ABC, abstractmethod

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.use_cases.event_repository import (
    AddEvents,
    ClearEventRepository,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import SectionRepository


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


class SimpleCreateIntersectionEvents(CreateIntersectionEvents):
    """Intersect tracks with sections to create intersection events and add them to the
    event repository.


    Args:
        intersect (RunIntersect): use case to intersect tracks with sections
        datastore (Datastore): the datastore containing tracks, sections and events
    """

    def __init__(
        self,
        run_intersect: RunIntersect,
        section_repository: SectionRepository,
        add_events: AddEvents,
    ) -> None:
        self._run_intersect = run_intersect
        self._section_repository = section_repository
        self._add_events = add_events

    def __call__(self) -> None:
        """Runs the intersection of tracks with sections in the repository."""
        sections = self._section_repository.get_all()
        if not sections:
            return
        events = self._run_intersect(sections)
        self._add_events(events)


class SimpleCreateSceneEvents(CreateSceneEvents):
    """Create scene enter and leave events and add them to the event repository.

    Args:
        get_all_tracks (GetAllTracks): use case to get all tracks from track repository.
        scene_action_detector (SceneActionDetector): use case to detect scene events.
        add_events (AddEvents): use case to add events to event repository.
    """

    def __init__(
        self,
        get_all_tracks: GetAllTracks,
        scene_action_detector: SceneActionDetector,
        add_events: AddEvents,
    ) -> None:
        self._get_all_tracks = get_all_tracks
        self._scene_action_detector = scene_action_detector
        self._add_events = add_events

    def __call__(self) -> None:
        """Create scene enter and leave events and save them to the event repository."""
        tracks = self._get_all_tracks()
        events = self._scene_action_detector.detect(tracks)
        self._add_events(events)


class CreateEvents:
    def __init__(
        self,
        clear_event_repository: ClearEventRepository,
        create_intersection_events: CreateIntersectionEvents,
        create_scene_events: CreateSceneEvents,
    ) -> None:
        self._clear_event_repository = clear_event_repository
        self._create_intersection_events = create_intersection_events
        self._create_scene_events = create_scene_events

    def __call__(self) -> None:
        """
        Intersect all tracks with all sections and write the events into the event
        repository.
        """
        self._clear_event_repository()
        self._create_intersection_events()
        self._create_scene_events()
