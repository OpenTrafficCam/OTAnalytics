import asyncio
from unittest.mock import AsyncMock, Mock

from nicegui import events
from nicegui.testing import User

ROW_DOUBLE_CLICK_EVENT = "rowDblclick"
MAX_WAIT_ITERATIONS = 100


def double_click_row(user: User, marker: str, row: dict) -> None:
    """Simulate a double click on a row of the table with the given marker.

    NiceGUI's ``User.trigger`` sends events without arguments. Quasar emits
    ``rowDblclick`` with the arguments ``(event, row, index)``, which is what the
    listeners of the table receive here.
    """
    assert user.client
    with user.client:
        for element in user.find(marker=marker).elements:
            for listener in element._event_listeners.values():
                if listener.type != ROW_DOUBLE_CLICK_EVENT:
                    continue
                event_arguments = events.GenericEventArguments(
                    sender=element, client=user.client, args=[{}, row, 0]
                )
                events.handle_event(listener.handler, event_arguments)


async def wait_until_awaited(mock: AsyncMock) -> None:
    """Give background tasks started by event handlers time to await the mock."""
    for _ in range(MAX_WAIT_ITERATIONS):
        if mock.await_count:
            return
        await asyncio.sleep(0.01)


async def wait_until_called(mock: Mock) -> None:
    """Give background tasks started by event handlers time to call the mock."""
    for _ in range(MAX_WAIT_ITERATIONS):
        if mock.call_count:
            return
        await asyncio.sleep(0.01)
