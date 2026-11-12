from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.elements.button import Button
from nicegui.testing import User

from OTAnalytics.adapter_ui.abstract_frame_offset import AbstractFrameOffset
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.visualization_offset_slider_form import (  # noqa
    MARKER_UPDATE_OFFSET,
    VisualizationOffSetSliderForm,
)

ENDPOINT_NAME = "/test-visualization-offset-slider-form"


@pytest.fixture
def viewmodel() -> Mock:
    return MagicMock(spec=ViewModel)


@pytest.fixture
def offset_form(
    viewmodel: ViewModel, resource_manager: ResourceManager
) -> VisualizationOffSetSliderForm:
    return VisualizationOffSetSliderForm(viewmodel, resource_manager)


class TestVisualizationOffSetSliderForm:
    @pytest.mark.asyncio
    async def test_build_applies_button_state_from_viewmodel(
        self,
        user: User,
        offset_form: VisualizationOffSetSliderForm,
        viewmodel: Mock,
    ) -> None:
        """Test that the button state of the viewmodel is applied after building."""

        def disable_button(frame: AbstractFrameOffset) -> None:
            frame.enable_update_offset_button(False)

        viewmodel.set_offset_frame.side_effect = disable_button

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            offset_form.build()

        await user.open(ENDPOINT_NAME)

        button = user.find(kind=Button, marker=MARKER_UPDATE_OFFSET).elements.pop()
        assert not button.enabled
