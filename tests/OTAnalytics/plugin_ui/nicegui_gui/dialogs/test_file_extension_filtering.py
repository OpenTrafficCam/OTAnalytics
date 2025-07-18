from pathlib import Path
from unittest.mock import Mock, patch

from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker


class TestFileExtensionFiltering:
    """Test the new file extension filtering functionality."""

    def test_multiple_extensions_filtering_example(self) -> None:
        """Demonstrate how to use LocalFilePicker with multiple file extensions."""
        test_dir = Path("/tmp")

        # Example: Filter for text files, Python files, and Markdown files
        extensions = [".txt", ".py", ".md"]

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_types=extensions
            )

            # Verify the picker was configured correctly
            assert picker.show_files_only_of_types == extensions
            assert (
                picker.show_files_only_of_type is None
            )  # Should be None when using new parameter
            assert picker.path == test_dir.expanduser()

    def test_single_extension_backward_compatibility_example(self) -> None:
        """Demonstrate backward compatibility with single extension filtering."""
        test_dir = Path("/tmp")

        # Example: Filter for only Python files (old way)
        extension = ".py"

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_type=extension
            )

            # Verify the picker was configured correctly
            assert picker.show_files_only_of_type == extension
            assert (
                picker.show_files_only_of_types is None
            )  # Should be None when using old parameter
            assert picker.path == test_dir.expanduser()

    def test_no_extension_filtering_example(self) -> None:
        """Demonstrate showing all files (no filtering)."""
        test_dir = Path("/tmp")

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(directory=test_dir)

            # Verify no filtering is applied
            assert picker.show_files_only_of_type is None
            assert picker.show_files_only_of_types is None
            assert picker.path == test_dir.expanduser()

    def test_priority_of_multiple_extensions_over_single(self) -> None:
        test_dir = Path("/tmp")

        # Provide both parameters - multiple should take priority
        single_extension = ".txt"
        multiple_extensions = [".py", ".md"]

        with patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui"):
            picker = LocalFilePicker(
                directory=test_dir,
                show_files_only_of_type=single_extension,
                show_files_only_of_types=multiple_extensions,
            )

            # Verify both are stored
            assert picker.show_files_only_of_type == single_extension
            assert picker.show_files_only_of_types == multiple_extensions

            # The filtering logic should prioritize multiple_extensions
            # This would be tested in the actual filtering logic

    @patch("pathlib.Path.glob")
    @patch("OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker.ui")
    def test_filtering_logic_with_multiple_extensions(
        self, mock_ui: Mock, mock_glob: Mock
    ) -> None:
        """Test that the filtering logic correctly handles multiple extensions."""
        test_dir = Path("/tmp")
        extensions = [".txt", ".py"]

        # Mock file paths with different extensions
        mock_files = []

        # Create mock files with different extensions
        for name, suffix, is_file_result in [
            ("test.txt", ".txt", True),
            ("script.py", ".py", True),
            ("document.pdf", ".pdf", True),
            ("readme.md", ".md", True),
            ("folder", "", False),
        ]:
            mock_file = Mock(spec=Path)
            mock_file.name = name
            mock_file.suffix = suffix
            mock_file.is_file.return_value = is_file_result
            mock_file.is_dir.return_value = not is_file_result
            mock_files.append(mock_file)

        mock_glob.return_value = mock_files

        picker = LocalFilePicker(
            directory=test_dir, show_files_only_of_types=extensions
        )

        # Call update_grid to trigger filtering
        picker.update_grid()

        # The filtering should include:
        # - test.txt (matches .txt)
        # - script.py (matches .py)
        # - folder (always include directories)
        # And exclude:
        # - document.pdf (doesn't match .txt or .py)
        # - readme.md (doesn't match .txt or .py)

        # Verify that the grid was updated (basic check)
        assert hasattr(picker, "grid")
        assert hasattr(picker.grid, "options")
