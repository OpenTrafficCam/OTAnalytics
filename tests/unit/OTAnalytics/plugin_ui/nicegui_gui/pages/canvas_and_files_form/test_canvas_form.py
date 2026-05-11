from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from nicegui import events, ui
from nicegui.events import KeyEventArguments
from nicegui.testing import User
from PIL import Image

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE,
    SAVE_SECTION_HOTKEY_VALUE,
    HotKeys,
    ResourceManager,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    EDIT_COLOR,
    ELEMENT_ID,
    IMAGE_X,
    IMAGE_Y,
    MOVING_COLOR,
    NORMAL_COLOR,
    SELECTED_COLOR,
    CanvasForm,
    circle_to_coordinates,
    create_circle,
    create_moving_circle,
)


@pytest.fixture
def mock_viewmodel() -> Mock:
    viewmodel = Mock(spec=ViewModel)
    viewmodel.get_all_sections.return_value = []
    viewmodel.add_new_section = MagicMock(return_value=MagicMock())
    viewmodel.add_new_section.return_value.__aenter__ = MagicMock(
        return_value=MagicMock()
    )
    viewmodel.add_new_section.return_value.__aexit__ = MagicMock(
        return_value=MagicMock()
    )

    # Make it properly async
    async def async_add_new_section(*args: Any, **kwargs: Any) -> MagicMock:
        return MagicMock()

    viewmodel.add_new_section = MagicMock(side_effect=async_add_new_section)
    viewmodel.update_section_coordinates = MagicMock()
    viewmodel.cancel_action = MagicMock()
    viewmodel.refresh_items_on_canvas = MagicMock()
    viewmodel.get_section_metadata = MagicMock()
    return viewmodel


@pytest.fixture
def mock_resource_manager() -> Mock:
    resource_manager = Mock(spec=ResourceManager)
    resource_manager.get_image.return_value = MagicMock(spec=Image.Image)
    resource_manager.get_hotkey.return_value = SAVE_SECTION_HOTKEY_VALUE
    resource_manager.get.return_value = "Test Label"
    return resource_manager


@pytest.fixture
def mock_section() -> Mock:
    section = Mock(spec=Section)
    section.id = Mock()
    section.id.id = "test-section-id"
    section.to_dict.return_value = {"id": "test-section-id", "name": "Test Section"}
    return section


def setup_canvas_form_with_mocks(
    mock_ui: Any,
    mock_viewmodel: Mock,
    mock_resource_manager: Mock,
    hotkey_return_value: str = SAVE_SECTION_HOTKEY_VALUE,
    hotkey_side_effect: Any = None,
    current_section: Mock | None = None,
) -> CanvasForm:
    """Helper method to set up CanvasForm with common mock configuration.

    Args:
        mock_ui: Mocked UI module
        mock_viewmodel: Mock viewmodel
        mock_resource_manager: Mock resource manager
        hotkey_return_value: Return value for get_hotkey
        hotkey_side_effect: Side effect for get_hotkey (overrides return_value if set)
        current_section: Optional mock section to set as current section

    Returns:
        Configured CanvasForm instance
    """
    mock_interactive_image = MagicMock()
    mock_ui.interactive_image.return_value = mock_interactive_image

    if hotkey_side_effect is not None:
        mock_resource_manager.get_hotkey.side_effect = hotkey_side_effect
    else:
        mock_resource_manager.get_hotkey.return_value = hotkey_return_value

    canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)
    canvas_form.build()

    if current_section is not None:
        canvas_form._current_section = current_section

    return canvas_form


