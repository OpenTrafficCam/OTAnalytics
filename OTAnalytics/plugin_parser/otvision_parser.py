import bz2
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

import ujson

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.application.datastore import (
    EventListParser,
    SectionParser,
    TrackParser,
    Video,
    VideoParser,
    VideoReader,
)
from OTAnalytics.domain import event, geometry, section
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

ENCODING: str = "UTF-8"


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
    ) -> None:
        super().__init__(track_classification_calculator, track_repository)

    def parse(self, ottrk_file: Path) -> list[Track]:
        """Parse ottrk file and convert its content to domain level objects namely
        `Track`s.

        Args:
            ottrk_file (Path): the file to

        Returns:
            list[Track]: the tracks.
        """
        ottrk_dict = _parse_bz2(ottrk_file)
        dets_list: list[dict] = ottrk_dict[ottrk_format.DATA][ottrk_format.DETECTIONS]
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

    def parse(self, file: Path) -> list[Section]:
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
        return sections

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
                section.START,
                section.END,
            ],
        )
        section_id = self._parse_section_id(data)
        relative_offset_coordinates = self._parse_relative_offset_coordinates(data)
        start = self._parse_coordinate(data[section.START])
        end = self._parse_coordinate(data[section.END])
        plugin_data = self._parse_plugin_data(data)
        return LineSection(
            section_id, relative_offset_coordinates, plugin_data, start, end
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
        content = self._convert(sections)
        _write_json(content, file)

    def _convert(self, sections: Iterable[Section]) -> dict[str, list[dict]]:
        """Convert sections into dictionary.

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of sections
        """
        return {section.SECTIONS: [section.to_dict() for section in sections]}


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
    ) -> dict[str, list[dict]]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert
            sections (Iterable[Section]): sections to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of events
        """
        converted_sections = self._convert_sections(sections)
        converted_events = self._convert_events(events)
        return {
            section.SECTIONS: converted_sections,
            event.EVENT_LIST: converted_events,
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
