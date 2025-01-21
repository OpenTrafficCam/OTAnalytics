from datetime import datetime, timezone
from functools import partial

from pandas import DataFrame

from OTAnalytics.application.logger import logger
from OTAnalytics.domain import track
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_dataset import TRACK_GEOMETRY_FACTORY, TrackDataset
from OTAnalytics.plugin_datastore.track_store import (
    PandasTrackClassificationCalculator,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    DetectionParser,
    TrackIdGenerator,
    TrackLengthLimit,
)


class PandasDetectionParser(DetectionParser):
    def __init__(
        self,
        calculator: PandasTrackClassificationCalculator,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
        track_ids: list[str] | None = None,
    ) -> None:
        self._calculator = calculator
        self._track_geometry_factory = track_geometry_factory
        self._track_length_limit = track_length_limit
        self._track_ids = track_ids

    def parse_tracks(
        self,
        detections: list[dict],
        metadata_video: dict,
        input_file: str,
        id_generator: TrackIdGenerator = TrackId,
    ) -> TrackDataset:
        return self._parse_as_dataframe(
            detections=detections,
            metadata_video=metadata_video,
            input_file=input_file,
            id_generator=id_generator,
        )

    def _parse_as_dataframe(
        self,
        detections: list[dict],
        metadata_video: dict,
        input_file: str,
        id_generator: TrackIdGenerator,
    ) -> TrackDataset:
        video_name = (
            metadata_video[ottrk_format.FILENAME]
            + metadata_video[ottrk_format.FILETYPE]
        )
        if not detections:
            return PandasTrackDataset(
                track_geometry_factory=self._track_geometry_factory,
                calculator=self._calculator,
            )
        data = DataFrame(detections)
        data.rename(
            columns={
                ottrk_format.CLASS: track.CLASSIFICATION,
                ottrk_format.CONFIDENCE: track.CONFIDENCE,
                ottrk_format.X: track.X,
                ottrk_format.Y: track.Y,
                ottrk_format.W: track.W,
                ottrk_format.H: track.H,
                ottrk_format.FRAME: track.FRAME,
                ottrk_format.OCCURRENCE: track.OCCURRENCE,
                ottrk_format.INTERPOLATED_DETECTION: track.INTERPOLATED_DETECTION,
                ottrk_format.TRACK_ID: track.TRACK_ID,
            },
            inplace=True,
        )
        data[track.TRACK_ID] = (
            data[track.TRACK_ID]
            .astype(str)
            .apply(lambda track_id: str(id_generator(track_id)))
        )
        data[track.VIDEO_NAME] = video_name
        data[track.INPUT_FILE] = input_file
        data[track.OCCURRENCE] = (
            data[track.OCCURRENCE]
            .astype(float)
            .apply(partial(datetime.fromtimestamp, tz=timezone.utc))
        )
        tracks_by_size = data.groupby(by=[track.TRACK_ID]).size().reset_index()
        track_ids_to_remain = tracks_by_size.loc[
            (tracks_by_size[0] >= self._track_length_limit.lower_bound)
            & (tracks_by_size[0] <= self._track_length_limit.upper_bound),
            track.TRACK_ID,
        ]
        if self._track_ids:
            track_ids_to_remain = track_ids_to_remain.loc[
                track_ids_to_remain.isin(self._track_ids)
            ]
        all_track_ids = tracks_by_size[track.TRACK_ID].unique()
        track_ids_outside_bounds = set(all_track_ids) - set(track_ids_to_remain)
        percentage_of_tracks_outside_bounds = (
            len(track_ids_outside_bounds) / len(all_track_ids) * 100
        )
        if len(track_ids_outside_bounds) > 0:
            logger().warning(
                f"Number of detections of {len(track_ids_outside_bounds)} "
                f"({percentage_of_tracks_outside_bounds:.2f}%) tracks "
                f"exceeds the allowed bounds ({self._track_length_limit})."
            )
            logger().debug(f"Track ids: {track_ids_outside_bounds}")
        tracks_to_remain = (
            data.loc[data[track.TRACK_ID].isin(track_ids_to_remain)]
            .copy()
            .set_index([track.TRACK_ID, track.OCCURRENCE])
        )
        tracks_to_remain.index.names = [track.TRACK_ID, track.OCCURRENCE]
        tracks_to_remain = tracks_to_remain.sort_index()
        return PandasTrackDataset.from_dataframe(
            tracks_to_remain, self._track_geometry_factory, calculator=self._calculator
        )
