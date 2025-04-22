from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.reset_state import ResetState


class TestResetState:
    def test_reset_state(self, videos_metadata: Mock) -> None:
        target = ResetState(videos_metadata)

        target.reset()

        videos_metadata.reset.assert_called_once()


@pytest.fixture
def videos_metadata() -> Mock:
    return Mock()
