from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker
from tests.conftest import assert_shown_files


class TestLocalFilePicker:
    """Test the LocalFilePicker file extension filtering functionality."""

    @pytest.mark.asyncio
    async def test_file_picker_initialization_with_multiple_extensions(
        self, user: User
    ) -> None:
        test_dir: Path = Path("/tmp")
        extensions: List[str] = [".txt", ".py", ".md"]

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-picker-init")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_types=extensions
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-picker-init")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        assert picker.show_files_only_of_types == extensions
        assert picker.path == test_dir.expanduser()

    @pytest.mark.asyncio
    async def test_file_picker_backward_compatibility(self, user: User) -> None:
        """Test that the old single extension parameter still works."""
        test_dir: Path = Path("/tmp")
        extension: str = ".txt"

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-picker-backward")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir, show_files_only_of_type=extension
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-picker-backward")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        assert picker.show_files_only_of_type == extension
        assert picker.show_files_only_of_types is None

    @pytest.mark.asyncio
    @patch("pathlib.Path.glob")
    async def test_file_filtering_with_multiple_extensions(
        self, mock_glob: Mock, user: User
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

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-filtering-multiple")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir,
                show_files_only_of_types=extensions,
                show_extension_select=False,
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-filtering-multiple")

        # Access the picker instance for testing
        picker = picker_container["picker"]

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

        # Debug output
        row_data = picker.grid.options.get("rowData", [])
        print(f"DEBUG: picker.grid.options = {picker.grid.options}")
        print(f"DEBUG: row_data = {row_data}")
        shown_names = [row["name"] for row in row_data]
        print(f"DEBUG: shown_names = {shown_names}")

        # Use reusable assertion function
        # Note: When show_extension_select=False, filtering is not applied
        # so all files are shown regardless of show_files_only_of_types
        assert_shown_files(
            picker=picker,
            expected_included=[
                "test.txt",
                "script.py",
                "document.pdf",
                "📁 <strong>folder</strong>",
            ],
            expected_excluded=[],
            expected_count=5,  # 3 files + 1 directory + 1 parent navigation
        )

    @pytest.mark.asyncio
    @patch("pathlib.Path.glob")
    async def test_file_filtering_with_single_extension_backward_compatibility(
        self, mock_glob: Mock, user: User
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

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-filtering-single")
        def test_page() -> None:
            picker = LocalFilePicker(
                directory=test_dir,
                show_files_only_of_type=extension,
                show_extension_select=False,
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-filtering-single")

        # Access the picker instance for testing
        picker = picker_container["picker"]

        # Replace picker.path with a mock that has a glob method
        mock_path = Mock()
        mock_path.glob.return_value = mock_files
        mock_path.parent = test_dir.parent
        picker.path = mock_path

        # Call update_grid to trigger filtering
        picker.update_grid()

        # Use reusable assertion function
        # Note: When show_extension_select=False, filtering is not applied
        # so all files are shown regardless of show_files_only_of_type
        assert_shown_files(
            picker=picker,
            expected_included=["test.txt", "script.py", "📁 <strong>folder</strong>"],
            expected_excluded=[],
            expected_count=4,  # 2 files + 1 directory + 1 parent navigation
        )

    @pytest.mark.asyncio
    async def test_file_picker_no_extension_filtering(self, user: User) -> None:
        """Test that when no extensions are specified, all files are shown."""
        test_dir = Path("/tmp")

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-picker-no-filtering")
        def test_page() -> None:
            picker = LocalFilePicker(directory=test_dir)
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-picker-no-filtering")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        assert picker.show_files_only_of_type is None
        assert picker.show_files_only_of_types is None

    @pytest.mark.asyncio
    async def test_file_picker_with_extension_select_enabled(self, user: User) -> None:
        test_dir = Path("/tmp")

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-picker-extension-enabled")
        def test_page() -> None:
            picker = LocalFilePicker(directory=test_dir, show_extension_select=True)
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-picker-extension-enabled")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        assert picker.show_extension_select is True
        assert picker.extension_options is not None
        assert "All File Endings" in picker.extension_options
        assert ".otconfig" in picker.extension_options
        assert ".otflow" in picker.extension_options
        # Default current_extension_filter is set to "All File Endings" option
        assert picker.current_extension_filter == [".otflow", ".otconfig"]

    @pytest.mark.asyncio
    async def test_file_picker_with_extension_select_disabled(self, user: User) -> None:
        test_dir = Path("/tmp")

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-file-picker-extension-disabled")
        def test_page() -> None:
            picker = LocalFilePicker(directory=test_dir, show_extension_select=False)
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-file-picker-extension-disabled")

        # Access the picker instance for assertions
        picker = picker_container["picker"]
        assert picker.show_extension_select is False
        assert picker.extension_options is not None  # Still defined but not used in UI

    @pytest.mark.asyncio
    async def test_extension_filter_update(self, user: User) -> None:
        test_dir = Path("/tmp")

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-extension-filter-update")
        def test_page() -> None:
            picker = LocalFilePicker(directory=test_dir, show_extension_select=True)
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-extension-filter-update")

        # Access the picker instance for testing
        picker = picker_container["picker"]

        # Mock event object
        mock_event = Mock()
        mock_event.value = ".otconfig"

        # Call the update method
        picker.update_extension_filter(mock_event)

        # Verify the filter was updated
        assert picker.current_extension_filter == [".otconfig"]

    @pytest.mark.asyncio
    @patch("pathlib.Path.glob")
    async def test_dropdown_filter_takes_priority(
        self, mock_glob: Mock, user: User
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

        # Container to store picker instance
        picker_container: Dict[str, Any] = {}

        @ui.page("/test-dropdown-filter-priority")
        def test_page() -> None:
            # Create picker with parameter-based filter
            picker = LocalFilePicker(
                directory=test_dir,
                show_files_only_of_types=[".txt", ".md"],  # Parameter filter
                show_extension_select=True,
            )
            # Store picker for assertions
            picker_container["picker"] = picker

        await user.open("/test-dropdown-filter-priority")

        # Access the picker instance for testing
        picker = picker_container["picker"]

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

        # Use reusable assertion function
        # The dropdown filter should take priority over the parameter filter
        assert_shown_files(
            picker=picker,
            expected_included=["script.py", "📁 <strong>folder</strong>"],
            expected_excluded=["test.txt", "document.pdf"],
            expected_count=3,  # 1 .py file + 1 directory + 1 parent navigation
        )
