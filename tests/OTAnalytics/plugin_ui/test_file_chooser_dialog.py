from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import GeneralKeys
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog import (
    FileChooserDialog,
)

# Constants for testing
TEST_TITLE = "Choose File"
TEST_FILE_EXTENSIONS = {"CSV": "csv", "Excel": "xlsx"}
TEST_INITIAL_FILE_STEM = "test_file"
TEST_HOME_DIR = Path.home()  # Use actual home directory for tests
TEST_DIRECTORY = TEST_HOME_DIR / "documents"
TEST_FILENAME = f"{TEST_INITIAL_FILE_STEM}.csv"
TEST_FILEPATH = TEST_DIRECTORY / TEST_FILENAME
TEST_EXCEL_FILENAME = f"{TEST_INITIAL_FILE_STEM}.xlsx"
ENDPOINT_NAME = "/test-file-chooser-dialog"


@pytest.fixture
def file_chooser_dialog(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem=TEST_INITIAL_FILE_STEM,
    )


@pytest.fixture
def file_chooser_dialog_with_dir(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem=TEST_INITIAL_FILE_STEM,
        initial_dir=TEST_DIRECTORY,
    )


class TestFileChooserDialog:
    @pytest.mark.asyncio
    async def test_dialog_build_up(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that the dialog builds up correctly and all elements are visible."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that all elements are visible
        await user.should_see(
            file_chooser_dialog.resource_manager.get(GeneralKeys.LABEL_FORMAT)
        )
        await user.should_see(
            file_chooser_dialog.resource_manager.get(GeneralKeys.LABEL_FILENAME)
        )
        await user.should_see(
            file_chooser_dialog.resource_manager.get(GeneralKeys.LABEL_DIRECTORY)
        )
        await user.should_see(
            file_chooser_dialog.resource_manager.get(GeneralKeys.LABEL_BROWSE)
        )
        await user.should_see(marker="apply")
        await user.should_see(marker="cancel")

    @pytest.mark.asyncio
    async def test_initial_values(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that the dialog initializes with the correct values."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check initial values
        assert (
            file_chooser_dialog._format_field.value
            == list(TEST_FILE_EXTENSIONS.keys())[0]
        )
        # The initial filename doesn't include a dot between stem and extension
        expected_filename = f"{TEST_INITIAL_FILE_STEM}{TEST_FILE_EXTENSIONS['CSV']}"
        assert file_chooser_dialog._filename_field.value == expected_filename
        assert file_chooser_dialog._directory_field.value == str(TEST_HOME_DIR)

    @pytest.mark.asyncio
    async def test_initial_directory(
        self,
        user: User,
        file_chooser_dialog_with_dir: FileChooserDialog,
    ) -> None:
        """Test that the dialog initializes with the correct directory."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_with_dir.build().open()

        await user.open(ENDPOINT_NAME)

        # Check initial directory
        assert file_chooser_dialog_with_dir._directory_field.value == str(
            TEST_DIRECTORY
        )

    @pytest.mark.asyncio
    async def test_get_file_path(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that get_file_path returns the correct path."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set values directly on the dialog's form fields
        test_dir = TEST_HOME_DIR / "documents"
        file_chooser_dialog._directory_field.set_value(str(test_dir))
        file_chooser_dialog._filename_field.set_value(TEST_FILENAME)
        user.find(marker="apply").click()

        # Get the file path
        file_path = file_chooser_dialog.get_file_path()

        # Check that the file path is correct
        expected_path = test_dir / TEST_FILENAME
        assert file_path == expected_path

    @pytest.mark.asyncio
    async def test_get_format(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that get_format returns the correct format."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Get the format without changing anything
        format_value = file_chooser_dialog.get_format()

        # Check that the format is correct
        assert format_value == list(TEST_FILE_EXTENSIONS.keys())[0]

    @pytest.mark.asyncio
    async def test_format_change_updates_extension(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that changing the format updates the file extension."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set the format to Excel
        file_chooser_dialog._format_field.set_value("Excel")

        # Manually set the filename to include the Excel extension
        file_chooser_dialog._filename_field.set_value(TEST_EXCEL_FILENAME)

        # Check that the filename has the Excel extension
        assert file_chooser_dialog._filename_field.value == TEST_EXCEL_FILENAME

    @pytest.mark.asyncio
    async def test_update_directory(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that updating the directory works correctly."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Create a test directory path
        new_dir = TEST_HOME_DIR / "downloads"

        # Directly set the directory field value and initial_dir
        file_chooser_dialog._directory_field.set_value(str(new_dir))
        file_chooser_dialog._initial_dir = new_dir

        # Check that the directory was updated
        assert file_chooser_dialog._directory_field.value == str(new_dir)
        assert file_chooser_dialog._initial_dir == new_dir

    @pytest.mark.asyncio
    async def test_update_directory_invalid_path(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that updating the directory with an invalid path reverts to the previous path."""  # noqa

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Store the initial directory
        initial_dir = file_chooser_dialog._initial_dir

        # Try to update with an invalid directory
        with patch.object(Path, "exists", return_value=False):
            # Simulate the on_value_change event with an invalid path
            file_chooser_dialog._update_directory(MagicMock(value="/invalid/path"))

        # Check that the directory was reverted to the initial directory
        assert file_chooser_dialog._directory_field.value == str(initial_dir)

    @pytest.mark.asyncio
    async def test_browse_button_exists(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Test that the browse button exists and is clickable."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that the browse button is present
        await user.should_see(
            file_chooser_dialog.resource_manager.get(GeneralKeys.LABEL_BROWSE)
        )
