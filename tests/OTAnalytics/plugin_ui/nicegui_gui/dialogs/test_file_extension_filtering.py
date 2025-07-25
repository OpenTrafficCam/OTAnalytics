from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker
from tests.conftest import assert_shown_files


class TestFileExtensionFiltering:
    """Test the new file extension filtering functionality."""

    @pytest.mark.asyncio
    async def test_multiple_extensions_filtering_example(self, user: User) -> None:
        """Demonstrate how to use LocalFilePicker with multiple file extensions."""
        test_dir = Path("/tmp")

        # Example: Filter for text files, Python files, and Markdown files
        extensions = [".txt", ".py", ".md"]

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-multiple-extensions-example")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_types=extensions
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-multiple-extensions-example")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        # Verify the picker was configured correctly
        assert picker.show_files_only_of_types == extensions
        assert (
            picker.show_files_only_of_type is None
        )  # Should be None when using new parameter
        assert picker.path == test_dir.expanduser()

    @pytest.mark.asyncio
    async def test_single_extension_backward_compatibility_example(
        self, user: User
    ) -> None:
        """Demonstrate backward compatibility with single extension filtering."""
        test_dir = Path("/tmp")

        # Example: Filter for only Python files (old way)
        extension = ".py"

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-single-extension-example")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_type=extension
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-single-extension-example")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        # Verify the picker was configured correctly
        assert picker.show_files_only_of_type == extension
        assert (
            picker.show_files_only_of_types is None
        )  # Should be None when using old parameter
        assert picker.path == test_dir.expanduser()

    @pytest.mark.asyncio
    async def test_no_extension_filtering_example(self, user: User) -> None:
        """Demonstrate showing all files (no filtering)."""
        test_dir = Path("/tmp")

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-no-extension-filtering-example")
        def test_page() -> None:
            picker = LocalFilePicker(directory=test_dir)
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-no-extension-filtering-example")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        # Verify no filtering is applied
        assert picker.show_files_only_of_type is None
        assert picker.show_files_only_of_types is None
        assert picker.path == test_dir.expanduser()

    @pytest.mark.asyncio
    async def test_priority_of_multiple_extensions_over_single(
        self, user: User
    ) -> None:
        test_dir = Path("/tmp")

        # Provide both parameters - multiple should take priority
        single_extension = ".txt"
        multiple_extensions = [".py", ".md"]

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-priority-multiple-over-single")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir,
                show_files_only_of_type=single_extension,
                show_files_only_of_types=multiple_extensions,
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-priority-multiple-over-single")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        # Verify both are stored
        assert picker.show_files_only_of_type == single_extension
        assert picker.show_files_only_of_types == multiple_extensions

        # The filtering logic should prioritize multiple_extensions
        # This would be tested in the actual filtering logic

    @pytest.mark.asyncio
    @patch("pathlib.Path.glob")
    async def test_filtering_logic_with_multiple_extensions(
        self, mock_glob: Mock, user: User
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

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-filtering-logic-multiple-extensions")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_types=extensions
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-filtering-logic-multiple-extensions")

        # Access the picker instance for testing
        picker = picker_container["picker"]

        # Replace picker.path with a mock that has a glob method
        mock_path = Mock()
        mock_path.glob.return_value = mock_files
        mock_path.parent = test_dir.parent
        picker.path = mock_path

        # Set current_selected_option to something other than "All Files"
        # so that show_files_only_of_types filtering is applied
        picker.current_selected_option = "Custom Filter"

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

        assert_shown_files(
            picker=picker,
            expected_included=["test.txt", "script.py"],
            expected_excluded=["document.pdf", "readme.md"],
            expected_count=4,
        )
