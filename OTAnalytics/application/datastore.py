from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import Section, SectionListObserver, SectionRepository
from OTAnalytics.domain.track import (
    Track,
    TrackClassificationCalculator,
    TrackId,
    TrackImage,
    TrackListObserver,
    TrackRepository,
)


class TrackParser(ABC):
    def __init__(
        self, track_classification_calculator: TrackClassificationCalculator
    ) -> None:
        self._track_classification_calculator = track_classification_calculator

    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


class SectionParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Section]:
        pass

    @abstractmethod
    def serialize(self, sections: Iterable[Section], file: Path) -> None:
        pass


class EventListParser(ABC):
    @abstractmethod
    def serialize(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        pass


class VideoReader(ABC):
    @abstractmethod
    def get_frame(self, video: Path, index: int) -> TrackImage:
        """Get frame of `video` at `index`.

        Args:
            video (Path): the path to the video file.
            index (int): the index of the frame to get.

        Returns:
            TrackImage: the frame.
        """
        pass


@dataclass(frozen=True)
class Video:
    """Represents a video file.

    Args:
        video_reader (VideoReader): A video reader used to get frames.
        path (Path): the video file path.

    Raises:
        ValueError: if video file path does not exist.
    """

    video_reader: VideoReader
    path: Path

    def __post_init__(self) -> None:
        self.check_path_exists()

    def check_path_exists(self) -> None:
        if not self.path.exists():
            raise ValueError("must be an existing path")

    def get_frame(self, index: int) -> TrackImage:
        """Returns the frame of the video at `index`.

        Args:
            index (int): the index of the frame to get.

        Returns:
            TrackImage: the frame.
        """
        return self.video_reader.get_frame(self.path, index)


class VideoRepository:
    """
    Repository containing the videos per track.
    """

    def __init__(self) -> None:
        self._videos: dict[TrackId, Video] = {}

    def add(self, track_id: TrackId, video: Video) -> None:
        """
        Add a video for a track id.

        Args:
            track_id (TrackId): id of the track
            video (Video): video containing the track
        """
        self._videos[track_id] = video

    def add_all(self, track_ids: Iterable[TrackId], videos: Iterable[Video]) -> None:
        """
        Add all videos for all tracks.

        Args:
            track_ids (Iterable[TrackId]): track ids to be added
            videos (Iterable[Video]): videos per track id to be added
        """
        for track_id, video in zip(track_ids, videos):
            self.add(track_id, video)

    def get_video_for(self, track_id: TrackId) -> Optional[Video]:
        """
        Retrieve a video for the given track id.

        Args:
            track_id (TrackId): id of the track to get a video for

        Returns:
            Optional[Video]: video of the track if a video exists for the track
        """
        return self._videos.get(track_id)


class VideoParser(ABC):
    """
    Parse the information about videos from a track file
    """

    @abstractmethod
    def parse(
        self, file: Path, track_ids: list[TrackId]
    ) -> Tuple[list[TrackId], list[Video]]:
        """
        Parse the given file in ottrk format and retrieve video information from it

        Args:
            file (Path): file in ottrk format
            track_ids (list[TrackId]): track ids to get videos for

        Returns:
            Tuple[list[TrackId], list[Video]]: track ids and the corresponding videos
        """
        pass


class Datastore:
    """
    Central element to hold data in the application.
    """

    def __init__(
        self,
        track_parser: TrackParser,
        section_parser: SectionParser,
        event_list_parser: EventListParser,
        video_parser: VideoParser,
    ) -> None:
        self._track_parser = track_parser
        self._section_parser = section_parser
        self._event_list_parser = event_list_parser
        self._video_parser = video_parser
        self._track_repository = TrackRepository()
        self._section_repository = SectionRepository()
        self._event_repository = EventRepository()
        self._video_repository = VideoRepository()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        """
        Listen to changes in the track repository.

        Args:
            observer (TrackListObserver): listener to be notified about changes
        """
        self._track_repository.register_tracks_observer(observer)

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        """
        Listen to changes in the section repository.

        Args:
            observer (SectionListObserver): listener to be notified about changes
        """
        self._section_repository.register_sections_observer(observer)

    def load_track_file(self, file: Path) -> None:
        """
        Load and parse the given track file together with the corresponding video file.

        Args:
            file (Path): file in ottrk format
        """
        tracks = self._track_parser.parse(file)
        track_ids = [track.id for track in tracks]
        track_ids, videos = self._video_parser.parse(file, track_ids)
        self._video_repository.add_all(track_ids, videos)
        self._track_repository.add_all(tracks)

    def delete_all_tracks(self) -> None:
        """Delete all tracks in repository."""
        self._track_repository.delete_all()

    def load_section_file(self, file: Path) -> None:
        """
        Load sections from the given files and store them in the section repository.

        Args:
            file (Path): file to load sections from
        """
        sections = self._section_parser.parse(file)
        self._section_repository.add_all(sections)

    def save_section_file(self, file: Path) -> None:
        """
        Save sections from the repository in a section file.

        Args:
            file (Path): file to save sections to
        """
        self._section_parser.serialize(
            self._section_repository.get_all(),
            file=file,
        )

    def get_all_sections(self) -> Iterable[Section]:
        return self._section_repository.get_all()

    def save_event_list_file(self, file: Path) -> None:
        """
        Save events from the event list in an event file.

        Args:
            file (Path): file to save events to
        """
        self._event_list_parser.serialize(
            self._event_repository.get_all(),
            self._section_repository.get_all(),
            file=file,
        )

    def add_section(self, section: Section) -> None:
        """
        Add a single section to the repository.

        Args:
            section (Section): section to add
        """
        self._section_repository.add(section)

    def get_image_of_track(self, track_id: TrackId) -> Optional[TrackImage]:
        """
        Retrieve an image for the given track.

        Args:
            track_id (TrackId): identifier for the track

        Returns:
            Optional[TrackImage]: an image of the track if the track is available and
            the image can be loaded
        """
        if video := self._video_repository.get_video_for(track_id):
            return video.get_frame(0)
        return None
