from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.project import Project
from OTAnalytics.application.use_cases.export_events import (
    EventExportSpecification,
    EventListExporter,
)
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import (
    Flow,
    FlowChangedObserver,
    FlowId,
    FlowListObserver,
    FlowRepository,
)
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.remark import RemarkRepository
from OTAnalytics.domain.section import (
    Section,
    SectionChangedObserver,
    SectionId,
    SectionListObserver,
    SectionRepository,
)
from OTAnalytics.domain.track import TrackId, TrackImage
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import (
    TrackFileRepository,
    TrackListObserver,
    TrackRepository,
)
from OTAnalytics.domain.video import (
    Video,
    VideoListObserver,
    VideoMetadata,
    VideoRepository,
)


@dataclass(frozen=True)
class DetectionMetadata:
    detection_classes: frozenset[str]


@dataclass(frozen=True)
class TrackParseResult:
    tracks: TrackDataset
    detection_metadata: DetectionMetadata
    video_metadata: VideoMetadata


class TrackParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> TrackParseResult:
        raise NotImplementedError


class EventListParser(ABC):
    @abstractmethod
    def serialize(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        pass


class VideoParser(ABC):
    @abstractmethod
    def parse(self, file: Path, metadata: Optional[VideoMetadata]) -> Video:
        pass

    @abstractmethod
    def parse_list(
        self,
        content: list[dict],
        base_folder: Path,
    ) -> Sequence[Video]:
        pass

    @abstractmethod
    def convert(
        self,
        videos: Iterable[Video],
        relative_to: Path = Path("."),
    ) -> dict[str, list[dict]]:
        pass


class TrackToVideoRepository:
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

    def clear(self) -> None:
        """
        Clear the repository.
        """
        self._videos.clear()


class TrackVideoParser(ABC):
    """
    Parse the information about videos from a track file
    """

    @abstractmethod
    def parse(
        self, file: Path, track_ids: list[TrackId], metadata: VideoMetadata
    ) -> Tuple[list[TrackId], list[Video]]:
        """
        Parse the given file in ottrk format and retrieve video information from it

        Args:
            file (Path): file in ottrk format
            track_ids (list[TrackId]): track ids to get videos for
            metadata (VideoMetadata): the video metadata

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
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        track_parser: TrackParser,
        section_repository: SectionRepository,
        flow_repository: FlowRepository,
        event_repository: EventRepository,
        event_list_parser: EventListParser,
        track_to_video_repository: TrackToVideoRepository,
        video_repository: VideoRepository,
        video_parser: VideoParser,
        track_video_parser: TrackVideoParser,
        progressbar: ProgressbarBuilder,
        remark_repository: RemarkRepository,
    ) -> None:
        self._track_parser = track_parser
        self._event_list_parser = event_list_parser
        self._video_parser = video_parser
        self._track_video_parser = track_video_parser
        self._track_repository = track_repository
        self._track_file_repository = track_file_repository
        self._section_repository = section_repository
        self._flow_repository = flow_repository
        self._event_repository = event_repository
        self._video_repository = video_repository
        self._remark_repository = remark_repository
        self._track_to_video_repository = track_to_video_repository
        self._progressbar = progressbar
        self.project = Project(name="", start_date=None, metadata=None)

    def register_video_observer(self, observer: VideoListObserver) -> None:
        self._video_repository.register_videos_observer(observer)

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

    def clear_repositories(self) -> None:
        self._event_repository.clear()
        self._section_repository.clear()
        self._flow_repository.clear()
        self._track_to_video_repository.clear()
        self._track_repository.clear()
        self._video_repository.clear()

    def load_video_files(self, files: list[Path]) -> None:
        raised_exceptions: list[Exception] = []
        videos = []
        for file in files:
            try:
                videos.append(self._video_parser.parse(file, None))
            except Exception as cause:
                raised_exceptions.append(cause)
        if raised_exceptions:
            raise ExceptionGroup(
                "Errors occurred while loading the video files:",
                raised_exceptions,
            )
        self._video_repository.add_all(videos)

    def remove_videos(self, videos: list[Video]) -> None:
        """
        Remove videos from the repository.

        Args:
            videos (Video): videos to remove
        """
        self._video_repository.remove(videos)

    def register_flows_observer(self, observer: FlowListObserver) -> None:
        """
        Listen to changes in the flow repository.

        Args:
            observer (FlowListObserver): listener to be notified about changes
        """
        self._flow_repository.register_flows_observer(observer)

    def get_all_tracks(self) -> TrackDataset:
        """
        Retrieve all tracks of the repository as list.

        Returns:
            list[Track]: all tracks of the repository
        """
        return self._track_repository.get_all()

    def delete_all_tracks(self) -> None:
        """Delete all tracks in repository."""
        self._track_repository.clear()

    def get_all_sections(self) -> list[Section]:
        return self._section_repository.get_all()

    def get_section_for(self, section_id: SectionId) -> Optional[Section]:
        return self._section_repository.get(section_id)

    def get_all_flows(self) -> list[Flow]:
        return self._flow_repository.get_all()

    def get_flow_for(self, flow_id: FlowId) -> Optional[Flow]:
        return self._flow_repository.get(flow_id)

    def get_flow_id(self) -> FlowId:
        """
        Get an id for a new flow
        """
        return self._flow_repository.get_id()

    def add_flow(self, flow: Flow) -> None:
        self._flow_repository.add(flow)

    def remove_flow(self, flow_id: FlowId) -> None:
        self._flow_repository.remove(flow_id)

    def update_flow(self, flow: Flow) -> None:
        self._flow_repository.update(flow)

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

    def export_event_list_file(
        self, file: Path, event_list_exporter: EventListExporter
    ) -> None:
        """
        Export events from the event list to other formats (like CSV or Excel).

        Args:
            file (Path): File to export events to
            event_list_exporter (EventListExporter): Exporter building the format
        """
        event_list_exporter.export(
            events=self._event_repository.get_all(),
            sections=self._section_repository.get_all(),
            export_specification=EventExportSpecification(
                file=file,
                export_mode=OVERWRITE,
            ),
        )

    def is_flow_using_section(self, section: SectionId) -> bool:
        """
        Checks if the section id is used by flows.

        Args:
            section (SectionId): section to check

        Returns:
            bool: true if the section is used by at least one flow
        """
        return self._flow_repository.is_flow_using_section(section)

    def flows_using_section(self, section: SectionId) -> list[Flow]:
        """
        Returns a list of flows using the section as start or end.

        Args:
            section (SectionId): section to search flows for

        Returns:
            list[FlowId]: flows using the section
        """
        return self._flow_repository.flows_using_section(section)

    def get_section_id(self) -> SectionId:
        """
        Get an id for a new section
        """
        return self._section_repository.get_id()

    def add_section(self, section: Section) -> None:
        """
        Add a single section to the repository.

        Args:
            section (Section): section to add
        """
        self._section_repository.add(section)

    def add_events(self, events: Iterable[Event]) -> None:
        """Add multiple events to the repository.

        Args:
            events (Iterable[Event]): events to add
        """
        self._event_repository.add_all(events)

    def remove_section(self, section: SectionId) -> None:
        """
        Remove the section from the repository.

        Args:
            section (SectionId): section to remove
        """
        self._section_repository.remove(section)

    def register_section_changed_observer(
        self, observer: SectionChangedObserver
    ) -> None:
        """
        Listen to changes of sections in the repository.

        Args:
            observer (SectionChangedObserver): observer to notify about changes
        """
        self._section_repository.register_section_changed_observer(observer)

    def register_flow_changed_observer(self, observer: FlowChangedObserver) -> None:
        """
        Listen to changes of sections in the repository.

        Args:
            observer (FlowChangedObserver): observer to notify about changes
        """
        self._flow_repository.register_flow_changed_observer(observer)

    def update_section(self, section: Section) -> None:
        """
        Update the section in the repository.

        Args:
            section (Section): updated section
        """
        self._section_repository.update(section)

    def set_section_plugin_data(self, section_id: SectionId, plugin_data: dict) -> None:
        """
        Set the plugin data of the section. The data will be overridden.

        Args:
            section_id (SectionId): section id to override the plugin data at
            plugin_data (dict): value of the new plugin data
        """
        self._section_repository.set_section_plugin_data(
            section_id=section_id, plugin_data=plugin_data
        )

    def get_video_at(self, file: Path) -> Optional[Video]:
        return self._video_repository.get(file)

    def get_video_for(self, track_id: TrackId) -> Optional[Video]:
        return self._track_to_video_repository.get_video_for(track_id)

    def get_all_videos(self) -> list[Video]:
        return self._video_repository.get_all()

    def get_image_of_track(
        self,
        track_id: TrackId,
        frame: int = 0,
    ) -> Optional[TrackImage]:
        """
        Retrieve an image for the given track.

        Args:
            track_id (TrackId): identifier for the track

        Returns:
            Optional[TrackImage]: an image of the track if the track is available and
            the image can be loaded
        """
        return (
            video.get_frame(frame) if (video := self.get_video_for(track_id)) else None
        )
