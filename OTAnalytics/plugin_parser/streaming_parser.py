import bz2
import glob
from abc import ABC, abstractmethod
from bisect import bisect
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence

import ijson
from pygeos import (
    contains,
    get_coordinates,
    intersection,
    intersects,
    is_empty,
    line_locate_point,
    points,
)

from OTAnalytics.application.datastore import DetectionMetadata, VideoMetadata
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
)
from OTAnalytics.domain.track_dataset import IntersectionPoint, TrackDataset
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    GEOMETRY,
    PROJECTION,
    PygeosTrackGeometryDataset,
    area_section_to_pygeos,
    create_pygeos_track,
    line_sections_to_pygeos_multi,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.json_parser import parse_json_bz2
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    Ottrk_Version_1_0_To_1_1,
    OttrkFormatFixer,
    OttrkParser,
    TrackIdGenerator,
    TrackLengthLimit,
    Version,
    create_python_track,
    parse_python_detection,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder

RawDetectionData = list[dict]
RawVideoMetadata = dict
RawFileData = tuple[RawDetectionData, RawVideoMetadata, TrackIdGenerator]


def parse_json_bz2_events(path: Path) -> Iterable[tuple[str, str, str]]:
    """
    Provide lazy data stream reading the bzip2 compressed file
    at the given path and interpreting it as json objects.
    """
    stream = bz2.BZ2File(path)
    return ijson.parse(stream)


def metadata_from_json_events(parse_events: Iterable[tuple[str, str, str]]) -> dict:
    """
    Extract the metadata block of the ottrk data format
    from the given json parser event stream.
    """
    result: dict
    for data in ijson.items(parse_events, "metadata"):
        result = data
        break
    return result


def detection_stream_from_json_events(parse_events: Any) -> Iterator[dict]:
    """
    Extract the detection attributes from the deata.detections block
    of the ottrk data format from the given json parser event stream.
    """
    yield from ijson.items(parse_events, "data.detections.item")


def parse_json_bz2_ottrk_bulk(path: Path) -> tuple[dict, Iterator[dict]]:
    """
    Extract metadata block and list of detections attributes of the ottrk data format
    from the bzip2 compressed file at the given path by reading the whole file in bulk.
    """
    ottrk_dict = parse_json_bz2(path)
    dets_list: list[dict] = ottrk_dict[ottrk_format.DATA][ottrk_format.DATA_DETECTIONS]
    metadata = ottrk_dict[ottrk_format.METADATA]

    return metadata, iter(dets_list)


class StreamDetectionParser(ABC):
    """
    Parser the detections data in ottrk data format
    and convert them to a stream of `TrackDataset`s.
    """

    @abstractmethod
    def parse_tracks_stream(
        self,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator = TrackId,
    ) -> Iterator[TrackDataset]:
        """Parse the given detections into a stream of TrackDatasets.

        When Detections with the "finished" flag are parsed,
        the according Track is assembled and provided via the stream.

        Args:
            detections (list[dict]): the detections in dict format.
            metadata_video (dict): metadata of the track file in dict format.
            id_generator (TrackIdGenerator): generator used to create track ids.

        Returns:
            Iterator[TrackDataset]: a stream of TackDatasets, one per Track.
        """
        raise NotImplementedError

    @abstractmethod
    def get_remaining_tracks(self) -> Iterator[TrackDataset]:
        """Get yet unparsed tracks,
        that did not show a detection with the "finished" flag."""
        raise NotImplementedError


class PythonStreamDetectionParser(StreamDetectionParser):
    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_length_limit: TrackLengthLimit,
    ) -> None:
        self._track_classification_calculator = track_classification_calculator
        self._track_length_limit = track_length_limit
        self._tracks_dict: dict[TrackId, list[Detection]] = dict()

    def parse_tracks_stream(
        self,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator = TrackId,
    ) -> Iterator[TrackDataset]:
        for det_dict in detections:
            det = parse_python_detection(metadata_video, id_generator, det_dict)
            if not self._tracks_dict.get(det.track_id):
                self._tracks_dict[det.track_id] = []

            self._tracks_dict[det.track_id].append(det)  # Group detections by track id

            if det_dict[ottrk_format.FINISHED]:
                track_detections = self._tracks_dict[det.track_id]
                del self._tracks_dict[det.track_id]

                track = create_python_track(
                    det.track_id,
                    track_detections,
                    self._track_classification_calculator,
                    self._track_length_limit,
                )  # yield finished track
                if track is not None:
                    yield SingletonTrackDataset(track)

    # after all files have been processed,
    # yield all remaining tracks without finished flag
    def get_remaining_tracks(self) -> Iterator[TrackDataset]:
        for (
            track_id,
            detections,
        ) in self._tracks_dict.items():
            track = create_python_track(
                track_id,
                detections,
                self._track_classification_calculator,
                self._track_length_limit,
            )  # yield remaining track
            if track is not None:
                yield SingletonTrackDataset(track)


