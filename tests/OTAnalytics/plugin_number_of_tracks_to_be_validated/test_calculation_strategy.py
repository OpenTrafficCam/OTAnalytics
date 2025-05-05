import pytest
from pandas import DataFrame

from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.track import TRACK_CLASSIFICATION, TRACK_ID, Track
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_number_of_tracks_to_be_validated.calculation_strategy import (
    DETECTION_RATE,
    DetectionRateByLength,
    DetectionRateByMaxConfidence,
    DetectionRateByPercentile,
)
from tests.OTAnalytics.plugin_number_of_tracks_to_be_validated.conftest import (
    TRACK_ONE_FALSE_DETECTION_CLASS,
    TRACK_PERFECT,
)


@pytest.fixture
def track_dataset(
    track_perfect: Track,
    track_two_false_detection_classes: Track,
    track_geometry_factory: TRACK_GEOMETRY_FACTORY,
) -> PandasTrackDataset:
    return PandasTrackDataset.from_list(
        [track_perfect, track_two_false_detection_classes], track_geometry_factory
    )


class TestDetectionRateByPercentile:
    def test_calculate(self, track_dataset: PandasTrackDataset) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity
        """  # noqa
        target = DetectionRateByPercentile()
        actual = target.calculate(track_dataset.get_data())
        # round due to inaccuracies in floating point arithmetic
        actual[DETECTION_RATE] = actual[DETECTION_RATE].round(4)
        expected = DataFrame(
            [
                {
                    TRACK_ID: TRACK_PERFECT,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.9,
                },
                {
                    TRACK_ID: TRACK_ONE_FALSE_DETECTION_CLASS,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.6568,
                },
            ]
        ).set_index([TRACK_ID, TRACK_CLASSIFICATION])

        assert actual.equals(expected)


class TestDetectionRateByMaxConfidence:
    def test_calculate(self, track_dataset: PandasTrackDataset) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity
        """  # noqa
        target = DetectionRateByMaxConfidence()
        actual = target.calculate(track_dataset.get_data())
        expected = DataFrame(
            [
                {
                    TRACK_ID: TRACK_PERFECT,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.9,
                },
                {
                    TRACK_ID: TRACK_ONE_FALSE_DETECTION_CLASS,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.9,
                },
            ]
        ).set_index([TRACK_ID, TRACK_CLASSIFICATION])

        assert actual.equals(expected)


class TestDetectionRateByLength:
    def test_calculate(self, track_dataset: PandasTrackDataset) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity #noqa
        """  # noqa
        target = DetectionRateByLength()
        actual = target.calculate(track_dataset.get_data())
        expected = DataFrame(
            [
                {
                    TRACK_ID: TRACK_PERFECT,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 1,
                },
                {
                    TRACK_ID: TRACK_ONE_FALSE_DETECTION_CLASS,
                    TRACK_CLASSIFICATION: OtcClasses.CAR,
                    DETECTION_RATE: 0.6,
                },
            ]
        ).set_index([TRACK_ID, TRACK_CLASSIFICATION])

        assert actual.equals(expected)
