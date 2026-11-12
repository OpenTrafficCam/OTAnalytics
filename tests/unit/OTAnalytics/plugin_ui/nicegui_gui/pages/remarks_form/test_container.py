"""Tests the form once the browser that showed its page has gone away."""

import asyncio
import gc
import weakref
from dataclasses import dataclass
from unittest.mock import Mock

from nicegui import Client, context, ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.pages.remarks_form.container import RemarkForm

A_REMARK = "Counted at the northern approach"
PAGE_WITH_FORM = "/with-form"
PAGE_ELSEWHERE = "/elsewhere"
COLLECTION_ATTEMPTS = 50
COLLECTION_INTERVAL_SECONDS = 0.01


class TestAfterThePageIsGone:
    async def test_loading_a_remark_does_not_raise(self, user: User) -> None:
        """The form outlives the page it was built into: it is created once and
        rebuilt on every visit. Once that visit's browser has left, NiceGUI
        deletes the client, and loading a remark reached for it and raised
        `RuntimeError`, failing every otconfig loaded after the first page visit.

        @bug by randy-seng
        """
        target = create_target(create_given())
        client_ids: list[str] = []

        @ui.page(PAGE_WITH_FORM)
        def page_with_form() -> None:
            target.build()
            client_ids.append(context.client.id)

        @ui.page(PAGE_ELSEWHERE)
        def page_elsewhere() -> None:
            ui.label("elsewhere")

        await user.open(PAGE_WITH_FORM)
        await leave_page(user, client_ids[0])

        target.load_remark()


async def leave_page(user: User, client_id: str) -> None:
    """Navigate away and let NiceGUI delete the page's client, as it does once the
    browser has left.

    Elements hold their client only weakly, so they notice it is gone only once it
    has been collected. Opening another page first makes the test user let go of
    it; the client's outbox loop lets go once it notices the deletion.
    """
    await user.open(PAGE_ELSEWHERE)
    client = Client.instances[client_id]
    collected = weakref.ref(client)
    client.delete()
    del client
    for _ in range(COLLECTION_ATTEMPTS):
        await asyncio.sleep(COLLECTION_INTERVAL_SECONDS)
        gc.collect()
        if collected() is None:
            return
    raise AssertionError("The deleted client was never collected")


@dataclass
class Given:
    resource_manager: Mock
    view_model: Mock


def create_given() -> Given:
    resource_manager = Mock()
    resource_manager.get.return_value = "label"
    view_model = Mock()
    view_model.get_remark.return_value = A_REMARK
    return Given(resource_manager=resource_manager, view_model=view_model)


def create_target(given: Given) -> RemarkForm:
    return RemarkForm(given.resource_manager, given.view_model)
