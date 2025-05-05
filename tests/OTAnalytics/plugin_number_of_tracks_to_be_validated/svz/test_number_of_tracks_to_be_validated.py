from unittest.mock import Mock

import pytest
from pandas import DataFrame

from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.track import OCCURRENCE, TRACK_CLASSIFICATION, TRACK_ID, Track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_number_of_tracks_to_be_validated.calculation_strategy import (
    DETECTION_RATE,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.metric_rates_builder import (
    MetricRatesBuilder,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.svz.metric_rates import (
    SVZ_CLASSIFICATION,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.svz.number_of_tracks_to_be_validated import (  # noqa
    SvzNumberOfTracksToBeValidated,
)
from tests.utils.builders.track_builder import create_track

TRACK_PEDESTRIAN = "track-pedestrian"

COORD = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]

TRACK_WITH_NO_ASSIGNMENT = "track-with-no-assignment"


@pytest.fixture
def track_with_no_assignment() -> Track:
    return create_track(
        track_id=TRACK_WITH_NO_ASSIGNMENT,
        coord=COORD,
        start_second=0,
        track_class=OtcClasses.BICYCLIST,
        detection_classes=[
            OtcClasses.BICYCLIST,
            OtcClasses.BICYCLIST,
            OtcClasses.BICYCLIST,
            OtcClasses.BICYCLIST,
            OtcClasses.BICYCLIST,
        ],
        confidences=[0.8, 0.9, 0.8, 0.88, 0.7],
    )


@pytest.fixture
def track_pedestrian() -> Track:
    return create_track(
        track_id=TRACK_PEDESTRIAN,
        coord=COORD,
        start_second=0,
        track_class=OtcClasses.PEDESTRIAN,
        detection_classes=[
            OtcClasses.PEDESTRIAN,
            OtcClasses.BICYCLIST,
            OtcClasses.PEDESTRIAN,
            OtcClasses.PEDESTRIAN,
            OtcClasses.BICYCLIST,
        ],
        confidences=[0.8, 0.9, 0.8, 0.88, 0.7],
    )


@pytest.fixture
def given_track_dataset(
    track_perfect: Track,
    track_two_false_detection_classes: Track,
    track_with_no_assignment: Track,
    track_pedestrian: Track,
    track_geometry_factory: TRACK_GEOMETRY_FACTORY,
) -> PandasTrackDataset:
    return PandasTrackDataset.from_list(
        [
            track_perfect,
            track_two_false_detection_classes,
            track_with_no_assignment,
            track_pedestrian,
        ],
        track_geometry_factory,
    )


@pytest.fixture
def given_tracks_provider(given_track_dataset: PandasTrackDataset) -> Mock:
    given = Mock()
    given.provide.return_value = given_track_dataset.get_data()
    return given


@pytest.fixture
def given_tracks_assigned_to_all_flows(
    track_perfect: Track,
    track_two_false_detection_classes: Track,
    track_pedestrian: Track,
) -> Mock:
    use_case = Mock()
    use_case.get_ids.return_value = [
        track_perfect.id,
        track_two_false_detection_classes.id,
        track_pedestrian.id,
    ]
    return use_case


@pytest.fixture
def given_detection_rate_strategy(
    track_perfect: Track,
    track_two_false_detection_classes: Track,
    track_pedestrian: Track,
) -> Mock:
    strategy = Mock()
    data = DataFrame(
        [
            {
                TRACK_ID: track_perfect.id.id,
                TRACK_CLASSIFICATION: track_perfect.classification,
                DETECTION_RATE: 0.95,
            },
            {
                TRACK_ID: track_two_false_detection_classes.id.id,
                TRACK_CLASSIFICATION: track_two_false_detection_classes.classification,
                DETECTION_RATE: 0.79,
            },
        ]
    ).set_index([TRACK_ID, TRACK_CLASSIFICATION])
    strategy.calculate.return_value = data
    return strategy


@pytest.fixture
def given_rates_builder() -> MetricRatesBuilder:
    return MetricRatesBuilder(SVZ_CLASSIFICATION)


@pytest.fixture
def expected_tracks_assigned_to_flows_dataframe(
    given_track_dataset: PandasTrackDataset,
    track_perfect: Track,
    track_two_false_detection_classes: Track,
) -> DataFrame:
    data = given_track_dataset.get_data()
    return (
        (data.loc[[track_perfect.id.id, track_two_false_detection_classes.id.id]])
        .reset_index()
        .set_index([TRACK_ID, OCCURRENCE])
    )


class TestSvzNumberOfTracksToBeValidated:
    def test_calculate(
        self,
        given_tracks_provider: Mock,
        given_tracks_assigned_to_all_flows: Mock,
        given_detection_rate_strategy: Mock,
        given_rates_builder: MetricRatesBuilder,
        track_perfect: Track,
        track_two_false_detection_classes: Track,
        expected_tracks_assigned_to_flows_dataframe: DataFrame,
    ) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity #noqa
        """  # noqa
        target = SvzNumberOfTracksToBeValidated(
            tracks_provider=given_tracks_provider,
            tracks_assigned_to_all_flows=given_tracks_assigned_to_all_flows,
            detection_rate_strategy=given_detection_rate_strategy,
            metric_rates_builder=given_rates_builder,
        )

        actual = target.calculate()
        assert actual == 1
        given_tracks_assigned_to_all_flows.get_ids.assert_called_once()
        given_detection_rate_strategy.calculate.assert_called_once()
        self.assert_strategy_called_with_tracks_assigned_to_flows(
            given_detection_rate_strategy, expected_tracks_assigned_to_flows_dataframe
        )
        given_tracks_provider.provide.assert_called_once()

    def assert_strategy_called_with_tracks_assigned_to_flows(
        self, detection_rate_strategy: Mock, expected: DataFrame
    ) -> None:
        actual = detection_rate_strategy.calculate.call_args[0][0]
        assert actual.equals(expected)
