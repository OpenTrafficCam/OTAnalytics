from unittest.mock import Mock, patch

import pytest

from OTAnalytics.domain.files import DifferentDrivesException, build_relative_path


class TestBuildingRelativePaths:
    def test_resolve_relative_paths_on_different_drives(self) -> None:
        with patch(
            "OTAnalytics.domain.files.splitdrive",
            side_effect=[("C:", "rest"), ("D:", "rest")],
        ):
            with pytest.raises(DifferentDrivesException):
                build_relative_path(
                    Mock(), Mock(), lambda actual, other: "drive exception"
                )
