from abc import ABC, abstractmethod
from typing import Iterable

from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class RunIntersect(ABC):
    """
    Interface defining the use case to intersect the given tracks with the given
    sections
    """

    @abstractmethod
    def run(self, track: Iterable[Track], sections: Iterable[Section]) -> list[Event]:
        raise NotImplementedError


class RunSceneEventDetection:
    def __init__(self, scene_action_detector: SceneActionDetector) -> None:
        self._scene_action_detector = scene_action_detector

    def run(self, tracks: Iterable[Track]) -> list[Event]:
        return self._scene_action_detector.detect(tracks)
