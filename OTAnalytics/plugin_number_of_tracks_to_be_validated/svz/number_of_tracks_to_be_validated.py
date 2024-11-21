from pandas import DataFrame

from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
)
from OTAnalytics.application.use_cases.number_of_tracks_to_be_validated import (
    NumberOfTracksToBeValidated,
)
from OTAnalytics.domain.track import OCCURRENCE, TRACK_CLASSIFICATION, TRACK_ID
from OTAnalytics.plugin_datastore.track_store import PandasDataFrameProvider
from OTAnalytics.plugin_number_of_tracks_to_be_validated.calculation_strategy import (
    DETECTION_RATE,
    DetectionRateCalculationStrategy,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.metric_rates_builder import (
    MetricRatesBuilder,
)


class SvzNumberOfTracksToBeValidated(NumberOfTracksToBeValidated):
    def __init__(
        self,
        track_provider: PandasDataFrameProvider,
        tracks_assigned_to_all_flows: TracksAssignedToAllFlows,
        detection_rate_strategy: DetectionRateCalculationStrategy,
        metric_rates_builder: MetricRatesBuilder,
    ) -> None:
        self._tracks_assigned_to_all_flows = tracks_assigned_to_all_flows
        self._track_provider = track_provider
        self._detection_rate_strategy = detection_rate_strategy
        self._rates_builder = metric_rates_builder

    def calculate(self) -> int:
        data = self._get_tracks_assigned_to_flow()
        rate = self._detection_rate_strategy.calculate(data).reset_index()
        metric_rates = self._rates_builder.build_as_dataframe()
        merged = rate.merge(metric_rates, how="left", on=TRACK_CLASSIFICATION)
        merged[DETECTION_RATE] = merged[DETECTION_RATE].round(2)
        number_of_tracks = len(merged)
        filter_column = "manual_classification"
        merged[filter_column] = merged[DETECTION_RATE] < merged["Gruppe A3"]
        filtered = merged.loc[merged[filter_column], :]
        logger().info(
            f"To classify manually: {len(filtered)} of {number_of_tracks} tracks."
        )
        return len(filtered)

    def _get_tracks_assigned_to_flow(self) -> DataFrame:
        road_user_assignments = [
            track_id.id for track_id in self._tracks_assigned_to_all_flows.get_ids()
        ]
        data = self._track_provider.get_data().reset_index()
        assigned_tracks = data.loc[data[TRACK_ID].isin(road_user_assignments)]
        assigned_tracks = assigned_tracks.loc[
            data[TRACK_CLASSIFICATION] != "pedestrian", :
        ]
        return assigned_tracks.set_index([TRACK_ID, OCCURRENCE])