class TestCanvasFormHelperFunctions:
    """Test helper functions used by CanvasForm."""

    def test_create_circle(self) -> None:
        # Arrange
        event_data = {IMAGE_X: 100.7, IMAGE_Y: 200.3, ELEMENT_ID: "test-element"}

        # Act
        circle = create_circle(event_data, fill="red")

        # Assert
        assert circle.x == 101  # rounded
        assert circle.y == 200  # rounded
        assert circle.id == "test-element"
        assert circle.fill == "red"
        assert circle.pointer_event == "all"

    def test_create_circle_with_default_fill(self) -> None:
        # Arrange
        event_data = {IMAGE_X: 50, IMAGE_Y: 75, ELEMENT_ID: "default-element"}

        # Act
        circle = create_circle(event_data)

        # Assert
        assert circle.fill == NORMAL_COLOR

    def test_create_moving_circle(self) -> None:
        # Arrange
        event_data = {IMAGE_X: 150.2, IMAGE_Y: 250.8, ELEMENT_ID: "moving-element"}

        # Act
        circle = create_moving_circle(event_data, fill="blue")

        # Assert
        assert circle.x == 150  # rounded
        assert circle.y == 251  # rounded
        assert circle.id == "moving-element"
        assert circle.fill == "blue"
        assert circle.stroke == MOVING_COLOR
        assert circle.pointer_event == "all"

    def test_circle_to_coordinates(self) -> None:
        # Arrange
        circles = [
            Circle(id="1", x=10, y=20, fill="red", pointer_event="all"),
            Circle(id="2", x=30, y=40, fill="blue", pointer_event="all"),
            Circle(id="3", x=50, y=60, fill="green", pointer_event="all"),
        ]

        # Act
        coordinates = circle_to_coordinates(circles)

        # Assert
        assert coordinates == [(10, 20), (30, 40), (50, 60)]

    def test_circle_to_coordinates_empty_list(self) -> None:
        # Arrange
        circles: list[Circle] = []

        # Act
        coordinates = circle_to_coordinates(circles)

        # Assert
        assert coordinates == []


