import bz2
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence, Tuple

import ujson

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics import version
from OTAnalytics.application.datastore import (
    ConfigParser,
    EventListParser,
    OtConfig,
    SectionParser,
    TrackParser,
    TrackVideoParser,
    VideoParser,
)
from OTAnalytics.domain import event, geometry, section, video
from OTAnalytics.domain.event import Event, EventType
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import Area, LineSection, Section, SectionId
from OTAnalytics.domain.track import (
    BuildTrackWithLessThanNDetectionsError,
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
    TrackRepository,
)
from OTAnalytics.domain.video import PATH, Video, VideoReader
from OTAnalytics.plugin_parser import dataformat_versions

ENCODING: str = "UTF-8"
METADATA: str = "metadata"
VERSION: str = "version"
SECTION_FORMAT_VERSION: str = "section_file_version"
EVENT_FORMAT_VERSION: str = "event_file_version"

PROJECT: str = "project"
NAME: str = "name"


def _parse_bz2(path: Path) -> dict:
    """Parse JSON bz2.

    Args:
        path (Path): Path to bz2 JSON.

    Returns:
        dict: The content of the JSON file.
    """
    with bz2.open(path, "rt", encoding=ENCODING) as file:
        return ujson.load(file)


def _write_bz2(data: dict, path: Path) -> None:
    """Serialize JSON bz2.

    Args:
        dict: The content of the JSON file.
        path (Path): Path to bz2 JSON.
    """
    with bz2.open(path, "wt", encoding=ENCODING) as file:
        ujson.dump(data, file)


def _parse_json(path: Path) -> dict:
    """Parse JSON.

    Args:
        path (Path): Path to JSON.

    Returns:
        dict: The content of the JSON file.
    """
    with open(path, "rt", encoding=ENCODING) as file:
        return ujson.load(file)


def _parse(path: Path) -> dict:
    """Parse file as JSON or bzip2 compressed JSON.

    Args:
        path (Path): Path to file

    Returns:
        dict: The content of the JSON file.
    """
    try:
        return _parse_json(path)
    except UnicodeDecodeError:
        return _parse_bz2(path)


def _write_json(data: dict, path: Path) -> None:
    """Serialize JSON.

    Args:
        dict: The content of the JSON file.
        path (Path): Path to JSON.
    """
    with open(path, "wt", encoding=ENCODING) as file:
        ujson.dump(data, file, indent=4)


class IncorrectVersionFormat(Exception):
    pass


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int

    @staticmethod
    def from_str(version_string: str) -> "Version":
        splitted = version_string.split(".")
        if len(splitted) < 2:
            message = (
                "Version must contain major and minor separated by '.' "
                + f"but was {version_string}"
            )
            raise IncorrectVersionFormat(message)
        minor = int(splitted[1])
        major = int(splitted[0])
        return Version(major=major, minor=minor)


class OttrkFormatFixer:
    def fix(self, content: dict) -> dict:
        """Fix formate changes from older ottrk and otdet format versions to the
        current version.

        Args:
            content (dict): ottrk file content

        Returns:
            dict: fixed ottrk file content
        """
        version = self.__parse_otdet_version(content)
        return self.__fix_bounding_boxes(content, version)

    def __parse_otdet_version(self, content: dict) -> Version:
        """Parse the otdet format version from the input.

        Args:
            content (dict): ottrk file content

        Returns:
            Version: otdet format version
        """
        version = content[ottrk_format.METADATA][ottrk_format.OTDET_VERSION]
        return Version.from_str(version)

    def __fix_bounding_boxes(
        self, content: dict, otdet_format_version: Version
    ) -> dict:
        """Fix all bounding boxes of detections.

        Args:
            content (dict): ottrk file content
            otdet_format_version (Version): otdet format version

        Returns:
            dict: fixed ottrk file content
        """
        detections = content[ottrk_format.DATA][ottrk_format.DETECTIONS]
        fixed_detections: list[dict] = []
        for detection in detections:
            fixed_detection = self.__fix_bounding_box(detection, otdet_format_version)
            fixed_detections.append(fixed_detection)
        content[ottrk_format.DATA][ottrk_format.DETECTIONS] = fixed_detections
        return content

    def __fix_bounding_box(
        self, detection: dict, otdet_format_version: Version
    ) -> dict:
        """This method fixes different coordinate formats of otdet format version
        <= 1.0.

        Args:
            content (dict): dictionary containing detection information

        Returns:
            dict: fixed dictionary
        """
        x_input = detection[ottrk_format.X]
        y_input = detection[ottrk_format.Y]
        w = detection[ottrk_format.W]
        h = detection[ottrk_format.H]
        if otdet_format_version <= Version(1, 0):
            x = x_input - w / 2
            y = y_input - h / 2
            detection[ottrk_format.X] = x
            detection[ottrk_format.Y] = y
        return detection


