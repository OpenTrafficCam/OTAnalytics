import bz2
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Tuple

import ujson

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics import version
from OTAnalytics.application.datastore import (
    EventListParser,
    SectionParser,
    TrackParser,
    Video,
    VideoParser,
    VideoReader,
)
from OTAnalytics.domain import event, flow, geometry, section
from OTAnalytics.domain.event import Event, EventType
from OTAnalytics.domain.flow import Flow
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
from OTAnalytics.plugin_parser import dataformat_versions

ENCODING: str = "UTF-8"
METADATA: str = "metadata"
VERSION: str = "version"
SECTION_FORMAT_VERSION: str = "section_file_version"
EVENT_FORMAT_VERSION: str = "event_file_version"


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
        ujson.dump(data, file)


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


VERSION_1_0: Version = Version(1, 0)
VERSION_1_1: Version = Version(1, 1)
VERSION_1_2: Version = Version(1, 2)


class DetectionFixer(ABC):
    def __init__(
        self,
        from_otdet_version: Version,
        to_otdet_version: Version,
    ) -> None:
        self._from_otdet_version: Version = from_otdet_version
        self._to_otdet_version: Version = to_otdet_version

    def from_version(self) -> Version:
        return self._from_otdet_version

    def to_version(self) -> Version:
        return self._to_otdet_version

    @abstractmethod
    def fix(self, detection: dict, current_version: Version) -> dict:
        pass


class Version_1_0_to_1_1(DetectionFixer):
    def __init__(self) -> None:
        super().__init__(VERSION_1_0, VERSION_1_0)

    def fix(
        self,
        detection: dict,
        otdet_format_version: Version,
    ) -> dict:
        return self.__fix_bounding_box(detection, otdet_format_version)

    def __fix_bounding_box(
        self,
        detection: dict,
        otdet_format_version: Version,
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
        if otdet_format_version <= self.to_version():
            x = x_input - w / 2
            y = y_input - h / 2
            detection[ottrk_format.X] = x
            detection[ottrk_format.Y] = y
        return detection


class Version_1_1_To_1_2(DetectionFixer):
    def __init__(self) -> None:
        super().__init__(VERSION_1_0, VERSION_1_2)

    def fix(self, detection: dict, current_version: Version) -> dict:
        return self.__fix_occurrence(detection, current_version)

    def __fix_occurrence(self, detection: dict, otdet_format_version: Version) -> dict:
        """This method converts the old datetime format of otdet format version
        <= 1.1.

        Args:
            content (dict): dictionary containing detection information

        Returns:
            dict: fixed dictionary
        """
        if otdet_format_version <= Version(1, 1):
            occurrence = datetime.strptime(
                detection[ottrk_format.OCCURRENCE], ottrk_format.DATE_FORMAT
            )
            detection[ottrk_format.OCCURRENCE] = str(occurrence.timestamp())
        return detection


ALL_FIXES = [Version_1_0_to_1_1(), Version_1_1_To_1_2()]


class OttrkFormatFixer:
    def __init__(self, detection_fixes: list[DetectionFixer] = ALL_FIXES) -> None:
        self._detection_fixes: list[DetectionFixer] = detection_fixes

    def fix(self, content: dict) -> dict:
        """Fix formate changes from older ottrk and otdet format versions to the
        current version.

        Args:
            content (dict): ottrk file content

        Returns:
            dict: fixed ottrk file content
        """
        version = self.__parse_otdet_version(content)
        return self.__fix_detections(content, version)

    def __parse_otdet_version(self, content: dict) -> Version:
        """Parse the otdet format version from the input.

        Args:
            content (dict): ottrk file content

        Returns:
            Version: otdet format version
        """
        version = content[ottrk_format.METADATA][ottrk_format.OTDET_VERSION]
        return Version.from_str(version)

    def __fix_detections(self, content: dict, current_otdet_version: Version) -> dict:
        detections = content[ottrk_format.DATA][ottrk_format.DETECTIONS]
        fixed_detections: list[dict] = []
        for detection in detections:
            fixed_detection = detection
            for fixer in self._detection_fixes:
                fixed_detection = fixer.fix(detection, current_otdet_version)
            fixed_detections.append(fixed_detection)
        content[ottrk_format.DATA][ottrk_format.DETECTIONS] = fixed_detections
        return content


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
        self._path_cache: dict[str, Path] = {}

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
            path = self.__get_path(det_dict)
            det = Detection(
                classification=det_dict[ottrk_format.CLASS],
                confidence=det_dict[ottrk_format.CONFIDENCE],
                x=det_dict[ottrk_format.X],
                y=det_dict[ottrk_format.Y],
                w=det_dict[ottrk_format.W],
                h=det_dict[ottrk_format.H],
                frame=det_dict[ottrk_format.FRAME],
                occurrence=datetime.fromtimestamp(
                    float(det_dict[ottrk_format.OCCURRENCE])
                ),
                input_file_path=path,
                interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
                track_id=TrackId(det_dict[ottrk_format.TRACK_ID]),
            )
            if not tracks_dict.get(det.track_id):
                tracks_dict[det.track_id] = []

            tracks_dict[det.track_id].append(det)  # Group detections by track id
        return tracks_dict

    def __get_path(self, det_dict: dict) -> Path:
        path_as_string = det_dict[ottrk_format.INPUT_FILE_PATH]
        if path_as_string in self._path_cache:
            return self._path_cache[path_as_string]
        path = Path(path_as_string)
        self._path_cache[path_as_string] = path
        return path


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

    def parse(self, file: Path) -> tuple[list[Section], list[Flow]]:
        """Parse the content of the file into Section objects.

        Args:
            file (Path): path to section file

        Returns:
            list[Section]: list of Section objects
        """
        content: dict = _parse(file)
        sections: list[Section] = [
            self.parse_section(entry) for entry in content.get(section.SECTIONS, [])
        ]
        flows: list[Flow] = []
        return sections, flows

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

    def serialize(
        self,
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
    ) -> None:
        """Serialize sections into file.

        Args:
            sections (Iterable[Section]): sections to serialize
            file (Path): file to serialize sections to
        """
        content = self._convert(sections, flows)
        _write_json(content, file)

    def _convert(
        self,
        sections: Iterable[Section],
        flows: Iterable[Flow],
    ) -> dict[str, list[dict]]:
        """Convert sections into dictionary.

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of sections
        """
        return {
            section.SECTIONS: [section.to_dict() for section in sections],
            flow.FLOWS: [flow.to_dict() for flow in flows],
        }


class OttrkVideoParser(VideoParser):
    def __init__(self, video_reader: VideoReader) -> None:
        self._video_reader = video_reader

    def parse(
        self, file: Path, track_ids: list[TrackId]
    ) -> Tuple[list[TrackId], list[Video]]:
        content = _parse_bz2(file)
        metadata = content[ottrk_format.METADATA][ottrk_format.VIDEO]
        video_file = metadata[ottrk_format.FILENAME] + metadata[ottrk_format.FILETYPE]
        video_file_path = Video(self._video_reader, file.parent / video_file)
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
