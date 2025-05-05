from unittest.mock import Mock, PropertyMock, patch

import pytest

from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset
from OTAnalytics.plugin_number_of_tracks_to_be_validated.tracks_as_dataframe_provider import (  # noqa
    TracksAsDataFrameProvider,
)
from tests.conftest import YieldFixture


def given_get_all_tracks(dataset: TrackDataset) -> Mock:
    given = Mock()
    given.as_dataset.return_value = dataset
    given.from_list.return_value = dataset.as_list()
    return given


@pytest.fixture
def given_empty_track_dataset() -> Mock:
    given = Mock(spec=TrackDataset)
    type(given).empty = PropertyMock(return_value=True)
    return given


@pytest.fixture
def expected_track_dataframe() -> Mock:
    return Mock()


@pytest.fixture
def given_pandas_track_dataset(expected_track_dataframe: Mock) -> Mock:
    given = Mock(spec=PandasTrackDataset)
    type(given).empty = PropertyMock(return_value=False)
    given.get_data.return_value = expected_track_dataframe
    return given


@pytest.fixture
def expected_track_dataset(expected_track_dataframe: Mock) -> Mock:
    dataset = Mock()
    dataset.get_data.return_value = expected_track_dataframe
    return dataset


@pytest.fixture
def given_non_pandas_track_dataset(expected_track_dataset: Mock) -> YieldFixture[Mock]:
    with patch(
        (
            "OTAnalytics.plugin_number_of_tracks_to_be_validated."
            "tracks_as_dataframe_provider.PandasTrackDataset.from_list"
        )
    ) as from_list:
        given = Mock()
        type(given).empty = PropertyMock(return_value=False)
        from_list.return_value = expected_track_dataset
        yield given


@pytest.fixture
def given_track_geometry_factory() -> Mock:
    return Mock()


@pytest.fixture
def given_pandas_track_classification_calculator() -> Mock:
    return Mock()


class TestTracksAsDataFrameProvider:
    def test_provide_given_empty_dataset(
        self,
        given_empty_track_dataset: Mock,
        given_track_geometry_factory: Mock,
        given_pandas_track_classification_calculator: Mock,
    ) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity #noqa
        """  # noqa
        target = TracksAsDataFrameProvider(
            get_all_tracks=given_get_all_tracks(given_empty_track_dataset()),
            track_geometry_factory=given_track_geometry_factory,
            calculator=given_pandas_track_classification_calculator,
        )
        actual = target.provide()
        assert actual is None

    def test_provide_given_pandas_track_dataset(
        self,
        given_pandas_track_dataset: Mock,
        given_track_geometry_factory: Mock,
        given_pandas_track_classification_calculator: Mock,
        expected_track_dataframe: Mock,
    ) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity #noqa
        """  # noqa
        target = TracksAsDataFrameProvider(
            get_all_tracks=given_get_all_tracks(given_pandas_track_dataset),
            track_geometry_factory=given_track_geometry_factory,
            calculator=given_pandas_track_classification_calculator,
        )
        actual = target.provide()
        assert actual == expected_track_dataframe

    def test_provide_given_non_pandas_track_dataset(
        self,
        given_non_pandas_track_dataset: Mock,
        given_track_geometry_factory: Mock,
        given_pandas_track_classification_calculator: Mock,
        expected_track_dataframe: Mock,
    ) -> None:
        """
        #Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/6491/activity #noqa
        """  # noqa
        target = TracksAsDataFrameProvider(
            get_all_tracks=given_get_all_tracks(given_non_pandas_track_dataset),
            track_geometry_factory=given_track_geometry_factory,
            calculator=given_pandas_track_classification_calculator,
        )
        actual = target.provide()
        assert actual == expected_track_dataframe
