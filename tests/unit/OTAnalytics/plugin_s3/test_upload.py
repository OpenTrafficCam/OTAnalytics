"""Tests for S3Upload.

`S3Upload` is not used by the S3 time-selection epic; it is copied alongside the
rest of the S3 client layer for the later result-upload work. It is tested here
so it does not sit in the tree unverified.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.plugin_s3.upload import S3Upload
from tests.utils.builders.s3_config_builder import BUCKET
from tests.utils.builders.s3_store_builder import create_store

KEY = "project-1/site-1/OTCamera04/events.otevents"
PAYLOAD = b"event-bytes"


@dataclass
class Given:
    client: AsyncMock
    store: Mock


def create_given() -> Given:
    client = AsyncMock()
    return Given(client=client, store=create_store(client))


def create_target(given: Given) -> S3Upload:
    return S3Upload(store=given.store)


class TestS3Upload:
    async def test_upload_sends_file_contents(self, tmp_path: Path) -> None:
        given = create_given()
        target = create_target(given)
        source = tmp_path / "events.otevents"
        source.write_bytes(PAYLOAD)

        await target.upload(src=source, key=KEY)

        given.client.put_object.assert_awaited_once_with(
            Bucket=BUCKET, Key=KEY, Body=PAYLOAD
        )

    async def test_upload_sets_content_type_when_given(self, tmp_path: Path) -> None:
        given = create_given()
        target = create_target(given)
        source = tmp_path / "events.otevents"
        source.write_bytes(PAYLOAD)

        await target.upload(src=source, key=KEY, content_type="application/json")

        given.client.put_object.assert_awaited_once_with(
            Bucket=BUCKET,
            Key=KEY,
            Body=PAYLOAD,
            ContentType="application/json",
        )