class OttrkParser(TrackParser):
    """Parse an ottrk file and convert its contents to our domain objects namely
    `Tracks`.

    Args:
        TrackParser (TrackParser): extends TrackParser interface.
    """

    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_repository: TrackRepository,
        format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
    ) -> None:
        super().__init__(track_classification_calculator, track_repository)
        self._format_fixer = format_fixer

    def parse(self, ottrk_file: Path) -> list[Track]:
        """Parse ottrk file and convert its content to domain level objects namely
        `Track`s.

        Args:
            ottrk_file (Path): the file to

        Returns:
            list[Track]: the tracks.
        """
        ottrk_dict = _parse_bz2(ottrk_file)
        fixed_ottrk = self._format_fixer.fix(ottrk_dict)
        dets_list: list[dict] = fixed_ottrk[ottrk_format.DATA][ottrk_format.DETECTIONS]
        return self._parse_tracks(dets_list)

    def _parse_tracks(self, dets: list[dict]) -> list[Track]:
        """Parse the detections of ottrk located at ottrk["data"]["detections"].

        This method will also sort the detections belonging to a track by their
        occurrence.

        Args:
            dets (list[dict]): the detections in dict format.

        Returns:
            list[Track]: the tracks.
        """
        tracks_dict = self._parse_detections(dets)
        tracks: list[Track] = []
        for track_id, detections in tracks_dict.items():
            existing_detections = self._get_existing_detections(track_id)
            all_detections = existing_detections + detections
            sort_dets_by_occurrence = sorted(
                all_detections, key=lambda det: det.occurrence
            )
            classification = self._track_classification_calculator.calculate(detections)
            try:
                current_track = Track(
                    id=track_id,
                    classification=classification,
                    detections=sort_dets_by_occurrence,
                )
                tracks.append(current_track)
            except BuildTrackWithLessThanNDetectionsError as build_error:
                # TODO: log error
                # Skip tracks with less than 2 detections
                print(build_error)

        return tracks

    def _get_existing_detections(self, track_id: TrackId) -> list[Detection]:
        """
        Returns the detections of an already existing track with the same id or
        an empty list

        Args:
            track_id (TrackId): track id to search for

        Returns:
            list[Detection]: detections of the already existing track or an empty list
        """
        if existing_track := self._track_repository.get_for(track_id):
            return existing_track.detections
        return []

    def _parse_detections(self, det_list: list[dict]) -> dict[TrackId, list[Detection]]:
        """Convert dict to Detection objects and group them by their track id."""
        tracks_dict: dict[TrackId, list[Detection]] = {}
        for det_dict in det_list:
            det = Detection(
                classification=det_dict[ottrk_format.CLASS],
                confidence=det_dict[ottrk_format.CONFIDENCE],
                x=det_dict[ottrk_format.X],
                y=det_dict[ottrk_format.Y],
                w=det_dict[ottrk_format.W],
                h=det_dict[ottrk_format.H],
                frame=det_dict[ottrk_format.FRAME],
                occurrence=datetime.strptime(
                    det_dict[ottrk_format.OCCURRENCE], ottrk_format.DATE_FORMAT
                ),
                input_file_path=Path(det_dict[ottrk_format.INPUT_FILE_PATH]),
                interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
                track_id=TrackId(det_dict[ottrk_format.TRACK_ID]),
            )
            if not tracks_dict.get(det.track_id):
                tracks_dict[det.track_id] = []

            tracks_dict[det.track_id].append(det)  # Group detections by track id
        return tracks_dict


class UnknownSectionType(Exception):
    """
    This exception indicates unknown types in section files.
    """

    pass


class InvalidSectionData(Exception):
    """
    This exception indicates invalid data when parsing a section file.
    """


