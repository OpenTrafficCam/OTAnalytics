"""Shared AsyncMock S3 connection scaffolding for plugin_s3 unit tests."""

from unittest.mock import AsyncMock, MagicMock, Mock

from OTAnalytics.plugin_s3.connect import S3Connection


def create_connection(client: AsyncMock) -> Mock:
    """A mock `S3Connection` whose `establish()` yields the given client.

    `establish()` returns an async context manager, so the mock needs
    `__aenter__`/`__aexit__` rather than a plain return value.
    """
    connection = Mock(spec=S3Connection)
    context_manager = MagicMock()
    context_manager.__aenter__ = AsyncMock(return_value=client)
    context_manager.__aexit__ = AsyncMock(return_value=None)
    connection.establish.return_value = context_manager
    return connection
