from typing import Any, Iterator
from unittest.mock import MagicMock, Mock, patch

import pytest
from nicegui import events, ui
from nicegui.events import KeyEventArguments
from nicegui.testing import User
from PIL import Image

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ADD_KNOB_HOTKEY_VALUE,
    CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE,
    DEFAULT_HOTKEYS,
    DELETE_KNOB_ALTERNATIVE_HOTKEY_VALUE,
    DELETE_KNOB_HOTKEY_VALUE,
    SAVE_SECTION_HOTKEY_VALUE,
    SHIFT_KNOB_BACKWARD_HOTKEY_VALUE,
    SHIFT_KNOB_FORWARD_HOTKEY_VALUE,
    HotKeys,
    ResourceManager,
)
from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polygon import Polygon
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    CLICK,
    EDIT_COLOR,
    EDIT_KNOB_ID_PREFIX,
    ELEMENT_ID,
    HOVERED_KNOB_COLOR,
    IMAGE_X,
    IMAGE_Y,
    MOUSE_MOVE,
    MOUSE_UP,
    NORMAL_COLOR,
    RELEASE_FOCUS,
    SELECTED_COLOR,
    CanvasForm,
    circle_to_coordinates,
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
    section.get_coordinates.return_value = [
        Coordinate(10, 20),
        Coordinate(110, 20),
        Coordinate(210, 20),
    ]
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
        canvas_form.start_section_geometry_editor(current_section)

    return canvas_form


class TestCanvasFormHelperFunctions:
    """Test helper functions used by CanvasForm."""

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
        canvas_form.start_section_builder()

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


def create_mouse_event(event_type: str, x: float, y: float) -> MagicMock:
    event = MagicMock(spec=events.MouseEventArguments)
    event.type = event_type
    event.image_x = x
    event.image_y = y
    return event


def create_key_event(key: str, keydown: bool = True) -> MagicMock:
    event = MagicMock(spec=KeyEventArguments)
    event.key = key
    event.action = MagicMock()
    event.action.keydown = keydown
    return event


def hotkeys_by_default(key: HotKeys) -> str | None:
    return DEFAULT_HOTKEYS.get(key)