class OtsectionParser(SectionParser):
    """
    Parse a section file and convert its content to domain objects namely
    LineSection, Area and Coordinate.

    Args:
        SectionParser (SectionParser): extends SectionParser interface
    """

    def parse(self, file: Path) -> Sequence[Section]:
        """Parse the content of the file into Section objects.

        Args:
            file (Path): path to section file

        Returns:
            list[Section]: list of Section objects
        """
        content: dict = _parse(file)
        return self.parse_list(content.get(section.SECTIONS, []))

    def parse_list(self, content: list[dict]) -> Sequence[Section]:
        return [self.parse_section(entry) for entry in content]

    def parse_section(self, entry: dict) -> Section:
        """Parse sections by type.

        Args:
            entry (dict): content of section file

        Raises:
            UnknownSectionType: if the type of a section is unknown

        Returns:
            Section: section of parsed type
        """
        match (entry.get(section.TYPE)):
            case section.LINE:
                return self._parse_line_section(entry)
            case section.AREA:
                return self._parse_area_section(entry)
        raise UnknownSectionType()

    def _parse_line_section(self, data: dict) -> Section:
        """Parse data to line section.

        Args:
            data (dict): data to parse to line section

        Returns:
            Section: line section
        """
        self._validate_data(
            data,
            attributes=[
                section.ID,
                section.RELATIVE_OFFSET_COORDINATES,
            ],
        )
        section_id = self._parse_section_id(data)
        relative_offset_coordinates = self._parse_relative_offset_coordinates(data)
        coordinates = self._parse_coordinates(data)
        plugin_data = self._parse_plugin_data(data)
        return LineSection(
            section_id, relative_offset_coordinates, plugin_data, coordinates
        )

    def _parse_section_id(self, data: dict) -> SectionId:
        return SectionId(data[section.ID])

    def _validate_data(self, data: dict, attributes: list[str]) -> None:
        """Validate attributes of dictionary.

        Args:
            data (dict): dictionary to validate
            attributes (list[str]): attributes that must exist

        Raises:
            InvalidSectionData: if an attribute is missing
        """
        for attribute in attributes:
            if attribute not in data.keys():
                raise InvalidSectionData(f"{attribute} attribute is missing")

    def _parse_area_section(self, data: dict) -> Section:
        """Parse data to area section.

        Args:
            data (dict): data to parse to area section

        Returns:
            Section: area section
        """
        self._validate_data(data, attributes=[section.ID, section.COORDINATES])
        section_id = self._parse_section_id(data)
        relative_offset_coordinates = self._parse_relative_offset_coordinates(data)
        coordinates = self._parse_coordinates(data)
        plugin_data = self._parse_plugin_data(data)
        return Area(section_id, relative_offset_coordinates, plugin_data, coordinates)

    def _parse_coordinates(self, data: dict) -> list[Coordinate]:
        """Parse data to coordinates.

        Args:
            data (dict): data to parse to coordinates

        Returns:
            list[Coordinate]: coordinates
        """
        return [self._parse_coordinate(entry) for entry in data[section.COORDINATES]]

    def _parse_coordinate(self, data: dict) -> Coordinate:
        """Parse data to coordinate.

        Args:
            data (dict): data to parse to coordinate

        Returns:
            Coordinate: coordinate
        """
        self._validate_data(data, attributes=[geometry.X, geometry.Y])
        return Coordinate(
            x=data.get(geometry.X, 0),
            y=data.get(geometry.Y, 0),
        )

    def _parse_relative_offset_coordinates(
        self, data: dict
    ) -> dict[EventType, RelativeOffsetCoordinate]:
        """Parse data to relative offset coordinates.

        Args:
            data (dict): data to parse to relative offset coordinates

        Returns:
            dict[EventType, RelativeOffsetCoordinate]: relative offset coordinates
        """
        return {
            EventType.parse(event_type): self._parse_relative_offset(offset)
            for event_type, offset in data[section.RELATIVE_OFFSET_COORDINATES].items()
        }

    def _parse_relative_offset(self, data: dict) -> RelativeOffsetCoordinate:
        """Parse data to relative offset coordinate.

        Args:
            data (dict): data to parse to relative offset coordinate

        Returns:
            RelativeOffsetCoordinate: the relative offset coordinate
        """
        self._validate_data(data, attributes=[geometry.X, geometry.Y])
        return RelativeOffsetCoordinate(
            x=data.get(geometry.X, 0),
            y=data.get(geometry.Y, 0),
        )

    def _parse_plugin_data(self, data: dict) -> dict:
        """Parse plugin data if there is an entry in the data dict.

        Args:
            data (dict): the dictionary containing the plugin_data at key
                `section.PLUGIN_DATA`

        Returns:
            dict: the plugin data
        """
        return data.get(section.PLUGIN_DATA, {})

    def serialize(self, sections: Iterable[Section], file: Path) -> None:
        """Serialize sections into file.

        Args:
            sections (Iterable[Section]): sections to serialize
            file (Path): file to serialize sections to
        """
        content = self.convert(sections)
        _write_json(content, file)

    def convert(self, sections: Iterable[Section]) -> dict[str, list[dict]]:
        """Convert sections into dictionary.

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of sections
        """
        return {section.SECTIONS: [section.to_dict() for section in sections]}


