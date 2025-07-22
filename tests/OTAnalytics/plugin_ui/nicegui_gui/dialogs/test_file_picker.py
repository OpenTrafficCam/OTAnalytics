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
                suffix=".txt",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix=".py",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix=".pdf",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix="",
                is_file=lambda: False,
                is_dir=lambda: True,
            ),
        ]

        # Set up the name attribute for each mock as proper strings
        mock_files[0].name = "test.txt"
        mock_files[1].name = "script.py"
        mock_files[2].name = "document.pdf"
        mock_files[3].name = "folder"

        mock_glob.return_value = mock_files

        picker = LocalFilePicker(
            directory=test_dir,
            show_files_only_of_types=extensions,
            show_extension_select=False,
        )

        # Set up the mock grid with proper options dictionary
        picker.grid = Mock()
        picker.grid.options = {}
        picker.grid.update = Mock()

        # Replace picker.path with a mock that has a glob method
        mock_path = Mock()
        mock_path.glob.return_value = mock_files
        mock_path.parent = test_dir.parent
        picker.path = mock_path

        # Debug: Check what paths are returned by glob
        print(f"DEBUG: mock_glob.return_value = {mock_glob.return_value}")
        print(
            f"DEBUG: picker.show_files_only_of_types = "
            f"{picker.show_files_only_of_types}"
        )
        print(
            f"DEBUG: picker.current_selected_option = {picker.current_selected_option}"
        )
        print(
            f"DEBUG: picker.current_extension_filter = "
            f"{picker.current_extension_filter}"
        )
        print(f"DEBUG: picker.show_extension_select = {picker.show_extension_select}")

        # Debug: Check mock file properties
        for mock_file in mock_files:
            print(
                f"DEBUG: {mock_file.name} - suffix: {mock_file.suffix}, "
                f"is_file: {mock_file.is_file()}, is_dir: {mock_file.is_dir()}"
            )

        # Call update_grid to trigger filtering
        picker.update_grid()

        # Verify that only .txt, .py files and directories are included
        row_data = picker.grid.options.get("rowData", [])
        print(f"DEBUG: picker.grid.options = {picker.grid.options}")
        print(f"DEBUG: row_data = {row_data}")
        shown_names = [row["name"] for row in row_data]
        print(f"DEBUG: shown_names = {shown_names}")

        # Should include .txt and .py files, plus directories
        assert "test.txt" in shown_names
        assert "script.py" in shown_names
        assert "📁 <strong>folder</strong>" in shown_names
        # Should exclude .pdf files
        assert "document.pdf" not in shown_names

        # Verify we have exactly 4 items (2 files + 1 directory + 1 parent navigation)
        assert len(row_data) == 4

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
                suffix=".txt",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix=".py",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix="",
                is_file=lambda: False,
                is_dir=lambda: True,
            ),
        ]

        # Set up the name attribute for each mock as proper strings
        mock_files[0].name = "test.txt"
        mock_files[1].name = "script.py"
        mock_files[2].name = "folder"

        mock_glob.return_value = mock_files

        picker = LocalFilePicker(
            directory=test_dir,
            show_files_only_of_type=extension,
            show_extension_select=False,
        )

        # Set up the mock grid with proper options dictionary
        picker.grid = Mock()
        picker.grid.options = {}
        picker.grid.update = Mock()

        # Replace picker.path with a mock that has a glob method
        mock_path = Mock()
        mock_path.glob.return_value = mock_files
        mock_path.parent = test_dir.parent
        picker.path = mock_path

        # Call update_grid to trigger filtering
        picker.update_grid()

        # Verify that only .txt files and directories are included
        row_data = picker.grid.options.get("rowData", [])
        shown_names = [row["name"] for row in row_data]

        # Should include .txt files and directories
        assert "test.txt" in shown_names
        assert "📁 <strong>folder</strong>" in shown_names
        # Should exclude .py files
        assert "script.py" not in shown_names

        # Verify we have exactly 3 items (1 file + 1 directory + 1 parent navigation)
        assert len(row_data) == 3

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
                suffix=".txt",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix=".py",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix=".pdf",
                is_file=lambda: True,
                is_dir=lambda: False,
            ),
            Mock(
                spec=Path,
                suffix="",
                is_file=lambda: False,
                is_dir=lambda: True,
            ),
        ]

        # Set up the name attribute for each mock as proper strings
        mock_files[0].name = "test.txt"
        mock_files[1].name = "script.py"
        mock_files[2].name = "document.pdf"
        mock_files[3].name = "folder"

        mock_glob.return_value = mock_files

        # Create picker with parameter-based filter
        picker = LocalFilePicker(
            directory=test_dir,
            show_files_only_of_types=[".txt", ".md"],  # Parameter filter
            show_extension_select=True,
        )

        # Set up the mock grid with proper options dictionary
        picker.grid = Mock()
        picker.grid.options = {}
        picker.grid.update = Mock()

        # Replace picker.path with a mock that has a glob method
        mock_path = Mock()
        mock_path.glob.return_value = mock_files
        mock_path.parent = test_dir.parent
        picker.path = mock_path

        # Set dropdown filter (should take priority)
        picker.current_extension_filter = [".py", ".pyw"]
        picker.current_selected_option = (
            "Python Files"  # Change from "All Files" to enable filtering
        )

        # Call update_grid to trigger filtering
        picker.update_grid()

        # The dropdown filter should take priority over the parameter filter
        row_data = picker.grid.options.get("rowData", [])
        shown_names = [row["name"] for row in row_data]

        # Should include .py files (from dropdown filter) and directories
        assert "script.py" in shown_names
        assert "📁 <strong>folder</strong>" in shown_names
        # Should exclude .txt files (would be included by parameter filter
        # but dropdown takes priority)
        assert "test.txt" not in shown_names
        # Should exclude .pdf files (not in either filter)
        assert "document.pdf" not in shown_names

        # Verify we have exactly 3 items (1 .py file + 1 directory +
        # 1 parent navigation)
        assert len(row_data) == 3
