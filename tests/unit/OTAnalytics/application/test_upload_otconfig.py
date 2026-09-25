from dataclasses import dataclass
from pathlib import Path

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.upload_otconfig import NoOtconfigUpload

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19/")


@dataclass
class Given:
    file: Path


def create_given(tmp_path: Path) -> Given:
    file = tmp_path / "my.otconfig"
    file.write_text("{}")
    return Given(file=file)


def create_target(given: Given) -> NoOtconfigUpload:
    return NoOtconfigUpload()


class TestNoOtconfigUpload:
    async def test_does_nothing(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)

        await create_target(given).upload(given.file, A_PREFIX)
