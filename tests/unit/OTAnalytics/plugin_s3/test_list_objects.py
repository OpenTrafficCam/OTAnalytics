"""Tests for S3ListObjects."""

from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock

from OTAnalytics.plugin_s3.list_objects import S3ListObjects
from tests.unit.OTAnalytics.plugin_s3.s3_config_builder import BUCKET, create_s3_config
from tests.unit.OTAnalytics.plugin_s3.s3_connection_builder import create_connection

PREFIX = "project-1/site-1/OTCamera04/"

KEY_1 = f"{PREFIX}OTCamera04_2026-08-27_06-00-00.ottrk"
KEY_2 = f"{PREFIX}OTCamera04_2026-08-27_06-00-00.mp4"
KEY_3 = f"{PREFIX}OTCamera04_2026-08-27_06-15-00.ottrk"


@dataclass
class Given:
    client: AsyncMock
    connection: Mock


def create_given() -> Given:
    client = AsyncMock()
    return Given(client=client, connection=create_connection(client))


def create_target(given: Given) -> S3ListObjects:
    return S3ListObjects(connection=given.connection, config=create_s3_config())


class TestS3ListObjects:
    async def test_list_keys_single_page(self) -> None:
        given = create_given()
        given.client.list_objects_v2.return_value = {
            "Contents": [{"Key": KEY_1}, {"Key": KEY_2}, {"Key": KEY_3}],
            "IsTruncated": False,
        }
        target = create_target(given)

        actual = await target.list_keys(PREFIX)

        assert actual == [KEY_1, KEY_2, KEY_3]
        given.client.list_objects_v2.assert_awaited_once_with(
            Bucket=BUCKET, Prefix=PREFIX
        )

    async def test_list_keys_follows_continuation_token(self) -> None:
        """A truncated response is followed until IsTruncated is false.

        # Requirement OP#10256
        """
        given = create_given()
        given.client.list_objects_v2.side_effect = [
            {
                "Contents": [{"Key": KEY_1}],
                "IsTruncated": True,
                "NextContinuationToken": "token-1",
            },
            {
                "Contents": [{"Key": KEY_2}],
                "IsTruncated": True,
                "NextContinuationToken": "token-2",
            },
            {"Contents": [{"Key": KEY_3}], "IsTruncated": False},
        ]
        target = create_target(given)

        actual = await target.list_keys(PREFIX)

        assert actual == [KEY_1, KEY_2, KEY_3]
        assert [
            call.kwargs.get("ContinuationToken")
            for call in given.client.list_objects_v2.await_args_list
        ] == [None, "token-1", "token-2"]

    async def test_list_keys_empty_prefix_returns_nothing(self) -> None:
        given = create_given()
        given.client.list_objects_v2.return_value = {"IsTruncated": False}
        target = create_target(given)

        actual = await target.list_keys(PREFIX)

        assert actual == []