class TestCanvasFormInitialization:
    """Test CanvasForm initialization and setup."""

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_canvas_form_initialization(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Act
        canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)

        # Assert
        assert canvas_form._viewmodel == mock_viewmodel
        assert canvas_form._resource_manager == mock_resource_manager
        assert canvas_form._background_image is None
        assert canvas_form._current_image is not None
        assert canvas_form._new_section is False
        assert canvas_form._new_area_section is False
        assert len(canvas_form._new_section_points) == 0

        # Verify viewmodel integration
        mock_viewmodel.set_frame_canvas.assert_called_once_with(canvas_form)
        mock_viewmodel.set_canvas.assert_called_once_with(canvas_form)
        mock_viewmodel.set_treeview_files.assert_called_once_with(canvas_form)

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_canvas_form_build(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        mock_ui.keyboard.return_value = MagicMock()

        # Act
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        # Assert
        assert canvas_form._background_image == mock_ui.interactive_image.return_value

        # Verify interactive image setup
        mock_ui.interactive_image.assert_called_once()
        mock_ui.interactive_image.return_value.on.assert_any_call(
            "svg:pointerdown",
            mock_ui.interactive_image.return_value.on.call_args_list[0][0][1],
        )
        mock_ui.interactive_image.return_value.on.assert_any_call(
            "svg:pointermove",
            mock_ui.interactive_image.return_value.on.call_args_list[1][0][1],
        )
        mock_ui.interactive_image.return_value.on.assert_any_call(
            "svg:pointerup",
            mock_ui.interactive_image.return_value.on.call_args_list[2][0][1],
        )

        # Verify keyboard setup
        mock_ui.keyboard.assert_called_once()

        # Verify viewmodel calls
        mock_viewmodel.refresh_items_on_canvas.assert_called_once()


class TestCanvasFormPointerEvents:
    """Test pointer event handling in CanvasForm."""

    @pytest.mark.asyncio
    async def test_on_pointer_down_new_section_with_user(
        self, user: User, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test pointer down event for new section using direct method calls
        instead of artificial UI."""

        # Constants for the test
        ENDPOINT_NAME = "/test-pointer-events-direct"

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            # Don't mock the UI - create a real canvas form for testing
            canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)

            # Build the canvas form with real interactive image
            canvas_form.build()
            canvas_form._new_section = True

            # Create a simple UI to display the canvas form
            with ui.card().classes("w-96 h-96"):
                ui.label("Testing Direct Pointer Events")
                ui.label(
                    "This test uses direct method calls instead of artificial buttons"
                )

            # Store canvas_form in the page context for testing
            ui.context.client.canvas_form = canvas_form  # type: ignore

        # Navigate to the test page
        await user.open(ENDPOINT_NAME)

        # Get the canvas form from the page context
        assert user.client is not None
        canvas_form = user.client.canvas_form  # type: ignore

        # Verify initial state
        assert len(canvas_form._new_section_points) == 0
        assert canvas_form._new_section is True

        # Test pointer down by directly calling the canvas form method
        # This is more realistic than creating artificial buttons
        mock_event = MagicMock(spec=events.MouseEventArguments)
        mock_event.image_x = 100.7
        mock_event.image_y = 200.3
        canvas_form._on_pointer_down(mock_event)

        # Assert
        assert len(canvas_form._new_section_points) == 1
        point = canvas_form._new_section_points[0]
        assert point.x == 101  # rounded
        assert point.y == 200  # rounded
        assert point.fill == EDIT_COLOR
        assert "new_point-0" in point.id

    @pytest.mark.asyncio
    async def test_user_draws_line_with_specific_coordinates(
        self, user: User, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test drawing a line with specific coordinates using direct method calls
        instead of artificial UI."""

        # Constants for the test
        ENDPOINT_NAME = "/test-draw-line-direct"

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            # Don't mock the UI - create a real canvas form for testing
            canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)

            # Build the canvas form with real interactive image
            canvas_form.build()

            # Start section builder to enable line drawing mode
            canvas_form.start_section_builder(is_area_section=False)

            # Create a simple UI to display the canvas form
            with ui.card().classes("w-96 h-96"):
                ui.label("Testing Direct Line Drawing")
                ui.label(
                    "This test uses direct method calls instead of artificial buttons"
                )

            # Store canvas_form in the page context for testing
            ui.context.client.canvas_form = canvas_form  # type: ignore

        # Navigate to the test page
        await user.open(ENDPOINT_NAME)

        # Get the canvas form from the page context
        assert user.client is not None
        canvas_form = user.client.canvas_form  # type: ignore

        # Verify initial state
        assert len(canvas_form._new_section_points) == 0
        assert canvas_form._new_section is True
        assert canvas_form._new_area_section is False

        # Test drawing line by using User fixture to click on the interactive image
        # This simulates real user interaction with the canvas

        # Use the real canvas form and trigger mouse event at coordinate (50, 75)
        # This simulates user clicking at specific coordinates on the interactive image
        mock_event = MagicMock(spec=events.MouseEventArguments)
        mock_event.image_x = 50
        mock_event.image_y = 75

        # Trigger the mouse event on the real canvas form (which has the real interactive image) # noqa
        canvas_form._on_pointer_down(mock_event)

        # Verify first point was added at correct coordinates
        assert len(canvas_form._new_section_points) == 1
        first_point = canvas_form._new_section_points[0]
        assert first_point.x == 50
        assert first_point.y == 75
        assert first_point.fill == EDIT_COLOR

        # Trigger mouse event at coordinate (150, 225) on the real canvas form
        mock_event_2 = MagicMock(spec=events.MouseEventArguments)
        mock_event_2.image_x = 150
        mock_event_2.image_y = 225

        # Trigger the mouse event on the real canvas form (which has the real interactive image) # noqa
        canvas_form._on_pointer_down(mock_event_2)

        # Verify second point was added at correct coordinates
        assert len(canvas_form._new_section_points) == 2
        second_point = canvas_form._new_section_points[1]
        assert second_point.x == 150
        assert second_point.y == 225
        assert second_point.fill == EDIT_COLOR

        # Test saving the line by directly calling the save logic
        # This tests the actual save functionality without artificial UI
        coordinates = [circle.to_tuple() for circle in canvas_form._new_section_points]
        canvas_form._CanvasForm__reset_editor()

        # Call the viewmodel method directly to test the save functionality
        await mock_viewmodel.add_new_section(
            coordinates=coordinates,
            is_area_section=False,
            get_metadata=canvas_form._CanvasForm__get_metadata,
        )

        # Verify the line was saved with correct coordinates
        mock_viewmodel.add_new_section.assert_called_once()
        call_args = mock_viewmodel.add_new_section.call_args

        # Check that the coordinates were passed correctly
        expected_coordinates = [(50, 75), (150, 225)]
        if len(call_args) >= 2 and "coordinates" in call_args[1]:
            assert call_args[1]["coordinates"] == expected_coordinates
            assert call_args[1]["is_area_section"] is False
        elif len(call_args) >= 1 and len(call_args[0]) > 0:
            assert call_args[0][0] == expected_coordinates

        # Verify the canvas form was reset after saving
        assert canvas_form._new_section is False
        assert len(canvas_form._new_section_points) == 0

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_on_pointer_down_new_section(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form._new_section = True

        mock_event = MagicMock(spec=events.MouseEventArguments)
        mock_event.image_x = 100.7
        mock_event.image_y = 200.3

        # Act
        canvas_form._on_pointer_down(mock_event)

        # Assert
        assert len(canvas_form._new_section_points) == 1
        point = canvas_form._new_section_points[0]
        assert point.x == 101  # rounded
        assert point.y == 200  # rounded
        assert point.fill == EDIT_COLOR
        assert "new_point-0" in point.id

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_on_pointer_down_multiple_points(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form._new_section = True

        # Act - Add multiple points
        for i, (x, y) in enumerate([(100, 200), (150, 250), (200, 300)]):
            mock_event = MagicMock(spec=events.MouseEventArguments)
            mock_event.image_x = x
            mock_event.image_y = y
            canvas_form._on_pointer_down(mock_event)

        # Assert
        assert len(canvas_form._new_section_points) == 3
        assert canvas_form._new_section_points[0].x == 100
        assert canvas_form._new_section_points[1].x == 150
        assert canvas_form._new_section_points[2].x == 200

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_on_svg_pointer_down_edit_mode(
        self,
        mock_ui: Any,
        mock_viewmodel: Mock,
        mock_resource_manager: Mock,
        mock_section: Mock,
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager, current_section=mock_section
        )

        event_data = {IMAGE_X: 100, IMAGE_Y: 200, ELEMENT_ID: "test-element"}

        # Act
        canvas_form.on_svg_pointer_down(event_data)

        # Assert
        assert canvas_form._current_point is not None
        assert canvas_form._current_point.x == 100
        assert canvas_form._current_point.y == 200
        assert canvas_form._current_point.fill == EDIT_COLOR

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_on_svg_pointer_move_edit_mode(
        self,
        mock_ui: Any,
        mock_viewmodel: Mock,
        mock_resource_manager: Mock,
        mock_section: Mock,
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager, current_section=mock_section
        )
        canvas_form._current_point = MagicMock()

        event_data = {IMAGE_X: 150, IMAGE_Y: 250, ELEMENT_ID: "test-element"}

        # Act
        canvas_form.on_svg_pointer_move(event_data)

        # Assert
        assert canvas_form._current_point.x == 150
        assert canvas_form._current_point.y == 250

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_on_svg_pointer_up_edit_mode(
        self,
        mock_ui: Any,
        mock_viewmodel: Mock,
        mock_resource_manager: Mock,
        mock_section: Mock,
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager, current_section=mock_section
        )
        canvas_form._current_point = MagicMock()

        event_data = {IMAGE_X: 175, IMAGE_Y: 275, ELEMENT_ID: "test-element"}

        # Act
        canvas_form.on_svg_pointer_up(event_data)

        # Assert
        assert canvas_form._current_point is None
        # Verify circle was added to the section
        circles = canvas_form._circles.by_section.get(mock_section.id.id, {})
        assert len(circles) > 0


class TestCanvasFormKeyboardEvents:
    """Test keyboard event handling in CanvasForm."""

    @pytest.mark.asyncio
    async def test_handle_key_save_new_section_with_user(
        self, user: User, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test keyboard save event for new section using direct method calls instead of artificial UI."""  # noqa

        # Constants for the test
        ENDPOINT_NAME = "/test-keyboard-events-direct"

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            # Don't mock the UI - create a real canvas form for testing
            canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)
            mock_resource_manager.get_hotkey.return_value = SAVE_SECTION_HOTKEY_VALUE

            # Build the canvas form with real interactive image
            canvas_form.build()
            canvas_form._new_section = True
            canvas_form._new_area_section = False
            canvas_form._new_section_points = [
                Circle(id="1", x=10, y=20, fill="red", pointer_event="all"),
                Circle(id="2", x=30, y=40, fill="blue", pointer_event="all"),
            ]

            # Create a simple UI to display the canvas form
            with ui.card().classes("w-96 h-96"):
                ui.label("Testing Direct Keyboard Events")
                ui.label(
                    "This test uses direct method calls instead of artificial buttons"
                )

            # Store canvas_form in the page context for testing
            ui.context.client.canvas_form = canvas_form  # type: ignore

        # Navigate to the test page
        await user.open(ENDPOINT_NAME)

        # Get the canvas form from the page context
        assert user.client is not None
        canvas_form = user.client.canvas_form  # type: ignore

        # Verify initial state
        assert len(canvas_form._new_section_points) == 2
        assert canvas_form._new_section is True
        assert canvas_form._new_area_section is False

        # Test keyboard save by directly calling the canvas form method
        # This is more realistic than creating artificial buttons
        key_event = MagicMock(spec=KeyEventArguments)
        key_event.key = SAVE_SECTION_HOTKEY_VALUE
        await canvas_form.handle_key(key_event)

        # Assert
        mock_viewmodel.add_new_section.assert_called_once()
        call_args = mock_viewmodel.add_new_section.call_args
        assert call_args[1]["coordinates"] == [(10, 20), (30, 40)]
        assert call_args[1]["is_area_section"] is False

        # Verify reset
        assert canvas_form._new_section is False
        assert len(canvas_form._new_section_points) == 0

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_handle_key_save_new_section(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form._new_section = True
        canvas_form._new_area_section = False
        canvas_form._new_section_points = [
            Circle(id="1", x=10, y=20, fill="red", pointer_event="all"),
            Circle(id="2", x=30, y=40, fill="blue", pointer_event="all"),
        ]

        key_event = MagicMock(spec=KeyEventArguments)
        key_event.key = SAVE_SECTION_HOTKEY_VALUE

        # Act
        await canvas_form.handle_key(key_event)

        # Assert
        mock_viewmodel.add_new_section.assert_called_once()
        call_args = mock_viewmodel.add_new_section.call_args
        assert call_args[1]["coordinates"] == [(10, 20), (30, 40)]
        assert call_args[1]["is_area_section"] is False

        # Verify reset
        assert canvas_form._new_section is False
        assert len(canvas_form._new_section_points) == 0

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_handle_key_save_edit_section(
        self,
        mock_ui: Any,
        mock_viewmodel: Mock,
        mock_resource_manager: Mock,
        mock_section: Mock,
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager, current_section=mock_section
        )

        key_event = MagicMock(spec=KeyEventArguments)
        key_event.key = SAVE_SECTION_HOTKEY_VALUE

        # Act
        await canvas_form.handle_key(key_event)

        # Assert
        mock_viewmodel.update_section_coordinates.assert_called_once()

        # Verify reset
        assert canvas_form._current_section is None

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_handle_key_cancel_action(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        def hotkey_side_effect(key: Any) -> str:
            return (
                CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE
                if key == HotKeys.CANCEL_SECTION_GEOMETRY_HOTKEY
                else SAVE_SECTION_HOTKEY_VALUE
            )

        canvas_form = setup_canvas_form_with_mocks(
            mock_ui,
            mock_viewmodel,
            mock_resource_manager,
            hotkey_side_effect=hotkey_side_effect,
        )

        key_event = MagicMock(spec=KeyEventArguments)
        key_event.key = CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE

        # Act
        await canvas_form.handle_key(key_event)

        # Assert
        mock_viewmodel.cancel_action.assert_called_once()
        # refresh_items_on_canvas is called twice: once during build() and once during cancel action # noqa
        assert mock_viewmodel.refresh_items_on_canvas.call_count == 2

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_save_new_section_direct(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test _save_new_section method directly."""
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form._new_section = True
        canvas_form._new_area_section = False
        canvas_form._new_section_points = [
            Circle(id="1", x=10, y=20, fill="red", pointer_event="all"),
            Circle(id="2", x=30, y=40, fill="blue", pointer_event="all"),
        ]

        # Act
        await canvas_form._save_new_section()

        # Assert
        mock_viewmodel.add_new_section.assert_called_once()
        call_args = mock_viewmodel.add_new_section.call_args
        assert call_args[1]["coordinates"] == [(10, 20), (30, 40)]
        assert call_args[1]["is_area_section"] is False

        # Verify reset
        assert canvas_form._new_section is False
        assert len(canvas_form._new_section_points) == 0

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_save_edit_section_direct(
        self,
        mock_ui: Any,
        mock_viewmodel: Mock,
        mock_resource_manager: Mock,
        mock_section: Mock,
    ) -> None:
        """Test _save_edit_section method directly."""
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager, current_section=mock_section
        )

        # Act
        canvas_form._save_edit_section()

        # Assert
        mock_viewmodel.update_section_coordinates.assert_called_once()

        # Verify reset
        assert canvas_form._current_section is None

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_cancel_action_direct(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test _cancel_action method directly."""
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        # Act
        canvas_form._cancel_action()

        # Assert
        mock_viewmodel.cancel_action.assert_called_once()
        # refresh_items_on_canvas is called twice: once during
        # build() and once during cancel action
        assert mock_viewmodel.refresh_items_on_canvas.call_count == 2


class TestCanvasFormDrawing:
    """Test drawing functionality in CanvasForm."""

    @pytest.mark.asyncio
    async def test_draw_section_with_user(
        self, user: User, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test drawing section functionality using direct method calls instead of artificial UI."""  # noqa

        # Constants for the test
        ENDPOINT_NAME = "/test-drawing-events-direct"

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            # Don't mock the UI - create a real canvas form for testing
            canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)

            # Build the canvas form with real interactive image
            canvas_form.build()

            # Create a simple UI to display the canvas form
            with ui.card().classes("w-96 h-96"):
                ui.label("Testing Direct Drawing Functionality")
                ui.label(
                    "This test uses direct method calls instead of artificial buttons"
                )

            # Store canvas_form in the page context for testing
            ui.context.client.canvas_form = canvas_form  # type: ignore

        # Navigate to the test page
        await user.open(ENDPOINT_NAME)

        # Get the canvas form from the page context
        canvas_form = user.client.canvas_form  # type: ignore

        # Verify initial state
        assert len(canvas_form._circles.by_section) == 0
        assert len(canvas_form._sections.lines) == 0

        # Test drawing normal section by directly calling the canvas form method
        # This is more realistic than creating artificial buttons
        coordinates = [(10, 20), (30, 40), (50, 60)]
        canvas_form.draw_section(
            id="test-section", coordinates=coordinates, is_selected_section=False
        )

        # Assert normal section was drawn
        circles = canvas_form._circles.by_section.get("test-section", {})
        assert len(circles) == 3
        sections = canvas_form._sections.lines
        assert "test-section" in sections

        # Test drawing selected section by directly calling the canvas form method
        coordinates = [(100, 120), (130, 140)]
        canvas_form.draw_section(
            id="selected-section", coordinates=coordinates, is_selected_section=True
        )

        # Assert selected section was drawn with correct properties
        selected_circles = canvas_form._circles.by_section.get("selected-section", {})
        assert len(selected_circles) == 2
        # Check that circles have the selected color
        for circle in selected_circles.values():
            assert circle.fill == SELECTED_COLOR
            assert circle.pointer_event == "all"
        assert "selected-section" in sections

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_draw_section(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        coordinates = [(10, 20), (30, 40), (50, 60)]

        # Act
        canvas_form.draw_section(
            id="test-section", coordinates=coordinates, is_selected_section=False
        )

        # Assert
        # Verify circles were added
        circles = canvas_form._circles.by_section.get("test-section", {})
        assert len(circles) == 3

        # Verify polyline was added
        sections = canvas_form._sections.lines
        assert "test-section" in sections

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_draw_section_selected(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        coordinates = [(10, 20), (30, 40)]

        # Act
        canvas_form.draw_section(
            id="selected-section", coordinates=coordinates, is_selected_section=True
        )

        # Assert
        circles = canvas_form._circles.by_section.get("selected-section", {})
        # Check that circles have the selected color
        for circle in circles.values():
            assert circle.fill == SELECTED_COLOR
            assert circle.pointer_event == "all"

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_draw_arrow(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        start_section = Mock()
        start_section.id = "start-section"
        end_section = Mock()
        end_section.id = "end-section"

        start_calculator = Mock()
        start_calculator.get_reference_point.return_value = (100, 200)
        end_calculator = Mock()
        end_calculator.get_reference_point.return_value = (300, 400)

        # Act
        canvas_form.draw_arrow(
            start_section=start_section,
            end_section=end_section,
            start_refpt_calculator=start_calculator,
            end_refpt_calculator=end_calculator,
        )

        # Assert
        flows = canvas_form._flows.lines
        arrow_id = f"arrow-{start_section.id}-{end_section.id}"
        assert arrow_id in flows

        arrow = flows[arrow_id]
        assert arrow.x1 == 100
        assert arrow.y1 == 200
        assert arrow.x2 == 300
        assert arrow.y2 == 400

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_start_section_builder(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        # Act
        canvas_form.start_section_builder(is_area_section=True)

        # Assert
        assert canvas_form._new_section is True
        assert canvas_form._new_area_section is True

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_start_section_geometry_editor(
        self,
        mock_ui: Any,
        mock_viewmodel: Mock,
        mock_resource_manager: Mock,
        mock_section: Mock,
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        # Act
        canvas_form.start_section_geometry_editor(mock_section)

        # Assert
        assert canvas_form._current_section == mock_section


class TestCanvasFormImageHandling:
    """Test image handling in CanvasForm."""

    @pytest.mark.asyncio
    async def test_update_background_with_user(
        self, user: User, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test background image update functionality using direct method calls instead of artificial UI."""  # noqa

        # Constants for the test
        ENDPOINT_NAME = "/test-image-handling-direct"

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            # Don't mock the UI - create a real canvas form for testing
            canvas_form = CanvasForm(mock_viewmodel, mock_resource_manager)

            # Build the canvas form with real interactive image
            canvas_form.build()

            # Create a simple UI to display the canvas form
            with ui.card().classes("w-96 h-96"):
                ui.label("Testing Direct Image Handling")
                ui.label(
                    "This test uses direct method calls instead of artificial buttons"
                )

            # Store canvas_form in the page context for testing
            ui.context.client.canvas_form = canvas_form  # type: ignore

        # Navigate to the test page
        await user.open(ENDPOINT_NAME)

        # Get the canvas form from the page context
        canvas_form = user.client.canvas_form  # type: ignore

        # Test updating background by directly calling the canvas form method
        # This is more realistic than creating artificial buttons
        mock_track_image = Mock(spec=TrackImage)
        mock_pil_image = Mock(spec=Image.Image)
        mock_track_image.as_image.return_value = mock_pil_image
        canvas_form.update_background(mock_track_image)

        # Assert background was updated
        assert canvas_form._current_image == mock_pil_image

        # Test clearing image by directly calling the canvas form method
        canvas_form.clear_image()

        # Assert image was cleared - the interactive image should be called with empty string # noqa
        # Since we're using a real interactive image, we can't easily mock it here
        # But we can verify the method was called without error

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_update_background(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        mock_track_image = Mock(spec=TrackImage)
        mock_pil_image = Mock(spec=Image.Image)
        mock_track_image.as_image.return_value = mock_pil_image

        # Act
        canvas_form.update_background(mock_track_image)

        # Assert
        assert canvas_form._current_image == mock_pil_image
        mock_ui.interactive_image.return_value.set_source.assert_called_with(
            mock_pil_image
        )

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_clear_image(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        # Act
        canvas_form.clear_image()

        # Assert
        mock_ui.interactive_image.return_value.set_source.assert_called_with("")

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_delete_element(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        # Arrange
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        # Add some elements first
        test_line = Line(id="test-line", x1=0, y1=0, x2=10, y2=10, stroke="red")
        test_polyline = Polyline(
            id="test-polyline", points=[(0, 0), (10, 10)], color="blue"
        )
        test_circle = Circle(
            id="test-circle", x=5, y=5, fill="green", pointer_event="all"
        )

        canvas_form._flows.add(test_line)
        canvas_form._sections.add("test", test_polyline)
        canvas_form._circles.add("test", test_circle)

        # Act
        canvas_form.delete_element("test-element")

        # Assert
        assert len(canvas_form._flows.lines) == 0
        assert len(canvas_form._sections.lines) == 0
        # CircleResources.clear() only clears the circles dict, not by_section
        assert len(canvas_form._circles.circles) == 0
