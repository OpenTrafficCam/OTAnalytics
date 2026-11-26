"""Tests of the form showing the visualization layers."""

import asyncio
from unittest.mock import AsyncMock, Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.plotting import LayerGroup, PlottingLayer
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_UPDATE_FLOW_HIGHLIGHTING,
    LayersForm,
)

LAYER_NAME = "Background"


class TestLayersForm:
    def test_introduces_itself_to_the_view_model(
        self, resource_manager: ResourceManager
    ) -> None:
        viewmodel = Mock()

        target = LayersForm(viewmodel, resource_manager, [])

        viewmodel.set_frame_track_plotting.assert_called_once_with(target)

    async def test_checkbox_enables_the_layer(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        layer = PlottingLayer(LAYER_NAME, Mock(), enabled=False)
        target = LayersForm(Mock(), resource_manager, [LayerGroup("Group", [layer])])

        @ui.page("/test")
        def page() -> None:
            target.build()

        await user.open("/test")
        user.find(LAYER_NAME).click()

        assert layer.is_enabled()

    async def test_checkbox_follows_a_layer_reset(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """Resetting the application resets the layers, not the checkboxes."""
        layer = PlottingLayer(LAYER_NAME, Mock(), enabled=True)
        target = LayersForm(Mock(), resource_manager, [LayerGroup("Group", [layer])])

        @ui.page("/test")
        def page() -> None:
            target.build()

        await user.open("/test")
        user.find(LAYER_NAME).click()

        layer.reset()

        checkbox = user.find(LAYER_NAME).elements.pop()
        assert isinstance(checkbox, ui.checkbox)
        assert checkbox.value is True

    async def test_creates_events_only_once_at_a_time(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        release = asyncio.Event()
        viewmodel = Mock()
        viewmodel.create_events_async = AsyncMock(side_effect=release.wait)
        target = LayersForm(viewmodel, resource_manager, [])

        @ui.page("/test")
        def page() -> None:
            target.build()

        await user.open("/test")
        user.find(marker=MARKER_UPDATE_FLOW_HIGHLIGHTING).click()
        user.find(marker=MARKER_UPDATE_FLOW_HIGHLIGHTING).click()
        await asyncio.sleep(0)
        release.set()
        await asyncio.sleep(0)
        user.find(marker=MARKER_UPDATE_FLOW_HIGHLIGHTING).click()
        await asyncio.sleep(0)

        assert viewmodel.create_events_async.await_count == 2