class StreamTrackParser(ABC):
    @abstractmethod
    def parse(self, files: list[Path]) -> Iterator[TrackDataset]:
        raise NotImplementedError


class StreamOttrkParser(StreamTrackParser):
    def __init__(
        self,
        detection_parser: StreamDetectionParser,
        format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
        registered_tracks_metadata: list[TracksMetadata] = [],
        registered_videos_metadata: list[VideosMetadata] = [],
        progressbar: ProgressbarBuilder = TqdmBuilder(),
    ) -> None:
        self._detection_parser = detection_parser
        self._tracks_dict: dict[TrackId, list[Detection]] = {}
        self._format_fixer = format_fixer
        self._registered_tracks_metadata: list[TracksMetadata] = list(
            registered_tracks_metadata
        )
        self._registered_videos_metadata: list[VideosMetadata] = list(
            registered_videos_metadata
        )
        self._progressbar = progressbar

    def register_tracks_metadata(self, tracks_metadata: TracksMetadata) -> None:
        self._registered_tracks_metadata.append(tracks_metadata)

    def register_videos_metadata(self, videos_metadata: VideosMetadata) -> None:
        self._registered_videos_metadata.append(videos_metadata)

    def _update_registered_metadata_collections(
        self,
        new_detection_metadata: DetectionMetadata,
        new_video_metadata: VideoMetadata,
    ) -> None:
        for tracks_metadata in self._registered_tracks_metadata:
            tracks_metadata.update_detection_classes(
                new_detection_metadata.detection_classes
            )

        for videos_metadata in self._registered_videos_metadata:
            videos_metadata.update(new_video_metadata)

    def parse(self, files: list[Path]) -> Iterator[TrackDataset]:
        files = self._sort_files(files)
        progressbar = self._progressbar(
            files, unit="files", description="Processed ottrk files: "
        )

        for ottrk_file in progressbar:
            ottrk_dict = parse_json_bz2(ottrk_file)

            fixed_ottrk = self._format_fixer.fix(ottrk_dict)
            det_list: list[dict] = fixed_ottrk[ottrk_format.DATA][
                ottrk_format.DATA_DETECTIONS
            ]
            metadata_video = ottrk_dict[ottrk_format.METADATA][ottrk_format.VIDEO]

            detection_metadata = OttrkParser.parse_metadata(
                ottrk_dict[ottrk_format.METADATA]
            )
            video_metadata = OttrkParser.parse_video_metadata(metadata_video)
            id_generator = OttrkParser.create_id_generator_from(
                ottrk_dict[ottrk_format.METADATA]
            )
            self._update_registered_metadata_collections(
                detection_metadata, video_metadata
            )

            yield from self._detection_parser.parse_tracks_stream(
                det_list, metadata_video, id_generator
            )

        # after all files are processed, yield remaining, unfinished tracks
        yield from self._detection_parser.get_remaining_tracks()

    def _sort_files(self, files: list[Path]) -> list[Path]:
        return list(
            sorted(filter(lambda p: p.is_file(), files), key=self._start_date_metadata)
        )

    def _start_date_metadata(self, file: Path) -> float:
        json_events = parse_json_bz2_events(file)
        metadata = metadata_from_json_events(
            json_events
        )  # TODO metadata fixer in constructor
        version = Version.from_str(metadata[ottrk_format.OTTRK_VERSION])
        metadata = Ottrk_Version_1_0_To_1_1().fix(metadata, version)
        return float(metadata[ottrk_format.VIDEO][ottrk_format.RECORDED_START_DATE])


