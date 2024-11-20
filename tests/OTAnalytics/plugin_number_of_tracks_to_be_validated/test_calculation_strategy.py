import pytest
from pandas import DataFrame

from OTAnalytics.domain.track import TRACK_CLASSIFICATION, TRACK_ID, Track
from OTAnalytics.domain.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_number_of_tracks_to_be_validated.calculation_strategy import (
    DETECTION_RATE,
    DetectionRateByLength,
    DetectionRateByMaxConfidence,
    DetectionRateByPercentile,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.otc_classes import OtcClasses
from tests.utils.builders.track_builder import create_track

FIRST_TRACK_ID = "track-perfect"
SECOND_TRACK_ID = "track-with-one-false-detection-class"

COORD = ([(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],)


@pytest.fixture
def track_perfect() -> Track:
    """
    confs_car  = [0.7, 0.75, 0.8, 0.88, 0.9]
    N_car = len(confs_car) = 5
    Q_90,car= 0.9

    p(car) = Q_90,car * (Q_90,car * N_car) / (Q_90,car * N_car)

    <=> p(car) = 0.9 * (0.9 * 3 ) / (0.9 * 3)= 0.9
    """
    return create_track(
        track_id=FIRST_TRACK_ID,
        coord=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
        start_second=0,
        track_class=OtcClasses.CAR,
        detection_classes=[
            OtcClasses.CAR,
            OtcClasses.CAR,
            OtcClasses.CAR,
            OtcClasses.CAR,
            OtcClasses.CAR,
        ],
        confidences=[0.8, 0.9, 0.7, 0.88, 0.75],
    )


@pytest.fixture
def track_with_one_false_detection_class() -> Track:
    """
    confs_car  = [0.8, 0.88, 0.9]
    confs_truck = [0.4, 0.5]

    N_car = len(confs_car) = 3
    N_truck = len(confs_truck) = 2

    Q_90,car= 0.9
    Q_90,truck = 0.5

    p(car) = Q_90,car * (Q_90,car * N_car) / (Q_90,car * N_car + Q_90,truck * N_truck

    <=> p(car) = 0.9 * (0.9 * 3 ) / (0.9 * 3 + 0.5 * 2)= 0.6567567568
    """
    return create_track(
        track_id=SECOND_TRACK_ID,
        coord=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
        start_second=0,
        track_class=OtcClasses.CAR,
        detection_classes=[
            OtcClasses.CAR,
            OtcClasses.CAR,
            OtcClasses.TRUCK,
            OtcClasses.CAR,
            OtcClasses.TRUCK,
        ],
        confidences=[0.8, 0.9, 0.5, 0.88, 0.4],
    )


@pytest.fixture
def track_dataset(
    track_perfect: Track,
    track_with_one_false_detection_class: Track,
    track_geometry_factory: TRACK_GEOMETRY_FACTORY,
) -> PandasTrackDataset:
    return PandasTrackDataset.from_list(
        [track_perfect, track_with_one_false_detection_class], track_geometry_factory
    )


class TestDetectionRateByPercentile:
    def test_calculate(self, track_dataset: PandasTrackDataset) -> None:
        rate_calculator = DetectionRateByPercentile()
        result = rate_calculator.calculate(track_dataset.get_data())
        # round due to inaccuracies in floating point arithmetic
        result[DETECTION_RATE] = result[DETECTION_RATE].round(4)
        expected = DataFrame(
            [
                {
                    TRACK_ID: FIRST_TRACK_ID,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.9,
                },
                {
                    TRACK_ID: SECOND_TRACK_ID,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.6568,
                },
            ]
        ).set_index([TRACK_ID, TRACK_CLASSIFICATION])

        assert result.equals(expected)


class TestDetectionRateByMaxConfidence:
    def test_calculate(self, track_dataset: PandasTrackDataset) -> None:
        rate_calculator = DetectionRateByMaxConfidence()
        result = rate_calculator.calculate(track_dataset.get_data())
        expected = DataFrame(
            [
                {
                    TRACK_ID: FIRST_TRACK_ID,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.9,
                },
                {
                    TRACK_ID: SECOND_TRACK_ID,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.9,
                },
            ]
        ).set_index([TRACK_ID, TRACK_CLASSIFICATION])

        assert result.equals(expected)


class TestDetectionRateByLength:
    def test_calculate(self, track_dataset: PandasTrackDataset) -> None:
        rate_calculator = DetectionRateByLength()
        result = rate_calculator.calculate(track_dataset.get_data())
        expected = DataFrame(
            [
                {
                    TRACK_ID: FIRST_TRACK_ID,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 1,
                },
                {
                    TRACK_ID: SECOND_TRACK_ID,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.6,
                },
            ]
        ).set_index([TRACK_ID, TRACK_CLASSIFICATION])

        assert result.equals(expected)
