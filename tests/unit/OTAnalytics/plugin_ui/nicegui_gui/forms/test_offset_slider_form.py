"""Tests the visualization of the track reference point."""

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.plugin_ui.nicegui_gui.forms.offset_slider_form import (
    MARKER_OFFSET_POINT,
    MARKER_OFFSET_X_VALUE,
    MARKER_OFFSET_Y_VALUE,
    OffsetSliderForm,
)

ENDPOINT = "/test-offset"


async def open_form(user: User, target: OffsetSliderForm) -> None:
    @ui.page(ENDPOINT)
    def page() -> None:
        target.build()

    await user.open(ENDPOINT)


def point_position(user: User) -> tuple[str, str]:
    point = user.find(marker=MARKER_OFFSET_POINT).elements.pop()
    return point._style["left"], point._style["top"]


def value_text(user: User, marker: str) -> str:
    label = user.find(marker=marker).elements.pop()
    assert isinstance(label, ui.label)
    return label.text


class TestOffsetVisualization:
    async def test_shows_the_initial_offset(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = OffsetSliderForm(
            resource_manager, initial_offset=RelativeOffsetCoordinate(0.5, 1.0)
        )

        await open_form(user, target)

        assert point_position(user) == ("50%", "100%")
        assert value_text(user, MARKER_OFFSET_X_VALUE) == "0.50"
        assert value_text(user, MARKER_OFFSET_Y_VALUE) == "1.00"

    async def test_follows_the_sliders(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = OffsetSliderForm(resource_manager)
        await open_form(user, target)

        assert target.x_offset_slider is not None
        target.x_offset_slider.set_value(0.2)

        assert point_position(user) == ("20%", "50%")
        assert value_text(user, MARKER_OFFSET_X_VALUE) == "0.20"

    async def test_follows_an_offset_set_from_outside(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """E.g. the offset of the selected section."""
        target = OffsetSliderForm(resource_manager)
        await open_form(user, target)

        target.set_offset(RelativeOffsetCoordinate(0.1, 0.9))

        assert point_position(user) == ("10%", "90%")
        assert value_text(user, MARKER_OFFSET_Y_VALUE) == "0.90"
