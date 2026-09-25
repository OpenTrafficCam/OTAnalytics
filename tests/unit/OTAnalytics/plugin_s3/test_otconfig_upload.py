from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.plugin_s3.otconfig_upload import S3OtconfigUpload
from OTAnalytics.plugin_s3.upload import S3Upload

PREFIX = S3KeyPrefix("project-1/site-2/otcamera19")


@dataclass
class Given:
    upload: AsyncMock


def create_given() -> Given:
    return Given(upload=AsyncMock(spec=S3Upload))


def create_target(given: Given) -> S3OtconfigUpload:
    return S3OtconfigUpload(upload=given.upload)


class TestS3OtconfigUpload:
    async def test_uploads_under_the_prefix_by_file_name(self, tmp_path: Path) -> None:
        given = create_given()
        target = create_target(given)
        file = tmp_path / "my_project.otconfig"

        await target.upload(file, PREFIX)

        given.upload.upload.assert_awaited_once_with(
            src=file, key="project-1/site-2/otcamera19/my_project.otconfig"
        )
