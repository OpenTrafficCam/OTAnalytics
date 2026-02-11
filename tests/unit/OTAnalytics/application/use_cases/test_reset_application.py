from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.reset_application import ResetApplication


class TestResetApplication:
    def test_reset(self, clear_repositories: Mock, reset_state: Mock) -> None:
        target = ResetApplication(clear_repositories, reset_state)

        target.reset()

        clear_repositories.assert_called_once()
        reset_state.reset.assert_called_once()


@pytest.fixture
def clear_repositories() -> Mock:
    return Mock()


@pytest.fixture
def reset_state() -> Mock:
    return Mock()
