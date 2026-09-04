"""Tests for S3Download."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.plugin_s3.download import S3Download
from tests.unit.OTAnalytics.plugin_s3.s3_config_builder import BUCKET, create_s3_config
from tests.unit.OTAnalytics.plugin_s3.s3_connection_builder import create_connection

KEY = "project-1/site-1/OTCamera04/OTCamera04_2026-08-27_06-00-00.ottrk"
PAYLOAD = b"ottrk-bytes"


@dataclass
class Given:
    client: AsyncMock
    connection: Mock


def create_given(payload: bytes = PAYLOAD) -> Given:
    body = AsyncMock()
    body.read = AsyncMock(return_value=payload)
    client = AsyncMock()
    client.get_object = AsyncMock(return_value={"Body": body})
    return Given(client=client, connection=create_connection(client))


def create_target(given: Given) -> S3Download:
    return S3Download(connection=given.connection, config=create_s3_config())


class TestS3Download:
    async def test_download_writes_payload_to_destination(self, tmp_path: Path) -> None:
        given = create_given()
        target = create_target(given)
        destination = tmp_path / "downloaded.ottrk"

        await target.download(key=KEY, dst=destination)

        assert destination.read_bytes() == PAYLOAD
        given.client.get_object.assert_awaited_once_with(Bucket=BUCKET, Key=KEY)

    async def test_download_creates_missing_parent_directories(
        self, tmp_path: Path
    ) -> None:
        """The staging tree mirrors S3 keys, so parents rarely exist yet.

        # Requirement OP#10256
        """
        given = create_given()
        target = create_target(given)
        destination = tmp_path / "project-1" / "site-1" / "OTCamera04" / "a.ottrk"
        assert not destination.parent.exists()

        await target.download(key=KEY, dst=destination)

        assert destination.read_bytes() == PAYLOAD
