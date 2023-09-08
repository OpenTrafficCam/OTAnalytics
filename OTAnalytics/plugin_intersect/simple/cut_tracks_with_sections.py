from typing import Any, Iterable

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
    CutTracksWithSection,
)
from OTAnalytics.application.use_cases.section_repository import (
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    GetTracksFromIds,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
)
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.section import Section, SectionId, SectionType
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackBuilder,
    TrackBuilderError,
    TrackClassificationCalculator,
    TrackId,
)
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper


class SimpleCutTracksIntersectingSection(CutTracksIntersectingSection):
    """Implementation of `CutTracksIntersectingSection`

    Args:
        get_sections_by_id (GetSectionsById): get sections by id.
        get_tracks (GetTracksWithoutSingleDetections): get all tracks with at
            least two detections.
        tracks_intersecting_sections (TracksIntersectingSections): returns all
            tracks intersecting a section.
        cut_tracks_with_section (CutTracksWithSection): returns cut tracks with
            a section.
        add_all_tracks (AddAllTracks): used to add all tracks to the track
            repository.
        remove_tracks (RemoveTracks): used to remove original tracks that have been
            cut.
        remove_section (RemoveSection): used to remove the cutting section.
    """

    def __init__(
        self,
        get_sections_by_id: GetSectionsById,
        get_tracks: GetTracksWithoutSingleDetections,
        tracks_intersecting_sections: TracksIntersectingSections,
        cut_tracks_with_section: CutTracksWithSection,
        add_all_tracks: AddAllTracks,
        remove_tracks: RemoveTracks,
        remove_section: RemoveSection,
    ) -> None:
        self._subject: Subject[Any] = Subject[Any]()

        self._get_sections_by_id = get_sections_by_id
        self._get_tracks = get_tracks
        self._tracks_intersecting_sections = tracks_intersecting_sections
        self._cut_tracks_with_section = cut_tracks_with_section
        self._add_all_tracks = add_all_tracks
        self._remove_tracks = remove_tracks
        self._remove_section = remove_section

    def __call__(self, cutting_section: Section) -> None:
        intersecting_track_ids = self._tracks_intersecting_sections([cutting_section])
        new_tracks = self._cut_tracks_with_section(
            intersecting_track_ids, cutting_section
        )
        self._add_all_tracks(new_tracks)
        self._remove_tracks(intersecting_track_ids)
        self._remove_section(cutting_section.id)
        self._subject.notify(None)

    def notify_sections(self, sections: list[SectionId]) -> None:
        for section in self._get_sections_by_id(sections):
            if section.get_type() == SectionType.CUTTING:
                self.__call__(section)

    def register(self, observer: OBSERVER[Any]) -> None:
        self._subject.register(observer)


class SimpleCutTracksWithSection(CutTracksWithSection):
    """Simple implementation to cut tracks with a cutting section.

    Args:
        get_tracks_from_ids (GetTracksFromIds): get tracks from an iterable of
            TrackIds.
        shapely_mapper (ShapelyMapper): used to create shapely geometries.
        track_builder (TrackBuilder): the builder used to create cut tracks.
    """

    def __init__(
        self,
        get_tracks_from_ids: GetTracksFromIds,
        shapely_mapper: ShapelyMapper,
        track_builder: TrackBuilder,
    ) -> None:
        self._get_tracks_from_ids = get_tracks_from_ids
        self._shapely_mapper = shapely_mapper
        self._track_builder = track_builder

    def __call__(
        self, track_ids: Iterable[TrackId], cutting_section: Section
    ) -> Iterable[Track]:
        tracks = self._get_tracks_from_ids(track_ids)
        cut_tracks: list[Track] = []

        for track in tracks:
            cut_tracks.extend(self._cut_track_with_section(track, cutting_section))
        return cut_tracks

    def _cut_track_with_section(
        self, track: Track, cutting_section: Section
    ) -> Iterable[Track]:
        cut_track_segments: list[Track] = []
        section_geometry = self._shapely_mapper.map_coordinates_to_line_string(
            cutting_section.get_coordinates()
        )
        for current_detection, next_detection in zip(
            track.detections[0:-1], track.detections[1:]
        ):
            track_segment_geometry = self._shapely_mapper.map_detections_to_line_string(
                [current_detection, next_detection]
            )
            if track_segment_geometry.intersects(section_geometry):
                new_track_segment = self._build_track(
                    f"{track.id.id}_{len(cut_track_segments) + 1}", current_detection
                )
                cut_track_segments.append(new_track_segment)
            else:
                self._track_builder.add_detection(current_detection)

        new_track_segment = self._build_track(
            f"{track.id.id}_{len(cut_track_segments) + 1}", track.last_detection
        )
        cut_track_segments.append(new_track_segment)

        return cut_track_segments

    def _build_track(self, track_id: str, detection: Detection) -> Track:
        self._track_builder.add_id(track_id)
        self._track_builder.add_detection(detection)
        return self._track_builder.build()


class SimpleCutTrackSegmentBuilder(TrackBuilder):
    """Build tracks that have been cut with a cutting section.

    The builder will be reset after a successful build of a track.

    Args:
        class_calculator (TrackClassificationCalculator): the strategy to determine
            the max class of a track.
    """

    def __init__(self, class_calculator: TrackClassificationCalculator) -> None:
        self._track_id: TrackId | None = None
        self._detections: list[Detection] = []

        self._class_calculator = class_calculator

    def add_id(self, track_id: str) -> None:
        self._track_id = TrackId(track_id)

    def add_detection(self, detection: Detection) -> None:
        self._detections.append(detection)

    def build(self) -> Track:
        if self._track_id is None:
            raise TrackBuilderError(
                "Track builder setup error occurred. TrackId not set."
            )
        detections = self._build_detections()
        result = Track(
            self._track_id,
            self._class_calculator.calculate(detections),
            detections,
        )
        self.reset()
        return result

    def reset(self) -> None:
        self._track_id = None
        self._detections = []

    def _build_detections(self) -> list[Detection]:
        if self._track_id is None:
            raise TrackBuilderError(
                "Track builder setup error occurred. TrackId not set."
            )
        new_detections = []
        for detection in self._detections:
            new_detections.append(
                Detection(
                    detection.classification,
                    detection.confidence,
                    detection.x,
                    detection.y,
                    detection.w,
                    detection.h,
                    detection.frame,
                    detection.occurrence,
                    detection.interpolated_detection,
                    self._track_id,
                    detection.video_name,
                )
            )
        return new_detections
