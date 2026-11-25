"""Tests that the layer checkboxes follow the layers they show."""

from typing import Any
from unittest.mock import MagicMock, Mock, patch

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.plotting import LayerGroup, PlottingLayer
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.constants import TestIdAttributes
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_VISUALIZATION_LAYERS_ALL,
    LayersForm,
    layer_marker,
)
from OTAnalytics.plugin_ui.visualization.visualization import ALL, INTERSECTING_SECTIONS

LAYER_NAME = "Background"
SHOW_TRACKS = "Show tracks"
SHOW_START_END_POINTS = "Show start and end points"
LAYERS_FORM_UI = (
    "OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form.ui"
)


def layer(name: str) -> PlottingLayer:
    return PlottingLayer(name, Mock(), enabled=False)


def marked_test_ids(ui: Any) -> list[str]:
    prefix = f"{TestIdAttributes.DATA_TESTID}="
    return [
        props.args[0].removeprefix(prefix)
        for props in ui.checkbox.return_value.props.call_args_list
        if props.args and props.args[0].startswith(prefix)
    ]


class TestLayerMarker:
    def test_marker_of_group_and_layer(self) -> None:
        marker = layer_marker(SHOW_START_END_POINTS, INTERSECTING_SECTIONS)

        assert marker == (
            "marker-visualization-layers"
            "-show-start-and-end-points-intersecting-sections"
        )

    def test_same_layer_name_in_other_group_has_other_marker(self) -> None:
        assert layer_marker(SHOW_TRACKS, ALL) != layer_marker(
            SHOW_START_END_POINTS, ALL
        )


class TestLayersForm:
    def test_introduces_itself_to_the_view_model(
        self, resource_manager: ResourceManager
    ) -> None:
        viewmodel = Mock()

        target = LayersForm(viewmodel, resource_manager, [])

        viewmodel.set_frame_track_plotting.assert_called_once_with(target)

    @patch(LAYERS_FORM_UI)
    def test_every_layer_checkbox_is_marked(self, ui: MagicMock) -> None:
        groups = [
            LayerGroup(SHOW_TRACKS, [layer(ALL), layer(INTERSECTING_SECTIONS)]),
            LayerGroup(SHOW_START_END_POINTS, [layer(ALL)]),
        ]
        form = LayersForm(Mock(spec=ViewModel), Mock(spec=ResourceManager), groups)

        form.build()

        assert marked_test_ids(ui) == [
            MARKER_VISUALIZATION_LAYERS_ALL,
            layer_marker(SHOW_TRACKS, INTERSECTING_SECTIONS),
            layer_marker(SHOW_START_END_POINTS, ALL),
        ]

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
