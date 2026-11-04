from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.use_cases.reset_application import ResetApplication


class TestResetApplication:
    def test_reset(self, clear_repositories: Mock, reset_state: Mock) -> None:
        target = ResetApplication(clear_repositories, reset_state)

        target.reset()

        clear_repositories.assert_called_once()
        reset_state.reset.assert_called_once()

    def test_notifies_observers_after_the_reset(
        self, clear_repositories: Mock, reset_state: Mock
    ) -> None:
        order = Mock()
        order.attach_mock(clear_repositories, "clear_repositories")
        order.attach_mock(reset_state.reset, "reset_state")
        order.attach_mock(observer := Mock(), "observer")
        target = ResetApplication(clear_repositories, reset_state)
        target.register(observer)

        target.reset()

        assert order.mock_calls == [
            call.clear_repositories(),
            call.reset_state(),
            call.observer(None),
        ]


@pytest.fixture
def clear_repositories() -> Mock:
    return Mock()


@pytest.fixture
def reset_state() -> Mock:
    return Mock()
