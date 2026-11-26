"""Tests the right panel: layers and the track reference point."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.element import Element
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    VisualizationOffsetSliderKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers import (
    VisualizationLayers,
)

ENDPOINT = "/test-visualization-layers"
LAYERS = "layers form"
OFFSET = "offset slider form"
TRACK_REFERENCE_POINT = "Track reference point"


def part(text: str) -> Mock:
    part = Mock()
    part.build.side_effect = lambda: ui.label(text)
    return part


def texts_in_order(element: Element) -> list[str]:
    texts = [element.text] if isinstance(element, ui.label) else []
    for child in element.default_slot.children:
        texts.extend(texts_in_order(child))
    return texts


class TestVisualizationLayers:
    async def test_shows_track_reference_point_below_the_layers(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = VisualizationLayers(resource_manager, part(LAYERS), part(OFFSET))

        @ui.page(ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT)

        assert user.client is not None
        texts = [
            text
            for text in texts_in_order(user.client.layout)
            if text in (LAYERS, TRACK_REFERENCE_POINT, OFFSET)
        ]
        assert texts == [LAYERS, TRACK_REFERENCE_POINT, OFFSET]
        await user.should_see(
            resource_manager.get(VisualizationOffsetSliderKeys.LABEL_DESCRIPTION)
        )
