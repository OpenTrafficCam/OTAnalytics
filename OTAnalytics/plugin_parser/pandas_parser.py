from datetime import datetime, timezone
from functools import partial

from pandas import DataFrame

from OTAnalytics.application.logger import logger
from OTAnalytics.domain import track
from OTAnalytics.domain.track import TrackDataset, TrackId
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
        track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
    ) -> None:
        self._calculator = calculator
        self._track_length_limit = track_length_limit

    def parse_tracks(
        self,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator = TrackId,
    ) -> TrackDataset:
        return self._parse_as_dataframe(detections, metadata_video, id_generator)

    def _parse_as_dataframe(
        self,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator,
    ) -> TrackDataset:
        video_name = (
            metadata_video[ottrk_format.FILENAME]
            + metadata_video[ottrk_format.FILETYPE]
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
            data[track.TRACK_ID].astype(str).apply(id_generator).astype(str)
        )
        data[track.VIDEO_NAME] = video_name
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
        all_track_ids = tracks_by_size[track.TRACK_ID].unique()
        too_long_track_ids = set(all_track_ids) - set(track_ids_to_remain)
        if len(too_long_track_ids) > 0:
            logger().warning(
                f"Number of detections of the following tracks exceeds the "
                f"allowed bounds ({self._track_length_limit})."
                f"Track ids: {too_long_track_ids}"
            )

        tracks_to_remain = data.loc[
            data[track.TRACK_ID].isin(track_ids_to_remain)
        ].copy()
        tracks_to_remain.sort_values(
            by=[track.TRACK_ID, track.OCCURRENCE], inplace=True
        )
        return PandasTrackDataset.from_dataframe(tracks_to_remain, self._calculator)
