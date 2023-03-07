import bz2
from datetime import datetime
from pathlib import Path

import ujson

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.application.datastore import TrackParser
from OTAnalytics.domain.track import Detection, Track


class OttrkParser(TrackParser):
    """Parse an ottrk file and convert its contents to our domain objects namely
    `Tracks`.

    Args:
        TrackParser (TrackParser): extends TrackParser interface.
    """

    def parse(self, ottrk_file: Path) -> list[Track]:
        """Parse ottrk file and convert its content to domain level objects namely
        `Track`s.

        Args:
            ottrk_file (Path): the file to

        Returns:
            list[Track]: the tracks.
        """
        ottrk_dict = self._parse_bz2(ottrk_file)
        dets_list: list[dict] = ottrk_dict[ottrk_format.DATA][ottrk_format.DETECTIONS]
        tracks = self._parse_tracks(dets_list)
        return tracks

    def _parse_bz2(self, p: Path) -> dict:
        """Parse JSON bz2.

        Args:
            p (Path): Path to bz2 JSON.

        Returns:
            dict: The content of the JSON file.
        """
        with bz2.open(p, "r") as f:
            _dict = ujson.load(f)
            return _dict

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
            sort_dets_by_frame = sorted(detections, key=lambda det: det.occurrence)
            tracks.append(Track(id=track_id, detections=sort_dets_by_frame))
        return tracks

    def _parse_detections(self, det_list: list[dict]) -> dict[int, list[Detection]]:
        """Convert dict to Detection objects and group them by their track id."""
        tracks_dict: dict[int, list[Detection]] = {}
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
                    det_dict[ottrk_format.OCCURENCE], ottrk_format.DATE_FORMAT
                ),
                input_file_path=det_dict[ottrk_format.INPUT_FILE_PATH],
                interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
                track_id=det_dict[ottrk_format.TRACK_ID],
            )
            if not tracks_dict.get(det.track_id):
                tracks_dict[det.track_id] = []

            tracks_dict[det.track_id].append(det)  # Group detections by track id
        return tracks_dict
