from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog import (
    FileChooserDialog,
)


class TestFileChooserDialog:
    """Test the FileChooserDialog file extension filtering functionality."""

    @pytest.fixture
    def mock_resource_manager(self) -> Mock:
        """Create a mock resource manager."""
        resource_manager = Mock(spec=ResourceManager)
        resource_manager.get.return_value = "Test Label"
        return resource_manager

    def test_file_chooser_dialog_initialization(
        self, mock_resource_manager: Mock
    ) -> None:
        """Test that FileChooserDialog can be initialized with file extensions."""
        file_extensions = {
            "Text Files": "txt",
            "Python Files": "py",
            "Markdown Files": "md",
        }

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=mock_resource_manager,
                title="Test Dialog",
                file_extensions=file_extensions,
                initial_file_stem="test_file",
                initial_dir=Path("/tmp"),
            )

            assert dialog._file_extensions == file_extensions
            assert dialog._title == "Test Dialog"
            assert dialog._initial_file_stem == "test_file"

    def test_get_extension_for_current_format(
        self, mock_resource_manager: Mock
    ) -> None:
        """Test that the correct extension is returned for the selected format."""
        file_extensions = {"Text Files": "txt", "Python Files": "py"}

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=mock_resource_manager,
                title="Test Dialog",
                file_extensions=file_extensions,
                initial_file_stem="test_file",
                initial_dir=Path("/tmp"),
            )

            # Mock the format field to return a specific format
            dialog._format_field = Mock()
            dialog._format_field.value = "Text Files"

            extension = dialog._get_extension_for_current_format()
            assert extension == "txt"

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.LocalFilePicker"
    )
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui")
    @pytest.mark.asyncio
    async def test_browse_directory_with_file_extension_filtering(
        self, mock_local_file_picker: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test that browse directory passes the correct file extensions to LocalFilePicker."""  # noqa
        file_extensions = {"Text Files": "txt", "Python Files": "py"}

        dialog = FileChooserDialog(
            resource_manager=mock_resource_manager,
            title="Test Dialog",
            file_extensions=file_extensions,
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        # Mock the format field to return a specific format
        dialog._format_field = Mock()
        dialog._format_field.value = "Text Files"

        # Mock the directory field
        dialog._directory_field = Mock()
        dialog._directory_field.value = "/tmp"

        # Mock the LocalFilePicker instance to return the expected result when awaited
        mock_picker_instance = AsyncMock()
        # Set up the mock to be awaitable and return the expected result
        mock_picker_instance.__await__ = Mock(
            return_value=iter([[Path("/tmp/test.txt")]])
        )
        mock_local_file_picker.return_value = mock_picker_instance

        # Mock the filename field
        dialog._filename_field = Mock()

        # Call the browse directory method
        await dialog._browse_directory()

        # Verify that LocalFilePicker was called with the correct file extensions
        mock_local_file_picker.assert_called_once()
        call_args = mock_local_file_picker.call_args

        # Check that show_files_only_of_types was passed with the correct extension
        assert "show_files_only_of_types" in call_args.kwargs
        assert call_args.kwargs["show_files_only_of_types"] == [".txt"]

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.LocalFilePicker"
    )
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui")
    @pytest.mark.asyncio
    async def test_browse_directory_with_extension_already_has_dot(
        self, mock_local_file_picker: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test that extensions already starting with dot are handled correctly."""
        file_extensions = {
            "Text Files": ".txt",  # Extension already has dot
            "Python Files": "py",  # Extension without dot
        }

        dialog = FileChooserDialog(
            resource_manager=mock_resource_manager,
            title="Test Dialog",
            file_extensions=file_extensions,
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        # Mock the format field to return a format with extension that already has dot
        dialog._format_field = Mock()
        dialog._format_field.value = "Text Files"

        # Mock the directory field
        dialog._directory_field = Mock()
        dialog._directory_field.value = "/tmp"

        # Mock the LocalFilePicker instance to return the expected result when awaited
        mock_picker_instance = AsyncMock()
        # Set up the mock to be awaitable and return the expected result
        mock_picker_instance.__await__ = Mock(return_value=iter([[]]))
        mock_local_file_picker.return_value = mock_picker_instance

        # Call the browse directory method
        await dialog._browse_directory()

        # Verify that LocalFilePicker was called with the correct file extensions
        mock_local_file_picker.assert_called_once()
        call_args = mock_local_file_picker.call_args

        assert "show_files_only_of_types" in call_args.kwargs
        assert call_args.kwargs["show_files_only_of_types"] == [".txt"]

    @patch(
        "OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.LocalFilePicker"
    )
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui")
    @pytest.mark.asyncio
    async def test_browse_directory_no_file_extensions(
        self, mock_local_file_picker: Mock, mock_resource_manager: Mock
    ) -> None:
        """Test that when no file extensions are provided, all files are shown."""
        dialog = FileChooserDialog(
            resource_manager=mock_resource_manager,
            title="Test Dialog",
            file_extensions={},  # No file extensions
            initial_file_stem="test_file",
            initial_dir=Path("/tmp"),
        )

        # Mock the directory field
        dialog._directory_field = Mock()
        dialog._directory_field.value = "/tmp"

        # Mock the LocalFilePicker instance to return the expected result when awaited
        mock_picker_instance = AsyncMock()
        # Set up the mock to be awaitable and return the expected result
        mock_picker_instance.__await__ = Mock(return_value=iter([[]]))
        mock_local_file_picker.return_value = mock_picker_instance

        # Call the browse directory method
        await dialog._browse_directory()

        # Verify that LocalFilePicker was called with no file extension filtering
        mock_local_file_picker.assert_called_once()
        call_args = mock_local_file_picker.call_args

        # Check that show_files_only_of_types is None (show all files)
        assert "show_files_only_of_types" in call_args.kwargs
        assert call_args.kwargs["show_files_only_of_types"] is None

    def test_get_file_path(self, mock_resource_manager: Mock) -> None:
        """Test that get_file_path returns the correct path."""
        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=mock_resource_manager,
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

    def test_get_format(self, mock_resource_manager: Mock) -> None:
        """Test that get_format returns the selected format."""
        file_extensions = {"Text Files": "txt", "Python Files": "py"}

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog.ui"):
            dialog = FileChooserDialog(
                resource_manager=mock_resource_manager,
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
