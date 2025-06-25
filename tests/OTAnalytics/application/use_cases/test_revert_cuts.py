from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.revert_cuts import RevertCuts
from OTAnalytics.domain.track import TrackId


class TestRevertCuts:
    def test_revert(self, track_repository: Mock) -> None:
        original_ids = frozenset([TrackId("1"), TrackId("2")])
        target = RevertCuts(track_repository)
        target.revert(original_ids)

        track_repository.revert_cuts_for.assert_called_once_with(original_ids)


@pytest.fixture
def track_repository() -> Mock:
    return Mock()
