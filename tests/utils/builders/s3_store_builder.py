"""Shared AsyncMock S3 store scaffolding for plugin_s3 unit tests."""

from unittest.mock import AsyncMock, MagicMock, Mock

from OTAnalytics.plugin_s3.store import S3Store
from tests.utils.builders.s3_config_builder import BUCKET


def create_store(client: AsyncMock, bucket: str = BUCKET) -> Mock:
    """A mock `S3Store` whose `client()` yields the given client.

    `client()` returns an async context manager, so the mock needs
    `__aenter__`/`__aexit__` rather than a plain return value.
    """
    store = Mock(spec=S3Store)
    context_manager = MagicMock()
    context_manager.__aenter__ = AsyncMock(return_value=client)
    context_manager.__aexit__ = AsyncMock(return_value=None)
    store.client.return_value = context_manager
    store.bucket = bucket
    return store