class SingletonTrackDataset(TrackDataset):
    """A TrackDataSet based on a single track."""

    def __init__(self, track: Track) -> None:
        self._track = track

        self._geometries: dict[RelativeOffsetCoordinate, dict]

    def _get_geometry_data_for(self, offset: RelativeOffsetCoordinate) -> Any:
        # TODO resolve code duplication with pygeos store
        if (geometry_data := self._geometries.get(offset, None)) is None:
            geometry = create_pygeos_track(self._track, offset)
            projection = [
                line_locate_point(geometry, points(p))
                for p in get_coordinates(geometry)
            ]
            geometry_data = {
                GEOMETRY: geometry,
                PROJECTION: projection,
            }

            self._geometries[offset] = geometry_data
        return geometry_data

    @property
    def track_ids(self) -> frozenset[TrackId]:
        return frozenset((self._track.id,))

    @property
    def first_occurrence(self) -> datetime | None:
        return self._track.first_detection.occurrence

    @property
    def last_occurrence(self) -> datetime | None:
        return self._track.last_detection.occurrence

    @property
    def classifications(self) -> frozenset[str]:
        return frozenset(tuple(self._track.classification))

    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        raise NotImplementedError

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self._track if id == self._track.id else None

    def remove(self, track_id: TrackId) -> "TrackDataset":
        raise NotImplementedError

    def remove_multiple(self, track_ids: set[TrackId]) -> "TrackDataset":
        raise NotImplementedError

    def clear(self) -> "TrackDataset":
        raise NotImplementedError

    def as_list(self) -> list[Track]:
        return [self._track]

    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> set[TrackId]:
        geometry_data = self._get_geometry_data_for(offset)
        section_geoms = line_sections_to_pygeos_multi(sections)

        if intersects(geometry_data[GEOMETRY], section_geoms):
            return {self._track.id}
        else:
            return set()

    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        geometry_data = self._get_geometry_data_for(offset)
        geometry = geometry_data[GEOMETRY]
        projection = geometry_data[PROJECTION]
        section_geoms = line_sections_to_pygeos_multi(sections)

        section_ips = [
            (sections[index].id, ip)
            for index, ip in enumerate(intersection(geometry, section_geoms))
            if not is_empty(ip)
        ]

        intersections = [
            (
                self._track.id,
                _section_id,
                IntersectionPoint(
                    bisect(projection, line_locate_point(geometry, point))
                ),
            )
            for _section_id, ip in section_ips
            for point in get_coordinates(ip)
        ]

        intersection_points = defaultdict(list)
        for (
            _id,
            section_id,
            intersection_point,
        ) in intersections:  # chain.from_iterable() TODO ??
            intersection_points[_id].append((section_id, intersection_point))

        return intersection_points

    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        geometry_data = self._get_geometry_data_for(offset)
        geometry = geometry_data[GEOMETRY]

        contains_result: dict[
            TrackId, list[tuple[SectionId, list[bool]]]
        ] = defaultdict(list)
        for _section in sections:
            section_geom = area_section_to_pygeos(_section)

            contains_mask = [
                contains(section_geom, points(p))[0] for p in get_coordinates(geometry)
            ]

            if not any(contains_mask):
                continue

            contains_result[self._track.id].append((_section.id, contains_mask))

        return contains_result

    def split(self, chunks: int) -> Sequence["TrackDataset"]:
        return [self]

    def __len__(self) -> int:
        return 1

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        for offset in offsets:
            if offset not in self._geometries.keys():
                self._geometries[offset] = self._get_geometry_data_for(offset)

    def apply_to_first_segments(self, consumer: Callable[[Event], None]) -> None:
        event = PythonTrackDataset.create_enter_scene_event(self._track)
        consumer(event)

    def apply_to_last_segments(self, consumer: Callable[[Event], None]) -> None:
        event = PythonTrackDataset.create_leave_scene_event(self._track)
        consumer(event)

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple["TrackDataset", set[TrackId]]:
        cut_tracks = PythonTrackDataset.cut_track_with_section(
            self._track, section, offset
        )

        if len(cut_tracks) > 0:
            return (
                PythonTrackDataset.from_list(cut_tracks),
                {self._track.id},
                # only possible id the single track of this data set
            )
        else:  # return empty track dataset as no tracks were cut
            return (PythonTrackDataset(), set())

    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        if len(self._track.detections) >= length:
            return self
        else:
            return PythonTrackDataset()


# TESTING


def parse_old(dir: Path) -> None:
    files = list(
        filter(lambda p: p.is_file(), sorted(dir.glob("*.ottrk"), key=lambda p: p.name))
    )

    track_repository = TrackRepository(
        PandasTrackDataset.from_list([], PygeosTrackGeometryDataset.from_track_dataset)
    )

    tracks_metadata = TracksMetadata(track_repository)
    videos_metadata = VideosMetadata()

    calculator = PandasByMaxConfidence()
    detection_parser = PandasDetectionParser(
        calculator,
        PygeosTrackGeometryDataset.from_track_dataset,
        track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
    )
    parser = OttrkParser(detection_parser)

    for file in files:
        print(file)
        parse_result = parser.parse(file)
        tracks_metadata.update_detection_classes(
            parse_result.detection_metadata.detection_classes
        )
        videos_metadata.update(parse_result.video_metadata)

    c = 0
    for t in track_repository.get_all():
        print(c, t.id)
        c += 1


def parse_stream(files: list[Path]) -> None:
    track_repository = TrackRepository(PythonTrackDataset())

    tracks_metadata = TracksMetadata(track_repository)
    videos_metadata = VideosMetadata()

    calculator = ByMaxConfidence()
    detection_parser = PythonStreamDetectionParser(
        calculator,
        track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
    )

    parser = StreamOttrkParser(detection_parser)
    parser.register_tracks_metadata(tracks_metadata)
    parser.register_videos_metadata(videos_metadata)

    res = parser.parse(files)
    [t for t in res]


if __name__ == "__main__":
    paths = [Path(f) for f in glob.glob(r"D:\ptm\data\load_multi_files\*.ottrk")]
    parse_stream(paths)
