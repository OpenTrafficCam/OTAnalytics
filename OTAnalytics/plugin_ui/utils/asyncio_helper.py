import asyncio
from typing import Coroutine


def run_async(coro: Coroutine) -> None:
    # Schedule the asynchronous removal so tests see the call immediately
    # while NiceGUI executes the coroutine in the event loop.
    try:
        asyncio.create_task(coro)
    except RuntimeError:
        # No running loop available; run the coroutine to completion
        asyncio.run(coro)