class MissingPath(Exception):
    pass


class SimpleVideoParser(VideoParser):
    def __init__(self, video_reader: VideoReader) -> None:
        self._video_reader = video_reader

    def parse(self, file: Path) -> Video:
        return Video(self._video_reader, file)

    def parse_list(
        self,
        content: list[dict],
        base_folder: Path,
    ) -> Sequence[Video]:
        return [self.__create_video(video, base_folder) for video in content]

    def __create_video(
        self,
        entry: dict,
        base_folder: Path,
    ) -> Video:
        if PATH not in entry:
            raise MissingPath(entry)
        video_path = Path(base_folder, entry[PATH])
        return Video(self._video_reader, video_path)

    def convert(
        self,
        videos: Iterable[Video],
        relative_to: Path = Path("."),
    ) -> dict[str, list[dict]]:
        return {
            video.VIDEOS: [video.to_dict(relative_to=relative_to) for video in videos]
        }


class OttrkVideoParser(TrackVideoParser):
    def __init__(self, video_parser: VideoParser) -> None:
        self._video_parser = video_parser

    def parse(
        self, file: Path, track_ids: list[TrackId]
    ) -> Tuple[list[TrackId], list[Video]]:
        content = _parse_bz2(file)
        metadata = content[ottrk_format.METADATA][ottrk_format.VIDEO]
        video_file = metadata[ottrk_format.FILENAME] + metadata[ottrk_format.FILETYPE]
        video_file_path = self._video_parser.parse(file.parent / video_file)
        return track_ids, [video_file_path] * len(track_ids)


class OtEventListParser(EventListParser):
    def serialize(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        """Serialize event list into file.

        Args:
            events (Iterable[Event]): events to serialize
            sections (Section): sections to serialize
            file (Path): file to serialize events and sections to
        """
        content = self._convert(events, sections)
        _write_bz2(content, file)

    def _convert(
        self, events: Iterable[Event], sections: Iterable[Section]
    ) -> dict[str, Any]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert
            sections (Iterable[Section]): sections to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of events
        """
        metadata = self._build_metadata()
        converted_sections = self._convert_sections(sections)
        converted_events = self._convert_events(events)
        return {
            METADATA: metadata,
            section.SECTIONS: converted_sections,
            event.EVENT_LIST: converted_events,
        }

    def _build_metadata(self) -> dict:
        return {
            VERSION: version.__version__,
            SECTION_FORMAT_VERSION: dataformat_versions.otsection_version(),
            EVENT_FORMAT_VERSION: dataformat_versions.otevent_version(),
        }

    def _convert_events(self, events: Iterable[Event]) -> list[dict]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert

        Returns:
            list[dict]: list containing raw information of events
        """
        return [event.to_dict() for event in events]

    def _convert_sections(self, sections: Iterable[Section]) -> list[dict]:
        """Convert sections to dictionary

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            list[dict]: list containing raw information of sections
        """
        return [section.to_dict() for section in sections]


class OtConfigParser(ConfigParser):
    def __init__(
        self,
        video_parser: VideoParser,
        section_parser: SectionParser,
    ) -> None:
        self._video_parser = video_parser
        self._section_parser = section_parser

    def parse(self, file: Path) -> OtConfig:
        base_folder = file.parent
        content = _parse(file)
        project_name = content[PROJECT][NAME]
        videos = self._video_parser.parse_list(content[video.VIDEOS], base_folder)
        sections = self._section_parser.parse_list(content[section.SECTIONS])
        return OtConfig(project_name=project_name, videos=videos, sections=sections)

    def serialize(
        self,
        project_name: str,
        video_files: Iterable[Video],
        sections: Iterable[Section],
        file: Path,
    ) -> None:
        parent_folder = file.parent
        project_content = {NAME: project_name}
        video_content = self._video_parser.convert(
            video_files,
            relative_to=parent_folder,
        )
        section_content = self._section_parser.convert(sections)
        content: dict[str, list[dict] | dict] = {PROJECT: project_content}
        content |= video_content
        content |= section_content
        _write_json(data=content, path=file)
