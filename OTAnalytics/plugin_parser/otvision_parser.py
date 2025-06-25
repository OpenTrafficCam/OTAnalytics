from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence, Tuple

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics import version
from OTAnalytics.application.config import (
    ALLOWED_TRACK_SIZE_PARSING,
    TRACK_LENGTH_LIMIT,
)
from OTAnalytics.application.datastore import (
    DetectionMetadata,
    EventListParser,
    TrackParser,
    TrackParseResult,
    TrackVideoParser,
    VideoParser,
)
from OTAnalytics.application.logger import logger
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.domain import event, flow, geometry, section, video
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.event import Event, EventType
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import Area, LineSection, Section, SectionId
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackHasNoDetectionError,
    TrackId,
    TrackImage,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
)
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.video import (
    PATH,
    SimpleVideo,
    Video,
    VideoMetadata,
    VideoReader,
)
from OTAnalytics.plugin_datastore.python_track_store import (
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_parser import dataformat_versions
from OTAnalytics.plugin_parser.json_parser import (
    parse_json,
    parse_json_bz2,
    write_json,
    write_json_bz2,
)

ENCODING: str = "UTF-8"
METADATA: str = "metadata"
VERSION: str = "version"
SECTION_FORMAT_VERSION: str = "section_file_version"
EVENT_FORMAT_VERSION: str = "event_file_version"

TrackIdGenerator = Callable[[str], TrackId]


def _validate_data(data: dict, attributes: list[str]) -> None:
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


@dataclass(frozen=True)
class FormatVersions:
    ottrk: Version
    otdet: Version


VERSION_OF_FORMAT = Callable[[FormatVersions], Version]


def version_of_ottrk(versions: FormatVersions) -> Version:
    return versions.ottrk


def version_of_otdet(versions: FormatVersions) -> Version:
    return versions.otdet


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


class MetadataFixer(ABC):
    def __init__(
        self,
        from_version: Version,
        to_version: Version,
        version_of_format: VERSION_OF_FORMAT,
    ) -> None:
        self._from_version: Version = from_version
        self._to_version: Version = to_version
        self._version_extractor = version_of_format

    def from_version(self) -> Version:
        return self._from_version

    def to_version(self) -> Version:
        return self._to_version

    def fix(self, metadata: dict, versions: FormatVersions) -> dict:
        return self._fix(metadata, current_version=self._version_extractor(versions))

    @abstractmethod
    def _fix(
        self,
        metadata: dict,
        current_version: Version,
    ) -> dict:
        pass


class Otdet_Version_1_0_to_1_1(DetectionFixer):
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


class Otdet_Version_1_0_To_1_2(DetectionFixer):
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
        if otdet_format_version < self.to_version():
            occurrence = datetime.strptime(
                detection[ottrk_format.OCCURRENCE], ottrk_format.DATE_FORMAT
            ).replace(tzinfo=timezone.utc)
            detection[ottrk_format.OCCURRENCE] = str(occurrence.timestamp())
        return detection


class Ottrk_Version_1_0_To_1_1(MetadataFixer):
    def __init__(self) -> None:
        super().__init__(VERSION_1_0, VERSION_1_1, version_of_ottrk)

    def _fix(self, metadata: dict, current_version: Version) -> dict:
        return self.__fix_tracking_run_ids(metadata, current_version)

    def __fix_tracking_run_ids(self, metadata: dict, current_version: Version) -> dict:
        if current_version < self.to_version():
            metadata[ottrk_format.TRACKING][ottrk_format.TRACKING_RUN_ID] = "legacy"
            metadata[ottrk_format.TRACKING][ottrk_format.FRAME_GROUP] = "legacy"
        return metadata


class Otdet_Version_1_1_To_1_2(MetadataFixer):
    def __init__(self) -> None:
        super().__init__(VERSION_1_1, VERSION_1_2, version_of_otdet)

    def _fix(self, metadata: dict, current_version: Version) -> dict:
        return self.__fix_recorded_start_date(metadata, current_version)

    def __fix_recorded_start_date(
        self, metadata: dict, current_version: Version
    ) -> dict:
        """
        Fix datetime of recorded start date in video metadata
        from date string to timestamp.
        """
        if current_version < self.to_version():
            recorded_start_date = metadata[ottrk_format.VIDEO][
                ottrk_format.RECORDED_START_DATE
            ]
            try:
                date = datetime.strptime(
                    recorded_start_date, ottrk_format.DATE_FORMAT
                ).replace(tzinfo=timezone.utc)
                metadata[ottrk_format.VIDEO][ottrk_format.RECORDED_START_DATE] = str(
                    date.timestamp()
                )
            except (ValueError, TypeError):
                # just for safety in case there are both
                # file with timestamp and date string in prior versions
                metadata[ottrk_format.VIDEO][ottrk_format.RECORDED_START_DATE] = float(
                    recorded_start_date
                )
        return metadata


ALL_DETECTION_FIXES: list[DetectionFixer] = [
    Otdet_Version_1_0_to_1_1(),
    Otdet_Version_1_0_To_1_2(),
]
ALL_METADATA_FIXES: list[MetadataFixer] = [
    Ottrk_Version_1_0_To_1_1(),
    Otdet_Version_1_1_To_1_2(),
]


class OttrkFormatFixer:
    def __init__(
        self,
        detection_fixes: list[DetectionFixer] = ALL_DETECTION_FIXES,
        metadata_fixes: list[MetadataFixer] = ALL_METADATA_FIXES,
    ) -> None:
        self._detection_fixes = detection_fixes
        self._metadata_fixes = metadata_fixes

    def fix(self, content: dict) -> dict:
        """Fix formate changes from older ottrk and otdet format versions to the
        current version.

        Args:
            content (dict): ottrk file content

        Returns:
            dict: fixed ottrk file content
        """
        otdet_version = self.__parse_otdet_version(content)
        content = self.__fix_metadata(content)
        return self.__fix_detections(content, otdet_version)

    def __parse_otdet_version(self, content: dict) -> Version:
        """Parse the otdet format version from the input.

        Args:
            content (dict): ottrk file content

        Returns:
            Version: otdet format version
        """
        version = content[ottrk_format.METADATA][ottrk_format.OTDET_VERSION]
        return Version.from_str(version)

    def __fix_metadata(self, content: dict) -> dict:
        content[ottrk_format.METADATA] = self.fix_metadata(
            metadata=content[ottrk_format.METADATA]
        )
        return content

    def fix_metadata(self, metadata: dict) -> dict:
        """
        Fix formate changes from older ottrk metadata
        format versions to the current version.
        """
        current_ottrk_version = Version.from_str(metadata[ottrk_format.OTTRK_VERSION])
        current_otdet_version = Version.from_str(metadata[ottrk_format.OTDET_VERSION])
        formatVersions = FormatVersions(current_ottrk_version, current_otdet_version)

        for fixer in self._metadata_fixes:
            metadata = fixer.fix(metadata, formatVersions)
        return metadata

    def __fix_detections(self, content: dict, current_otdet_version: Version) -> dict:
        detections = content[ottrk_format.DATA][ottrk_format.DATA_DETECTIONS]
        fixed_detections: list[dict] = []
        for detection in detections:
            fixed_detection = detection
            for fixer in self._detection_fixes:
                fixed_detection = fixer.fix(detection, current_otdet_version)
            fixed_detections.append(fixed_detection)
        content[ottrk_format.DATA][ottrk_format.DATA_DETECTIONS] = fixed_detections
        return content


class DetectionParser(ABC):
    """Parse the detections of an ottrk file and convert them into a `TrackDataset`."""

    @abstractmethod
    def parse_tracks(
        self,
        detections: list[dict],
        metadata_video: dict,
        input_file: str,
        id_generator: TrackIdGenerator = TrackId,
    ) -> TrackDataset:
        """Parse the detections.

        This method will also sort the detections belonging to a track by their
        occurrence.

        Args:
            detections (list[dict]): the detections in dict format.
            metadata_video (dict): metadata of the track file in dict format.
            input_file (Path): path to the input file containing the detections.
            id_generator (TrackIdGenerator): generator used to create track ids.

        Returns:
            TrackDataset: the tracks.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class TrackLengthLimit(DataclassValidation):
    lower_bound: int
    upper_bound: int

    def _validate(self) -> None:
        if self.lower_bound < 0:
            raise ValueError(
                f"Lower bound of track length limit must be greater than or equal to 0 "
                f"but is {self.lower_bound}"
            )
        if self.upper_bound <= self.lower_bound:
            raise ValueError(
                f"Upper bound of track length limit must be greater than to lower bound"
                f" ({self.lower_bound} but is {self.upper_bound}"
            )

    def __str__(self) -> str:
        return f"lower bound: {self.lower_bound}, upper bound: {self.upper_bound}"


DEFAULT_TRACK_LENGTH_LIMIT = TrackLengthLimit(
    ALLOWED_TRACK_SIZE_PARSING,
    TRACK_LENGTH_LIMIT,
)


def parse_python_detection(
    metadata_video: dict,
    id_generator: TrackIdGenerator,
    det_dict: dict,
    input_file: str,
) -> PythonDetection:
    """Convert dict to Detection object."""
    return PythonDetection(
        _classification=det_dict[ottrk_format.CLASS],
        _confidence=det_dict[ottrk_format.CONFIDENCE],
        _x=det_dict[ottrk_format.X],
        _y=det_dict[ottrk_format.Y],
        _w=det_dict[ottrk_format.W],
        _h=det_dict[ottrk_format.H],
        _frame=det_dict[ottrk_format.FRAME],
        _occurrence=datetime.fromtimestamp(
            float(det_dict[ottrk_format.OCCURRENCE]), tz=timezone.utc
        ),
        _interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
        _track_id=id_generator(str(det_dict[ottrk_format.TRACK_ID])),
        _video_name=metadata_video[ottrk_format.FILENAME]
        + metadata_video[ottrk_format.FILETYPE],
        _input_file=input_file,
    )


def create_python_track(
    track_id: TrackId,
    all_detections: list[Detection],
    track_classification_calculator: TrackClassificationCalculator,
    track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
) -> PythonTrack | None:
    track_length = len(all_detections)
    if track_length_limit.lower_bound <= track_length <= track_length_limit.upper_bound:
        sort_dets_by_occurrence = sorted(all_detections, key=lambda det: det.occurrence)
        classification = track_classification_calculator.calculate(all_detections)
        try:
            current_track = PythonTrack(
                _original_id=track_id,
                _id=track_id,
                _classification=classification,
                _detections=sort_dets_by_occurrence,
            )
            return current_track
        except TrackHasNoDetectionError as build_error:
            # Skip tracks with no detections
            logger().warning(build_error)

    else:
        logger().debug(
            f"Trying to construct track (track_id={track_id}). "
            f"Number of detections ({track_length} detections) is outside "
            f"the allowed bounds ({track_length_limit})."
        )

    return None


class PythonDetectionParser(DetectionParser):
    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_repository: TrackRepository,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
    ):
        self._track_repository = track_repository
        self._track_geometry_factory = track_geometry_factory
        self._path_cache: dict[str, Path] = {}
        self._track_classification_calculator = track_classification_calculator
        self._track_length_limit = track_length_limit

    def parse_tracks(
        self,
        dets: list[dict],
        metadata_video: dict,
        input_file: str,
        id_generator: TrackIdGenerator = TrackId,
    ) -> TrackDataset:
        tracks_dict = self._parse_track_detections(
            det_list=dets,
            metadata_video=metadata_video,
            input_file=input_file,
            id_generator=id_generator,
        )
        tracks: list[Track] = []

        for track_id, detections in tracks_dict.items():
            existing_detections = self._get_existing_detections(track_id)
            all_detections = detections + existing_detections
            current_track = create_python_track(
                track_id,
                all_detections,
                self._track_classification_calculator,
                self._track_length_limit,
            )
            if current_track is not None:
                tracks.append(current_track)

        return PythonTrackDataset.from_list(
            tracks,
            self._track_geometry_factory,
            self._track_classification_calculator,
        )

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

    def _parse_track_detections(
        self,
        det_list: list[dict],
        metadata_video: dict,
        input_file: str,
        id_generator: TrackIdGenerator,
    ) -> dict[TrackId, list[Detection]]:
        """
        Convert list of dict to Detection objects
        and group them by their track id.
        """
        tracks_dict: dict[TrackId, list[Detection]] = {}
        for det_dict in det_list:
            det = parse_python_detection(
                metadata_video, id_generator, det_dict, input_file
            )

            if not tracks_dict.get(det.track_id):
                tracks_dict[det.track_id] = []
            tracks_dict[det.track_id].append(det)  # Group detections by track id

        return tracks_dict


class OttrkParser(TrackParser):
    """Parse an ottrk file and convert its contents to our domain objects namely
    `Tracks`.

    Args:
        detection_parser (DetectionParser): parses the given detections.
        format_fixer (OttrkFormatFixer): to fix older ottrk version files.
    """

    def __init__(
        self,
        detection_parser: DetectionParser,
        format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
    ) -> None:
        self._detection_parser = detection_parser
        self._format_fixer = format_fixer

    def parse(self, ottrk_file: Path) -> TrackParseResult:
        """Parse ottrk file and convert its content to domain level objects namely
        `Track`s.

        Args:
            ottrk_file (Path): the track file.

        Returns:
            TrackParseResult: contains tracks and track metadata.
        """
        ottrk_dict = parse_json_bz2(ottrk_file)
        fixed_ottrk = self._format_fixer.fix(ottrk_dict)
        dets_list: list[dict] = fixed_ottrk[ottrk_format.DATA][
            ottrk_format.DATA_DETECTIONS
        ]
        metadata_video = ottrk_dict[ottrk_format.METADATA][ottrk_format.VIDEO]
        video_metadata = self.parse_video_metadata(metadata_video)
        id_generator = self.create_id_generator_from(ottrk_dict[ottrk_format.METADATA])
        tracks = self._detection_parser.parse_tracks(
            dets_list, metadata_video, str(ottrk_file), id_generator
        )
        detection_metadata = self.parse_metadata(ottrk_dict[ottrk_format.METADATA])
        return TrackParseResult(tracks, detection_metadata, video_metadata)

    @classmethod
    def parse_video_metadata(cls, metadata_video: dict) -> VideoMetadata:
        video_path = (
            metadata_video[ottrk_format.FILENAME]
            + metadata_video[ottrk_format.FILETYPE]
        )
        recorded_start_date = datetime.fromtimestamp(
            float(metadata_video[ottrk_format.RECORDED_START_DATE]), timezone.utc
        )
        expected_duration = (
            timedelta(seconds=metadata_video[ottrk_format.EXPECTED_DURATION])
            if ottrk_format.EXPECTED_DURATION in metadata_video.keys()
            else None
        )
        recorded_fps = float(metadata_video[ottrk_format.RECORDED_FPS])
        actual_fps = (
            float(metadata_video[ottrk_format.ACTUAL_FPS])
            if ottrk_format.ACTUAL_FPS in metadata_video.keys()
            else None
        )
        number_of_frames = int(metadata_video[ottrk_format.NUMBER_OF_FRAMES])
        return VideoMetadata(
            path=video_path,
            recorded_start_date=recorded_start_date,
            expected_duration=expected_duration,
            recorded_fps=recorded_fps,
            actual_fps=actual_fps,
            number_of_frames=number_of_frames,
        )

    @classmethod
    def create_id_generator_from(cls, metadata: dict) -> TrackIdGenerator:
        tracking_metadata: dict = metadata[ottrk_format.TRACKING]
        tracking_run_id = tracking_metadata[ottrk_format.TRACKING_RUN_ID]
        frame_group = tracking_metadata[ottrk_format.FRAME_GROUP]
        return lambda id: TrackId(f"{tracking_run_id}#{frame_group}#{id}")

    @classmethod
    def parse_metadata(cls, metadata_detection: dict) -> DetectionMetadata:
        detection_classes_entry: dict[str, str] = metadata_detection[
            ottrk_format.METADATA_DETECTION
        ][ottrk_format.MODEL][ottrk_format.CLASSES]
        detection_classes = frozenset(
            classification for classification in detection_classes_entry.values()
        )
        return DetectionMetadata(detection_classes)


class UnknownSectionType(Exception):
    """
    This exception indicates unknown types in section files.
    """

    pass


class InvalidSectionData(Exception):
    """
    This exception indicates invalid data when parsing a section file.
    """

    pass


class OtFlowParser(FlowParser):
    """
    Parse a flow file and convert its content to domain objects namely
    Flow, LineSection, Area and Coordinate.

    Args:
        FlowParser (FlowParser): extends FlowParser interface
    """

    def parse(self, file: Path) -> tuple[Sequence[Section], Sequence[Flow]]:
        """Parse the content of the file into Flow and Section objects.

        Args:
            file (Path): path to flow file

        Returns:
            list[Section]: list of Section objects
            list[Flow]: list of Flow objects
        """
        content: dict = parse_json(file)
        section_content = content.get(section.SECTIONS, [])
        flow_content = content.get(flow.FLOWS, [])
        return self.parse_content(section_content, flow_content)

    def parse_content(
        self,
        section_content: list[dict],
        flow_content: list[dict],
    ) -> tuple[Sequence[Section], Sequence[Flow]]:
        sections = [self.parse_section(entry) for entry in section_content]
        flows = [self.parse_flow(entry) for entry in flow_content]
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
        _validate_data(
            data,
            attributes=[
                section.ID,
                section.RELATIVE_OFFSET_COORDINATES,
            ],
        )
        section_id = self._parse_section_id(data)
        name = self._parse_name(data)
        relative_offset_coordinates = self._parse_relative_offset_coordinates(data)
        coordinates = self._parse_coordinates(data)
        plugin_data = self._parse_plugin_data(data)
        return LineSection(
            section_id, name, relative_offset_coordinates, plugin_data, coordinates
        )

    def _parse_section_id(self, data: dict) -> SectionId:
        return SectionId(data[section.ID])

    def _parse_name(self, data: dict) -> str:
        _id = data[section.ID]
        return data.get(section.NAME, _id)

    def _parse_area_section(self, data: dict) -> Section:
        """Parse data to area section.

        Args:
            data (dict): data to parse to area section

        Returns:
            Section: area section
        """
        _validate_data(data, attributes=[section.ID, section.COORDINATES])
        section_id = self._parse_section_id(data)
        name = self._parse_name(data)
        relative_offset_coordinates = self._parse_relative_offset_coordinates(data)
        coordinates = self._parse_coordinates(data)
        plugin_data = self._parse_plugin_data(data)
        return Area(
            section_id, name, relative_offset_coordinates, plugin_data, coordinates
        )

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
        _validate_data(data, attributes=[geometry.X, geometry.Y])
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
        _validate_data(data, attributes=[geometry.X, geometry.Y])
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

    def parse_flow(self, entry: dict) -> Flow:
        """
        Parse flows and assign already parsed sections to the flows.

        Args:
            entry (dict): element to be parsed
            to_section (Callable[[SectionId], Optional[Section]]): callable to get a
            section for a section id

        Raises:
            MissingSection: if there is no section for the parsed section id

        Returns:
            Flow: parsed flow element
        """
        _validate_data(
            entry,
            attributes=[
                flow.FLOW_ID,
                flow.START,
                flow.END,
                flow.DISTANCE,
            ],
        )
        flow_id = FlowId(entry.get(flow.FLOW_ID, ""))
        name = entry.get(flow.FLOW_NAME, flow_id.id)
        start = SectionId(entry.get(flow.START, ""))
        end = SectionId(entry.get(flow.END, ""))
        distance = self.__parse_distance(entry)
        return Flow(
            flow_id,
            name=name,
            start=start,
            end=end,
            distance=distance,
        )

    def __parse_distance(self, entry: dict) -> Optional[float]:
        if (distance_entry := entry.get(flow.DISTANCE, 0.0)) is not None:
            return float(distance_entry)
        return None

    def serialize(
        self,
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
    ) -> None:
        """Serialize sections and flows into file.

        Args:
            sections (Iterable[Section]): sections to serialize
            flows (Iterable[Flow]): flows to serialize
            file (Path): file to serialize flows and sections to
        """
        content = self.convert(sections, flows)
        write_json(content, file)

    def convert(
        self,
        sections: Iterable[Section],
        flows: Iterable[Flow],
    ) -> dict[str, list[dict]]:
        """Convert sections and flows into dictionary.

        Args:
            sections (Iterable[Section]): sections to convert
            flows (Iterable[Flow]): flows to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of sections
            and flows
        """
        return {
            section.SECTIONS: [section.to_dict() for section in sections],
            flow.FLOWS: [flow.to_dict() for flow in flows],
        }


class MissingPath(Exception):
    pass


class SimpleVideoParser(VideoParser):
    def __init__(self, video_reader: VideoReader) -> None:
        self._video_reader = video_reader

    def parse(self, file: Path, metadata: VideoMetadata | None) -> Video:
        return SimpleVideo(self._video_reader, file, metadata)

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
        return self.parse(video_path, None)

    def convert(
        self,
        videos: Iterable[Video],
        relative_to: Path = Path("."),
    ) -> dict[str, list[dict]]:
        return {
            video.VIDEOS: [video.to_dict(relative_to=relative_to) for video in videos]
        }


@dataclass
class CachedVideo(Video):

    other: Video
    cache: dict[int, TrackImage] = field(default_factory=dict)

    @property
    def start_date(self) -> Optional[datetime]:
        return self.other.start_date

    @property
    def end_date(self) -> Optional[datetime]:
        return self.other.end_date

    @property
    def fps(self) -> float:
        return self.other.fps

    def get_path(self) -> Path:
        return self.other.get_path()

    def get_frame(self, index: int) -> TrackImage:
        if index in self.cache:
            return self.cache[index]
        new_frame = self.other.get_frame(index)
        self.cache[index] = new_frame
        return new_frame

    def get_frame_number_for(self, date: datetime) -> int:
        return self.other.get_frame_number_for(date)

    def to_dict(self, relative_to: Path) -> dict:
        return self.other.to_dict(relative_to)

    def contains(self, date: datetime) -> bool:
        return self.other.contains(date)


class CachedVideoParser(VideoParser):

    def __init__(self, other: VideoParser) -> None:
        self._other = other

    def parse(self, file: Path, metadata: Optional[VideoMetadata]) -> Video:
        other_video = self._other.parse(file, metadata)
        return self.__create_cached_video(other_video)

    def __create_cached_video(self, other_video: Video) -> Video:
        return CachedVideo(other_video)

    def parse_list(self, content: list[dict], base_folder: Path) -> Sequence[Video]:
        return [
            self.__create_cached_video(video)
            for video in self._other.parse_list(content, base_folder)
        ]

    def convert(
        self,
        videos: Iterable[Video],
        relative_to: Path = Path("."),
    ) -> dict[str, list[dict]]:
        return self._other.convert(videos=videos, relative_to=relative_to)


class OttrkVideoParser(TrackVideoParser):
    def __init__(
        self,
        video_parser: VideoParser,
        track_format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
    ) -> None:
        self._video_parser = video_parser
        self._track_format_fixer = track_format_fixer

    def parse(
        self, file: Path, track_ids: list[TrackId], metadata: VideoMetadata
    ) -> Tuple[list[TrackId], list[Video]]:
        video = self._video_parser.parse(file.parent / metadata.path, metadata)
        return track_ids, [video] * len(track_ids)

    def __parse_recorded_start_date(self, metadata: dict) -> datetime:
        start_date = float(metadata[ottrk_format.RECORDED_START_DATE])
        return datetime.fromtimestamp(start_date, tz=timezone.utc)


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
        write_json_bz2(content, file)

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