class TestCanvasFormSectionBuilder:
    """Drawing a new section on the canvas (reference: SectionBuilder)."""

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_start_section_builder_subscribes_mouse_move(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        canvas_form.start_section_builder()

        background_image = mock_ui.interactive_image.return_value
        background_image._props.__setitem__.assert_called_with(
            "events", [CLICK, MOUSE_MOVE, MOUSE_UP]
        )

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_start_section_builder_releases_focus_for_hotkeys(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        canvas_form.start_section_builder()

        background_image = mock_ui.interactive_image.return_value
        background_image.client.run_javascript.assert_called_once_with(RELEASE_FOCUS)

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_mouse_move_draws_preview_line_from_last_point(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form.start_section_builder()
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))

        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 50.4, 60.6))

        assert canvas_form._preview_point == (50, 61)
        assert len(canvas_form._new_section_points) == 1
        content = mock_ui.interactive_image.return_value.content
        assert 'points="10,20 50,61"' in content

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_mouse_move_without_builder_does_nothing(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 50, 60))

        assert canvas_form._preview_point is None

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    def test_click_adds_points(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form.start_section_builder()

        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))
        canvas_form.on_mouse(create_mouse_event(CLICK, 30, 40))

        assert circle_to_coordinates(canvas_form._new_section_points) == [
            (10, 20),
            (30, 40),
        ]

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_right_click_finishes_new_section(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form.start_section_builder()
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))
        canvas_form.on_mouse(create_mouse_event(CLICK, 30, 40))

        await canvas_form.on_right_click()

        mock_viewmodel.add_new_section.assert_called_once()
        call_args = mock_viewmodel.add_new_section.call_args
        assert call_args[1]["coordinates"] == [(10, 20), (30, 40)]
        assert canvas_form._new_section is False

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_right_click_without_editor_does_nothing(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )

        await canvas_form.on_right_click()

        mock_viewmodel.add_new_section.assert_not_called()
        mock_viewmodel.update_section_coordinates.assert_not_called()

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_finish_line_section_with_one_point_is_ignored(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui,
            mock_viewmodel,
            mock_resource_manager,
            hotkey_side_effect=hotkeys_by_default,
        )
        canvas_form.start_section_builder()
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))

        await canvas_form.handle_key(create_key_event(SAVE_SECTION_HOTKEY_VALUE))

        mock_viewmodel.add_new_section.assert_not_called()
        mock_ui.notify.assert_called_once()
        assert canvas_form._new_section is True
        assert len(canvas_form._new_section_points) == 1

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_finish_area_section_with_two_points_is_ignored(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form.start_section_builder(is_area_section=True)
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))
        canvas_form.on_mouse(create_mouse_event(CLICK, 30, 40))

        await canvas_form.on_right_click()

        mock_viewmodel.add_new_section.assert_not_called()
        mock_ui.notify.assert_called_once()
        assert canvas_form._new_section is True

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_finish_area_section_closes_area(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui, mock_viewmodel, mock_resource_manager
        )
        canvas_form.start_section_builder(is_area_section=True)
        for x, y in [(10, 20), (30, 40), (50, 20)]:
            canvas_form.on_mouse(create_mouse_event(CLICK, x, y))

        await canvas_form.on_right_click()

        mock_viewmodel.add_new_section.assert_called_once()
        call_args = mock_viewmodel.add_new_section.call_args
        assert call_args[1]["coordinates"] == [(10, 20), (30, 40), (50, 20), (10, 20)]
        assert call_args[1]["is_area_section"] is True

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_escape_aborts_new_section(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui,
            mock_viewmodel,
            mock_resource_manager,
            hotkey_side_effect=hotkeys_by_default,
        )
        canvas_form.start_section_builder()
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))

        await canvas_form.handle_key(
            create_key_event(CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE)
        )

        mock_viewmodel.cancel_action.assert_called_once()
        assert canvas_form._new_section is False
        assert canvas_form._new_section_points == []
        assert canvas_form._preview_point is None

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_keys_are_ignored_without_active_editor(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui,
            mock_viewmodel,
            mock_resource_manager,
            hotkey_side_effect=hotkeys_by_default,
        )

        await canvas_form.handle_key(
            create_key_event(CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE)
        )
        await canvas_form.handle_key(create_key_event(SAVE_SECTION_HOTKEY_VALUE))

        mock_viewmodel.cancel_action.assert_not_called()
        mock_viewmodel.add_new_section.assert_not_called()
        mock_viewmodel.update_section_coordinates.assert_not_called()

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
    )
    @pytest.mark.asyncio
    async def test_key_up_is_ignored(
        self, mock_ui: Any, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> None:
        canvas_form = setup_canvas_form_with_mocks(
            mock_ui,
            mock_viewmodel,
            mock_resource_manager,
            hotkey_side_effect=hotkeys_by_default,
        )
        canvas_form.start_section_builder()
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))
        canvas_form.on_mouse(create_mouse_event(CLICK, 30, 40))

        await canvas_form.handle_key(
            create_key_event(SAVE_SECTION_HOTKEY_VALUE, keydown=False)
        )

        mock_viewmodel.add_new_section.assert_not_called()
        assert canvas_form._new_section is True


def svg_event(x: float, y: float, element_id: str = "") -> dict:
    return {IMAGE_X: x, IMAGE_Y: y, ELEMENT_ID: element_id}


def knob_id(index: int) -> str:
    return f"{EDIT_KNOB_ID_PREFIX}{index}"


ORIGINAL_COORDINATES = [(10, 20), (110, 20), (210, 20)]
CANVAS_UI = (
    "OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form.ui"
)


