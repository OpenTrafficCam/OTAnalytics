import pytest

from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.track import Track
from tests.utils.builders.track_builder import create_track

TRACK_PERFECT = "track-perfect"
TRACK_ONE_FALSE_DETECTION_CLASS = "track-with-one-false-detection-class"


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
        track_id=TRACK_PERFECT,
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
def track_two_false_detection_classes() -> Track:
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
        track_id=TRACK_ONE_FALSE_DETECTION_CLASS,
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
