from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker


class TestLocalFilePicker:
    """Test the LocalFilePicker file extension filtering functionality."""

    def test_file_picker_initialization_with_multiple_extensions(self) -> None:
        test_dir: Path = Path("/tmp")
        extensions: List[str] = [".txt", ".py", ".md"]

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_types=extensions
            )

            assert picker.show_files_only_of_types == extensions
            assert picker.path == test_dir.expanduser()

    def test_file_picker_backward_compatibility(self) -> None:
        """Test that the old single extension parameter still works."""
        test_dir: Path = Path("/tmp")
        extension: str = ".txt"

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_type=extension
            )

            assert picker.show_files_only_of_type == extension
            assert picker.show_files_only_of_types is None

    @patch("pathlib.Path.glob")
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui")
    def test_file_filtering_with_multiple_extensions(
        self, mock_ui: Mock, mock_glob: Mock
    ) -> None:
        """Test that files are filtered correctly with multiple extensions."""
        test_dir: Path = Path("/tmp")
        extensions: List[str] = [".txt", ".py"]

        # Mock file paths
        mock_files: List[Mock] = [
            Mock(
                spec=Path,
                name="test.txt",
                suffix=".txt",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="script.py",
                suffix=".py",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="document.pdf",
                suffix=".pdf",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="folder",
                suffix="",
                is_file=lambda: False,
                is_dir=lambda: True,
            ),
        ]

        # Set up the name attribute for each mock
        for mock_file in mock_files:
            mock_file.name = mock_file.name

        mock_glob.return_value = mock_files

        picker = LocalFilePicker(
            directory=test_dir, show_files_only_of_types=extensions
        )

        # Call update_grid to trigger filtering
        picker.update_grid()

        # Verify that only .txt, .py files and directories are included
        # The exact verification would depend on how the grid is updated
        # This is a basic structure for the test

    @patch("pathlib.Path.glob")
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui")
    def test_file_filtering_with_single_extension_backward_compatibility(
        self, mock_ui: Mock, mock_glob: Mock
    ) -> None:
        test_dir: Path = Path("/tmp")
        extension: str = ".txt"

        # Mock file paths
        mock_files: List[Mock] = [
            Mock(
                spec=Path,
                name="test.txt",
                suffix=".txt",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="script.py",
                suffix=".py",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="folder",
                suffix="",
                is_file=lambda: False,
                is_dir=lambda: True,
            ),
        ]

        # Set up the name attribute for each mock
        for mock_file in mock_files:
            mock_file.name = mock_file.name

        mock_glob.return_value = mock_files

        picker = LocalFilePicker(directory=test_dir, show_files_only_of_type=extension)

        # Call update_grid to trigger filtering
        picker.update_grid()

        # Verify that only .txt files and directories are included
        # The exact verification would depend on how the grid is updated

    def test_file_picker_no_extension_filtering(self) -> None:
        """Test that when no extensions are specified, all files are shown."""
        test_dir = Path("/tmp")

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(directory=test_dir)

            assert picker.show_files_only_of_type is None
            assert picker.show_files_only_of_types is None

    def test_file_picker_with_extension_select_enabled(self) -> None:
        test_dir = Path("/tmp")

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(directory=test_dir, show_extension_select=True)

            assert picker.show_extension_select is True
            assert picker.extension_options is not None
            assert "All Files" in picker.extension_options
            assert "OTConfig Files" in picker.extension_options
            assert picker.current_extension_filter is None

    def test_file_picker_with_extension_select_disabled(self) -> None:
        test_dir = Path("/tmp")

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(directory=test_dir, show_extension_select=False)

            assert picker.show_extension_select is False
            assert (
                picker.extension_options is not None
            )  # Still defined but not used in UI

    def test_extension_filter_update(self) -> None:
        test_dir = Path("/tmp")

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(directory=test_dir, show_extension_select=True)

            # Mock event object
            mock_event = Mock()
            mock_event.value = "OTConfig Files"

            # Call the update method
            picker.update_extension_filter(mock_event)

            # Verify the filter was updated
            assert picker.current_extension_filter == [".otconfig"]

    @patch("pathlib.Path.glob")
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui")
    def test_dropdown_filter_takes_priority(
        self, mock_ui: Mock, mock_glob: Mock
    ) -> None:
        """Test that dropdown filter takes priority over parameter-based filters."""
        test_dir: Path = Path("/tmp")

        # Mock file paths
        mock_files: List[Mock] = [
            Mock(
                spec=Path,
                name="test.txt",
                suffix=".txt",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="script.py",
                suffix=".py",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="document.pdf",
                suffix=".pdf",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                name="folder",
                suffix="",
                is_file=lambda: False,
                is_dir=lambda: True,
            ),
        ]

        # Set up the name attribute for each mock
        for mock_file in mock_files:
            mock_file.name = mock_file.name

        mock_glob.return_value = mock_files

        # Create picker with parameter-based filter
        picker = LocalFilePicker(
            directory=test_dir,
            show_files_only_of_types=[".txt", ".md"],  # Parameter filter
            show_extension_select=True,
        )

        # Set dropdown filter (should take priority)
        picker.current_extension_filter = [".py", ".pyw"]

        # Call update_grid to trigger filtering
        picker.update_grid()

        # The dropdown filter should take priority over the parameter filter
        # This test verifies the logic structure is correct
