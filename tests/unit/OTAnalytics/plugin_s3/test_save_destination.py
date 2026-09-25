from dataclasses import dataclass
from pathlib import Path

import pytest

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.save_destination import UnsupportedSaveDestination
from OTAnalytics.plugin_s3.save_destination import RequireDestinationUnderUserSource

PREFIX = S3KeyPrefix("project-1/site-2/otcamera19")


@dataclass
class Given:
    user_source: Path


def create_given(user_source: Path) -> Given:
    return Given(user_source=user_source)


def create_target(given: Given) -> RequireDestinationUnderUserSource:
    return RequireDestinationUnderUserSource(given.user_source)


class TestRequireDestinationUnderUserSource:
    def test_accepts_a_file_under_the_prefix(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = create_target(given)
        destination = tmp_path / PREFIX.value / "my.otconfig"

        target(destination, PREFIX)

    def test_refuses_a_file_outside_user_source(self, tmp_path: Path) -> None:
        given = create_given(tmp_path / "user-source")
        target = create_target(given)
        destination = tmp_path / "elsewhere" / "my.otconfig"

        with pytest.raises(UnsupportedSaveDestination):
            target(destination, PREFIX)

    def test_refuses_a_file_under_user_source_but_a_different_prefix(
        self, tmp_path: Path
    ) -> None:
        given = create_given(tmp_path)
        target = create_target(given)
        destination = tmp_path / "some-other-prefix" / "my.otconfig"

        with pytest.raises(UnsupportedSaveDestination):
            target(destination, PREFIX)
