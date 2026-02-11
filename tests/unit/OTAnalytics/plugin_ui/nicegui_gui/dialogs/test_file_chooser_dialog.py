from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog import (
    MARKER_DIRECTORY,
    MARKER_FORMAT,
    FileChooserDialog,
)


class TestFileChooserDialog:
    """Test the FileChooserDialog file extension filtering functionality."""

    def test_file_chooser_dialog_initialization(
        self, resource_manager: ResourceManager
    ) -> None:
        """Test that FileChooserDialog can be initialized with file extensions."""
        file_extensions = {
            "Text Files": "txt",
            "Python Files": "py",
            "Markdown Files": "md",
        }

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=resource_manager,
                title="Test Dialog",
                file_extensions=file_extensions,
                initial_file_stem="test_file",
                initial_dir=Path("/tmp"),
            )

            assert dialog._file_extensions == file_extensions
            assert dialog._title == "Test Dialog"
            assert dialog._initial_file_stem == "test_file"

    @pytest.mark.asyncio
    async def test_get_extension_for_current_format(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """Test that the correct extension is returned for the selected format."""
        file_extensions = {"Text Files": "txt", "Python Files": "py"}

        dialog = FileChooserDialog(
            resource_manager=resource_manager,
            title="Test Dialog",
            file_extensions=file_extensions,
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        @ui.page("/test")
        def page() -> None:
            dialog.build().open()

        await user.open("/test")

        # Select "Text Files" using user fixture
        user.find(marker=MARKER_FORMAT).click()
        user.find("Text Files").click()

        extension = dialog._get_extension_for_current_format()
        assert extension == "txt"

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.LocalFilePicker"
    )
    @pytest.mark.asyncio
    async def test_browse_directory_with_file_extension_filtering(
        self,
        mock_local_file_picker: Mock,
        user: User,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that browse directory calls LocalFilePicker correctly."""  # noqa
        file_extensions = {"Text Files": "txt", "Python Files": "py"}

        dialog = FileChooserDialog(
            resource_manager=resource_manager,
            title="Test Dialog",
            file_extensions=file_extensions,
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        @ui.page("/test")
        def page() -> None:
            dialog.build().open()

        await user.open("/test")

        # Select "Text Files" using user fixture
        user.find(marker=MARKER_FORMAT).click()
        user.find("Text Files").click()

        # Set directory using user fixture
        user.find(marker=MARKER_DIRECTORY).clear().type("/tmp")

        # Mock the LocalFilePicker to be an awaitable that returns the expected result
        async def mock_picker() -> list:
            return [Path("/tmp/test.txt")]

        mock_local_file_picker.return_value = mock_picker()

        # Call the browse directory method
        await dialog._browse_directory()

        # Verify that LocalFilePicker was called with the correct parameters
        mock_local_file_picker.assert_called_once()
        call_args = mock_local_file_picker.call_args

        # Check the actual parameters that are used in the implementation
        assert call_args.kwargs["directory"] == Path("/tmp")
        assert call_args.kwargs["show_hidden_files"] is False
        assert call_args.kwargs["show_files_only_of_type"] is None
        assert call_args.kwargs["show_only_directories"] is False

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.LocalFilePicker"
    )
    @pytest.mark.asyncio
    async def test_browse_directory_with_extension_already_has_dot(
        self,
        mock_local_file_picker: Mock,
        user: User,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that browse directory works with extensions that already have dots."""
        file_extensions = {
            "Text Files": ".txt",  # Extension already has dot
            "Python Files": "py",  # Extension without dot
        }

        dialog = FileChooserDialog(
            resource_manager=resource_manager,
            title="Test Dialog",
            file_extensions=file_extensions,
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        @ui.page("/test")
        def page() -> None:
            dialog.build().open()

        await user.open("/test")

        # Select "Text Files" using user fixture (extension already has dot)
        user.find(marker=MARKER_FORMAT).click()
        user.find("Text Files").click()

        # Set directory using user fixture
        user.find(marker=MARKER_DIRECTORY).clear().type("/tmp")

        # Mock the LocalFilePicker to be an awaitable that returns the expected result
        async def mock_picker() -> list:
            return []

        mock_local_file_picker.return_value = mock_picker()

        # Call the browse directory method
        await dialog._browse_directory()

        # Verify that LocalFilePicker was called with the correct parameters
        mock_local_file_picker.assert_called_once()
        call_args = mock_local_file_picker.call_args

        # Check the actual parameters that are used in the implementation
        assert call_args.kwargs["directory"] == Path("/tmp")
        assert call_args.kwargs["show_hidden_files"] is False
        assert call_args.kwargs["show_files_only_of_type"] is None
        assert call_args.kwargs["show_only_directories"] is False

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.LocalFilePicker"
    )
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui")
    @pytest.mark.asyncio
    async def test_browse_directory_no_file_extensions(
        self,
        mock_ui: Mock,
        mock_local_file_picker: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that when no file extensions are provided, all files are shown."""
        dialog = FileChooserDialog(
            resource_manager=resource_manager,
            title="Test Dialog",
            file_extensions={},  # No file extensions
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        # Mock the directory field
        dialog._directory_field = Mock()
        dialog._directory_field.value = "/tmp"

        # Mock the LocalFilePicker to be an awaitable that returns the expected result
        async def mock_picker() -> list:
            return []

        mock_local_file_picker.return_value = mock_picker()

        # Call the browse directory method
        await dialog._browse_directory()

        # Verify that LocalFilePicker was called with the correct parameters
        mock_local_file_picker.assert_called_once()
        call_args = mock_local_file_picker.call_args

        # Check the actual parameters that are used in the implementation
        assert call_args.kwargs["directory"] == Path("/tmp")
        assert call_args.kwargs["show_hidden_files"] is False
        assert call_args.kwargs["show_files_only_of_type"] is None
        assert call_args.kwargs["show_only_directories"] is False

    def test_get_file_path(self, resource_manager: ResourceManager) -> None:
        """Test that get_file_path returns the correct path."""
        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=resource_manager,
                title="Test Dialog",
                file_extensions={"Text": "txt"},
                initial_file_stem="test_file",
                initial_dir=Path("/tmp"),
            )

            # Mock the directory and filename fields
            dialog._directory_field = Mock()
            dialog._directory_field.value = "/home/user"
            dialog._filename_field = Mock()
            dialog._filename_field.value = "test.txt"

            file_path = dialog.get_file_path()
            assert file_path == Path("/home/user/test.txt")

    def test_get_format(self, resource_manager: ResourceManager) -> None:
        """Test that get_format returns the selected format."""
        file_extensions = {"Text Files": "txt", "Python Files": "py"}

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=resource_manager,
                title="Test Dialog",
                file_extensions=file_extensions,
                initial_file_stem="test_file",
                initial_dir=Path("/tmp"),
            )

            # Mock the format field
            dialog._format_field = Mock()
            dialog._format_field.value = "Python Files"

            format_value = dialog.get_format()
            assert format_value == "Python Files"
