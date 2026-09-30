from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.state import CurrentKeyPrefix
from OTAnalytics.domain.orthophoto import OrthophotoNotFound
from OTAnalytics.plugin_s3.download_objects import DownloadCancelled
from OTAnalytics.plugin_s3.orthophoto import S3ObtainOrthophoto

KEY_PREFIX = S3KeyPrefix("projects/otfusion-demo/site-1")
LOCAL_FILE = Path("/staging/projects/otfusion-demo/site-1/map2.tiff")
ANY_FOLDER = Path("/anywhere")


@dataclass
class Given:
    download_objects: AsyncMock
    current_key_prefix: CurrentKeyPrefix


def create_given() -> Given:
    return Given(download_objects=AsyncMock(), current_key_prefix=CurrentKeyPrefix())


def setup_default(given: Given) -> Given:
    given.current_key_prefix.set(KEY_PREFIX)
    given.download_objects.download_all.return_value = [LOCAL_FILE]
    return given


def setup_with_failing_download(given: Given, failure: Exception) -> Given:
    given.download_objects.download_all.side_effect = failure
    return given


def create_target(given: Given) -> S3ObtainOrthophoto:
    return S3ObtainOrthophoto(given.download_objects, given.current_key_prefix)


class TestS3ObtainOrthophoto:
    async def test_downloads_the_key_under_the_prefix(self) -> None:
        given = setup_default(create_given())

        actual = await create_target(given).obtain(Path("map2.tiff"), ANY_FOLDER)

        assert actual == LOCAL_FILE
        keys = given.download_objects.download_all.call_args.args[0]
        assert keys == ["projects/otfusion-demo/site-1/map2.tiff"]

    @pytest.mark.parametrize("reference", ["../site-2/map.tiff", "/etc/map.tiff"])
    async def test_refuses_a_reference_outside_the_prefix(self, reference: str) -> None:
        given = setup_default(create_given())

        with pytest.raises(OrthophotoNotFound):
            await create_target(given).obtain(Path(reference), ANY_FOLDER)

        given.download_objects.download_all.assert_not_called()

    @pytest.mark.parametrize(
        "failure", [DownloadCancelled("cancel"), RuntimeError("network down")]
    )
    async def test_download_failure_becomes_orthophoto_not_found(
        self, failure: Exception
    ) -> None:
        given = setup_with_failing_download(setup_default(create_given()), failure)

        with pytest.raises(OrthophotoNotFound):
            await create_target(given).obtain(Path("map2.tiff"), ANY_FOLDER)
