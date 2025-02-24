from pandas import DataFrame

from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.number_of_tracks_to_be_validated import (
    NumberOfTracksToBeValidated,
)
from OTAnalytics.domain.track import (
    OCCURRENCE,
    TRACK_CLASSIFICATION,
    TRACK_ID,
    TrackIdProvider,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.calculation_strategy import (
    DETECTION_RATE,
    DetectionRateCalculationStrategy,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.metric_rates_builder import (
    MetricRatesBuilder,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.svz.metric_rates import (
    SVZ_RATE,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.tracks_as_dataframe_provider import (  # noqa
    TracksAsDataFrameProvider,
)

MANUAL_CLASSIFICATION = "manual_classification"


class SvzNumberOfTracksToBeValidated(NumberOfTracksToBeValidated):
    def __init__(
        self,
        tracks_provider: TracksAsDataFrameProvider,
        tracks_assigned_to_all_flows: TrackIdProvider,
        detection_rate_strategy: DetectionRateCalculationStrategy,
        metric_rates_builder: MetricRatesBuilder,
    ) -> None:
        self._tracks_provider = tracks_provider
        self._tracks_assigned_to_all_flows = tracks_assigned_to_all_flows
        self._detection_rate_strategy = detection_rate_strategy
        self._rates_builder = metric_rates_builder

    def calculate(self) -> int:
        tracks_df = self._tracks_provider.provide()
        if tracks_df is None:
            return 0
        data = self._get_tracks_assigned_to_flow(tracks_df.reset_index())
        rate = self._detection_rate_strategy.calculate(data).reset_index()
        metric_rates = self._rates_builder.build_as_dataframe()
        merged = rate.merge(metric_rates, how="left", on=TRACK_CLASSIFICATION)
        merged[DETECTION_RATE] = merged[DETECTION_RATE].round(2)
        number_of_tracks = len(merged)
        filter_column = MANUAL_CLASSIFICATION
        merged[filter_column] = merged[DETECTION_RATE] < merged[SVZ_RATE]
        filtered = merged.loc[merged[filter_column], :]
        logger().info(
            f"To classify manually: {len(filtered)} of {number_of_tracks} tracks."
        )
        return len(filtered)

    def _get_tracks_assigned_to_flow(self, track_df: DataFrame) -> DataFrame:
        road_user_assignments = [
            track_id.id for track_id in self._tracks_assigned_to_all_flows.get_ids()
        ]
        assigned_tracks = track_df.loc[track_df[TRACK_ID].isin(road_user_assignments)]
        assigned_tracks = assigned_tracks.loc[
            track_df[TRACK_CLASSIFICATION] != "pedestrian", :
        ]
        return assigned_tracks.set_index([TRACK_ID, OCCURRENCE])
