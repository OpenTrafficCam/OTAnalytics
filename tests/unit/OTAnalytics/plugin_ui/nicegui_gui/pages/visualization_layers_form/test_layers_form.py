"""Tests that the layer checkboxes follow the layers they show."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.plotting import LayerGroup, PlottingLayer
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
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