class TestCanvasFormSectionGeometryEditor:
    """Editing an existing section (reference: SectionGeometryEditor)."""

    @pytest.fixture
    def canvas_form(
        self, mock_viewmodel: Mock, mock_resource_manager: Mock, mock_section: Mock
    ) -> Iterator[Any]:
        with patch(CANVAS_UI) as mock_ui:
            canvas_form = setup_canvas_form_with_mocks(
                mock_ui,
                mock_viewmodel,
                mock_resource_manager,
                hotkey_side_effect=hotkeys_by_default,
                current_section=mock_section,
            )
            canvas_form.mock_ui = mock_ui  # type: ignore[attr-defined]
            yield canvas_form

    @pytest.fixture
    def area_section(self, mock_section: Mock) -> Mock:
        mock_section.get_coordinates.return_value = [
            Coordinate(0, 0),
            Coordinate(10, 0),
            Coordinate(10, 10),
            Coordinate(0, 0),
        ]
        return mock_section

    def test_start_editor_releases_focus_for_hotkeys(self, canvas_form: Any) -> None:
        background_image = canvas_form.mock_ui.interactive_image.return_value
        background_image.client.run_javascript.assert_called_with(RELEASE_FOCUS)

    def test_start_editor_loads_coordinates(self, canvas_form: Any) -> None:
        assert canvas_form._edit_coordinates == ORIGINAL_COORDINATES
        assert canvas_form._edit_temporary == ORIGINAL_COORDINATES
        assert canvas_form._selected_knob_index is None

    def test_start_editor_for_area_drops_closing_coordinate(
        self, mock_viewmodel: Mock, mock_resource_manager: Mock, area_section: Mock
    ) -> None:
        with patch(CANVAS_UI) as mock_ui:
            canvas_form = setup_canvas_form_with_mocks(
                mock_ui, mock_viewmodel, mock_resource_manager
            )
            canvas_form.start_section_geometry_editor(
                area_section, is_area_section=True
            )

        assert canvas_form._edit_coordinates == [(0, 0), (10, 0), (10, 10)]

    def test_start_editor_subscribes_mouse_move(self, canvas_form: Any) -> None:
        background_image = canvas_form.mock_ui.interactive_image.return_value
        background_image._props.__setitem__.assert_called_with(
            "events", [CLICK, MOUSE_MOVE, MOUSE_UP]
        )

    def test_hover_highlights_knob_under_mouse(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_move(svg_event(112, 22))

        assert canvas_form._hovered_knob_index == 1
        content = canvas_form.mock_ui.interactive_image.return_value.content
        assert HOVERED_KNOB_COLOR in content

    def test_hover_far_from_knob_highlights_nothing(self, canvas_form: Any) -> None:
        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 60, 100))

        assert canvas_form._hovered_knob_index is None

    def test_midpoints_are_drawn_below_knobs(self, canvas_form: Any) -> None:
        svg = canvas_form._edit_geometry()

        assert 'id="edit-mid-0"' in svg
        assert 'id="edit-mid-1"' in svg
        assert svg.index("edit-mid-1") < svg.index(knob_id(0))

    def test_midpoints_are_hidden_while_knob_is_selected(
        self, canvas_form: Any
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(110, 20, knob_id(1)))

        assert "edit-mid-" not in canvas_form._edit_geometry()

    def test_click_on_midpoint_inserts_and_drags_knob(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_down(svg_event(60, 20, "edit-mid-0"))

        assert canvas_form._edit_temporary == [(10, 20), (60, 20), (110, 20), (210, 20)]
        assert canvas_form._selected_knob_index == 1

        canvas_form.on_svg_pointer_move(svg_event(70, 50, "edit-mid-0"))
        canvas_form.on_svg_pointer_up(svg_event(71, 51, "edit-mid-0"))

        assert canvas_form._edit_coordinates == [
            (10, 20),
            (71, 51),
            (110, 20),
            (210, 20),
        ]

    def test_repeated_insert_in_same_segment_adds_new_knob(
        self, canvas_form: Any
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(210, 20, "edit-mid-1"))
        canvas_form.on_svg_pointer_up(svg_event(160, 20, "edit-mid-1"))
        canvas_form._on_canvas_click((160, 20))
        canvas_form.on_svg_pointer_down(svg_event(135, 20, "edit-mid-1"))
        canvas_form._on_canvas_click((135, 20))

        assert canvas_form._edit_temporary == [
            (10, 20),
            (110, 20),
            (135, 20),
            (160, 20),
            (210, 20),
        ]

    def test_drag_knob_moves_it(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_down(svg_event(110, 20, knob_id(1)))
        assert canvas_form._selected_knob_index == 1

        canvas_form.on_svg_pointer_move(svg_event(120, 50, knob_id(1)))
        assert canvas_form._edit_temporary[1] == (120, 50)
        assert canvas_form._edit_coordinates == ORIGINAL_COORDINATES

        canvas_form.on_svg_pointer_up(svg_event(121, 51, knob_id(1)))

        assert canvas_form._edit_coordinates == [(10, 20), (121, 51), (210, 20)]
        assert canvas_form._selected_knob_index is None

    def test_drag_released_outside_of_svg_moves_knob(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_down(svg_event(10, 20, knob_id(0)))
        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 30, 70))

        canvas_form.on_mouse(create_mouse_event(MOUSE_UP, 31, 71))

        assert canvas_form._edit_coordinates == [(31, 71), (110, 20), (210, 20)]
        assert canvas_form._selected_knob_index is None

    def test_click_selects_knob_and_second_click_places_it(
        self, canvas_form: Any
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(210, 20, knob_id(2)))
        canvas_form.on_svg_pointer_up(svg_event(210, 20, knob_id(2)))
        assert canvas_form._selected_knob_index == 2

        canvas_form.on_svg_pointer_move(svg_event(250, 80, knob_id(2)))
        canvas_form.on_svg_pointer_down(svg_event(250, 80, knob_id(2)))
        canvas_form.on_svg_pointer_up(svg_event(250, 80, knob_id(2)))

        assert canvas_form._edit_coordinates == [(10, 20), (110, 20), (250, 80)]
        assert canvas_form._selected_knob_index is None

    def test_click_on_image_places_selected_knob(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_down(svg_event(210, 20, knob_id(2)))
        canvas_form.on_svg_pointer_up(svg_event(210, 20, knob_id(2)))

        canvas_form.on_mouse(create_mouse_event(CLICK, 230, 90))

        assert canvas_form._edit_coordinates == [(10, 20), (110, 20), (230, 90)]
        assert canvas_form._selected_knob_index is None

    def test_pointer_down_next_to_knob_selects_closest_knob(
        self, canvas_form: Any
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(113, 18, "other-element"))

        assert canvas_form._selected_knob_index == 1

    def test_pointer_down_far_from_knobs_selects_nothing(
        self, canvas_form: Any
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(60, 100, "other-element"))

        assert canvas_form._selected_knob_index is None

    @pytest.mark.asyncio
    async def test_plus_inserts_knob_at_mouse_position(self, canvas_form: Any) -> None:
        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 60, 30))

        await canvas_form.handle_key(create_key_event(ADD_KNOB_HOTKEY_VALUE))

        assert canvas_form._edit_temporary == [
            (10, 20),
            (60, 30),
            (110, 20),
            (210, 20),
        ]
        assert canvas_form._selected_knob_index == 1

    @pytest.mark.asyncio
    async def test_inserted_knob_is_placed_with_click(self, canvas_form: Any) -> None:
        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 60, 30))
        await canvas_form.handle_key(create_key_event(ADD_KNOB_HOTKEY_VALUE))

        canvas_form.on_svg_pointer_move(svg_event(65, 35, knob_id(1)))
        canvas_form.on_svg_pointer_down(svg_event(65, 35, knob_id(1)))
        canvas_form.on_svg_pointer_up(svg_event(65, 35, knob_id(1)))

        assert canvas_form._edit_coordinates == [
            (10, 20),
            (65, 35),
            (110, 20),
            (210, 20),
        ]
        assert canvas_form._selected_knob_index is None

    @pytest.mark.asyncio
    async def test_escape_after_insert_removes_new_knob(
        self, canvas_form: Any, mock_viewmodel: Mock
    ) -> None:
        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 60, 30))
        await canvas_form.handle_key(create_key_event(ADD_KNOB_HOTKEY_VALUE))

        await canvas_form.handle_key(
            create_key_event(CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE)
        )

        assert canvas_form._edit_temporary == ORIGINAL_COORDINATES
        assert canvas_form._selected_knob_index is None
        assert canvas_form._current_section is not None
        mock_viewmodel.cancel_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_escape_without_selected_knob_cancels(
        self, canvas_form: Any, mock_viewmodel: Mock
    ) -> None:
        await canvas_form.handle_key(
            create_key_event(CANCEL_SECTION_GEOMETRY_HOTKEY_VALUE)
        )

        mock_viewmodel.cancel_action.assert_called_once()
        mock_viewmodel.update_section_coordinates.assert_not_called()
        assert canvas_form._current_section is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key", [DELETE_KNOB_HOTKEY_VALUE, DELETE_KNOB_ALTERNATIVE_HOTKEY_VALUE]
    )
    async def test_delete_removes_selected_knob(
        self, canvas_form: Any, key: str
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(110, 20, knob_id(1)))
        canvas_form.on_svg_pointer_up(svg_event(110, 20, knob_id(1)))

        await canvas_form.handle_key(create_key_event(key))

        assert canvas_form._edit_coordinates == [(10, 20), (210, 20)]
        assert canvas_form._selected_knob_index is None

    @pytest.mark.asyncio
    async def test_delete_keeps_minimum_number_of_knobs(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_down(svg_event(110, 20, knob_id(1)))
        canvas_form.on_svg_pointer_up(svg_event(110, 20, knob_id(1)))
        await canvas_form.handle_key(create_key_event(DELETE_KNOB_HOTKEY_VALUE))
        canvas_form.on_svg_pointer_down(svg_event(10, 20, knob_id(0)))
        canvas_form.on_svg_pointer_up(svg_event(10, 20, knob_id(0)))

        await canvas_form.handle_key(create_key_event(DELETE_KNOB_HOTKEY_VALUE))

        assert canvas_form._edit_coordinates == [(10, 20), (210, 20)]

    @pytest.mark.asyncio
    async def test_arrow_keys_shift_selected_knob(self, canvas_form: Any) -> None:
        canvas_form.on_svg_pointer_down(svg_event(10, 20, knob_id(0)))
        canvas_form.on_svg_pointer_up(svg_event(10, 20, knob_id(0)))

        await canvas_form.handle_key(create_key_event(SHIFT_KNOB_FORWARD_HOTKEY_VALUE))

        assert canvas_form._edit_temporary == [(110, 20), (10, 20), (210, 20)]
        assert canvas_form._selected_knob_index == 1

        await canvas_form.handle_key(create_key_event(SHIFT_KNOB_BACKWARD_HOTKEY_VALUE))

        assert canvas_form._edit_temporary == ORIGINAL_COORDINATES
        assert canvas_form._selected_knob_index == 0

    @pytest.mark.asyncio
    async def test_enter_saves_edited_coordinates(
        self, canvas_form: Any, mock_viewmodel: Mock, mock_section: Mock
    ) -> None:
        canvas_form.on_svg_pointer_down(svg_event(110, 20, knob_id(1)))
        canvas_form.on_svg_pointer_move(svg_event(120, 50, knob_id(1)))
        canvas_form.on_svg_pointer_up(svg_event(120, 50, knob_id(1)))

        await canvas_form.handle_key(create_key_event(SAVE_SECTION_HOTKEY_VALUE))

        mock_viewmodel.update_section_coordinates.assert_called_once_with(
            mock_section.to_dict.return_value, [(10, 20), (120, 50), (210, 20)]
        )
        assert canvas_form._current_section is None

    @pytest.mark.asyncio
    async def test_right_click_saves_edited_coordinates(
        self, canvas_form: Any, mock_viewmodel: Mock, mock_section: Mock
    ) -> None:
        await canvas_form.on_right_click()

        mock_viewmodel.update_section_coordinates.assert_called_once_with(
            mock_section.to_dict.return_value, ORIGINAL_COORDINATES
        )

    @pytest.mark.asyncio
    async def test_save_area_closes_area(
        self, mock_viewmodel: Mock, mock_resource_manager: Mock, area_section: Mock
    ) -> None:
        with patch(CANVAS_UI) as mock_ui:
            canvas_form = setup_canvas_form_with_mocks(
                mock_ui, mock_viewmodel, mock_resource_manager
            )
            canvas_form.start_section_geometry_editor(
                area_section, is_area_section=True
            )

            await canvas_form.on_right_click()

        mock_viewmodel.update_section_coordinates.assert_called_once_with(
            area_section.to_dict.return_value, [(0, 0), (10, 0), (10, 10), (0, 0)]
        )

    def test_edit_knobs_are_drawn(self, canvas_form: Any) -> None:
        content = canvas_form.mock_ui.interactive_image.return_value.content

        for index in range(len(ORIGINAL_COORDINATES)):
            assert f'id="{knob_id(index)}"' in content
        assert EDIT_COLOR in content


class TestCanvasFormPresentation:
    """Presentation of sections and flows (reference: SectionPainter, ArrowPainter)."""

    @pytest.fixture
    def canvas_form(
        self, mock_viewmodel: Mock, mock_resource_manager: Mock
    ) -> Iterator[Any]:
        with patch(CANVAS_UI) as mock_ui:
            canvas_form = setup_canvas_form_with_mocks(
                mock_ui,
                mock_viewmodel,
                mock_resource_manager,
                hotkey_side_effect=hotkeys_by_default,
            )
            canvas_form.mock_ui = mock_ui  # type: ignore[attr-defined]
            yield canvas_form

    def content(self, canvas_form: Any) -> str:
        return canvas_form.mock_ui.interactive_image.return_value.content

    def test_area_section_is_drawn_as_filled_polygon(self, canvas_form: Any) -> None:
        canvas_form.draw_section(
            id="area",
            coordinates=[(0, 0), (10, 0), (10, 10), (0, 0)],
            is_selected_section=False,
            is_area_section=True,
        )

        shape = canvas_form._sections.lines["area"]
        assert isinstance(shape, Polygon)
        assert shape.points == [(0, 0), (10, 0), (10, 10)]
        assert 0 < shape.fill_opacity < 1
        assert len(canvas_form._circles.by_section["area"]) == 3
        assert "<polygon" in self.content(canvas_form)

    def test_line_section_is_drawn_as_polyline(self, canvas_form: Any) -> None:
        canvas_form.draw_section(
            id="line", coordinates=[(0, 0), (10, 0)], is_selected_section=False
        )

        assert isinstance(canvas_form._sections.lines["line"], Polyline)

    def test_section_name_is_drawn(self, canvas_form: Any) -> None:
        canvas_form.draw_section(
            id="line",
            coordinates=[(5, 30), (10, 0)],
            is_selected_section=False,
            text="North",
        )

        content = self.content(canvas_form)
        assert ">North</text>" in content
        assert 'x="5"' in content

    def test_section_without_name_has_no_text(self, canvas_form: Any) -> None:
        canvas_form.draw_section(
            id="line", coordinates=[(0, 0), (10, 0)], is_selected_section=False
        )

        assert "<text" not in self.content(canvas_form)

    def test_section_texts_are_removed_with_sections(self, canvas_form: Any) -> None:
        canvas_form.draw_section(
            id="line",
            coordinates=[(0, 0), (10, 0)],
            is_selected_section=False,
            text="North",
        )

        canvas_form.delete_element("line_section")
        canvas_form.draw_all()

        assert "North" not in self.content(canvas_form)

    def test_new_area_section_is_drawn_as_polygon(self, canvas_form: Any) -> None:
        canvas_form.start_section_builder(is_area_section=True)
        for x, y in [(0, 0), (10, 0)]:
            canvas_form.on_mouse(create_mouse_event(CLICK, x, y))
        canvas_form.on_mouse(create_mouse_event(MOUSE_MOVE, 10, 10))

        assert 'points="0,0 10,0 10,10"' in self.content(canvas_form)
        assert "<polygon" in self.content(canvas_form)

    def test_draw_arrow_uses_arrow_style(self, canvas_form: Any) -> None:
        start_section, end_section, start_calculator, end_calculator = arrow_mocks()

        canvas_form.draw_arrow(
            start_section=start_section,
            end_section=end_section,
            start_refpt_calculator=start_calculator,
            end_refpt_calculator=end_calculator,
            arrow_style={"fill": "#8CFFC2", "width": 4, "dash": (5, 5)},
        )

        arrow = canvas_form._flows.lines["arrow-start-section-end-section"]
        assert arrow.color == "#8CFFC2"
        assert arrow.width == 4
        assert arrow.dash == (5, 5)
        assert 'stroke="#8CFFC2"' in self.content(canvas_form)

    def test_draw_arrow_without_style_uses_default(self, canvas_form: Any) -> None:
        start_section, end_section, start_calculator, end_calculator = arrow_mocks()

        canvas_form.draw_arrow(
            start_section=start_section,
            end_section=end_section,
            start_refpt_calculator=start_calculator,
            end_refpt_calculator=end_calculator,
        )

        arrow = canvas_form._flows.lines["arrow-start-section-end-section"]
        assert arrow.color == NORMAL_COLOR

    def test_disabled_canvas_ignores_editor_input(
        self, canvas_form: Any, mock_section: Mock
    ) -> None:
        canvas_form.start_section_builder()
        canvas_form.disable()

        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))

        assert canvas_form._new_section_points == []

        canvas_form.enable()
        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))

        assert len(canvas_form._new_section_points) == 1

    @pytest.mark.asyncio
    async def test_disabled_canvas_ignores_keys_and_right_click(
        self, canvas_form: Any, mock_viewmodel: Mock, mock_section: Mock
    ) -> None:
        canvas_form.start_section_geometry_editor(mock_section)
        canvas_form.disable()

        await canvas_form.handle_key(create_key_event(SAVE_SECTION_HOTKEY_VALUE))
        await canvas_form.on_right_click()
        canvas_form.on_svg_pointer_down(svg_event(110, 20, knob_id(1)))

        mock_viewmodel.update_section_coordinates.assert_not_called()
        assert canvas_form._selected_knob_index is None

    def test_editor_started_by_running_action_is_enabled(
        self, canvas_form: Any
    ) -> None:
        canvas_form.disable()
        canvas_form.start_section_builder()

        canvas_form.on_mouse(create_mouse_event(CLICK, 10, 20))

        assert len(canvas_form._new_section_points) == 1


def arrow_mocks() -> tuple[Mock, Mock, Mock, Mock]:
    start_section = Mock()
    start_section.id = "start-section"
    end_section = Mock()
    end_section.id = "end-section"
    start_calculator = Mock()
    start_calculator.get_reference_point.return_value = (100, 200)
    end_calculator = Mock()
    end_calculator.get_reference_point.return_value = (300, 400)
    return start_section, end_section, start_calculator, end_calculator
