from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.reset_state import ResetState


class TestResetState:
    def test_reset_state(
        self,
        videos_metadata: Mock,
        tracks_metadata: Mock,
        track_view_state: Mock,
        track_state: Mock,
        section_state: Mock,
        flow_state: Mock,
        action_state: Mock,
        file_state: Mock,
    ) -> None:
        target = ResetState(
            videos_metadata,
            tracks_metadata,
            track_view_state,
            track_state,
            section_state,
            flow_state,
            action_state,
            file_state,
        )

        target.reset()

        videos_metadata.reset.assert_called_once()
        tracks_metadata.reset.assert_called_once()
        track_view_state.reset.assert_called_once()
        track_state.reset.assert_called_once()
        section_state.reset.assert_called_once()
        flow_state.reset.assert_called_once()
        action_state.reset.assert_called_once()
        file_state.reset.assert_called_once()


@pytest.fixture
def videos_metadata() -> Mock:
    return Mock()


@pytest.fixture
def tracks_metadata() -> Mock:
    return Mock()


@pytest.fixture
def track_view_state() -> Mock:
    return Mock()


@pytest.fixture
def track_state() -> Mock:
    return Mock()


@pytest.fixture
def section_state() -> Mock:
    return Mock()


@pytest.fixture
def flow_state() -> Mock:
    return Mock()


@pytest.fixture
def action_state() -> Mock:
    return Mock()


@pytest.fixture
def file_state() -> Mock:
    return Mock()
