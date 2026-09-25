from dataclasses import dataclass
from pathlib import Path

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.save_destination import NoDestinationGuard

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19")


@dataclass
class Given:
    destination: Path


def create_given(tmp_path: Path) -> Given:
    return Given(destination=tmp_path / "anywhere.otconfig")


def create_target(given: Given) -> NoDestinationGuard:
    return NoDestinationGuard()


class TestNoDestinationGuard:
    def test_accepts_any_destination(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)

        create_target(given)(given.destination, A_PREFIX)
