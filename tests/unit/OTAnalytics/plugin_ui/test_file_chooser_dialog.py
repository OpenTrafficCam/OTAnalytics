from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import FileChooserDialogKeys
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog import (
    MARKER_DIRECTORY,
    MARKER_FILENAME,
    MARKER_FORMAT,
    FileChooserDialog,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY,
    MARKER_CANCEL,
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
        enforce_suffix=False,
    )


@pytest.fixture
def file_chooser_dialog_with_dir(resource_manager: Mock) -> FileChooserDialog:
    # Mock Path.exists to return True so the directory is accepted
    with patch.object(Path, "exists", return_value=True):
        return FileChooserDialog(
            resource_manager=resource_manager,
            title=TEST_TITLE,
            file_extensions=TEST_FILE_EXTENSIONS,
            initial_file_stem=TEST_INITIAL_FILE_STEM,
            initial_dir=TEST_DIRECTORY,
            enforce_suffix=False,
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
            file_chooser_dialog.resource_manager.get(FileChooserDialogKeys.LABEL_FORMAT)
        )
        await user.should_see(
            file_chooser_dialog.resource_manager.get(
                FileChooserDialogKeys.LABEL_FILENAME
            )
        )
        await user.should_see(
            file_chooser_dialog.resource_manager.get(
                FileChooserDialogKeys.LABEL_DIRECTORY
            )
        )
        await user.should_see(
            file_chooser_dialog.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE)
        )
        await user.should_see(marker=MARKER_APPLY)
        await user.should_see(marker=MARKER_CANCEL)

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
        # The initial filename includes a dot between stem and extension
        expected_filename = f"{TEST_INITIAL_FILE_STEM}.{TEST_FILE_EXTENSIONS['CSV']}"
        assert file_chooser_dialog._filename_field is not None
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

        # Set the format to Excel using the user fixture
        user.find(marker=MARKER_FORMAT).click()
        user.find("Excel").click()

        # Manually set the filename to include the Excel extension using the user fixture # noqa
        user.find(marker=MARKER_FILENAME).clear().type(TEST_EXCEL_FILENAME)

        # Check that the filename has the Excel extension
        assert file_chooser_dialog._filename_field is not None
        assert file_chooser_dialog._filename_field.value == TEST_EXCEL_FILENAME

    @pytest.mark.asyncio
    async def test_update_directory_invalid_path_keeps_typed_value(
        self,
        user: User,
        file_chooser_dialog: FileChooserDialog,
    ) -> None:
        """Typing a non-existent path keeps the typed value but does not update _initial_dir."""  # noqa

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        initial_dir = file_chooser_dialog._initial_dir

        with patch.object(Path, "exists", return_value=False):
            user.find(marker=MARKER_DIRECTORY).clear().type("/invalid/path")
            user.find(marker=MARKER_FILENAME).click()

        assert file_chooser_dialog._directory_field.value == "/invalid/path"
        assert file_chooser_dialog._initial_dir == initial_dir

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
            file_chooser_dialog.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE)
        )


TEST_CONTEXT_FILE_TYPE = "events"


@pytest.fixture
def file_chooser_dialog_export(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem=TEST_INITIAL_FILE_STEM,
        context_file_type=TEST_CONTEXT_FILE_TYPE,
        enforce_suffix=True,
    )


@pytest.fixture
def file_chooser_dialog_save(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions={"otconfig": "otconfig", "otflow": "otflow"},
        initial_file_stem=TEST_INITIAL_FILE_STEM,
        context_file_type="",
        enforce_suffix=True,
    )


@pytest.fixture
def file_chooser_dialog_open(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem="",
        enforce_suffix=False,
    )


class TestFileChooserDialogModes:
    @pytest.mark.asyncio
    async def test_export_mode_locked_suffix(
        self, user: User, file_chooser_dialog_export: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_export.build().open()

        await user.open(ENDPOINT_NAME)

        assert file_chooser_dialog_export._filename_stem_field is not None
        assert file_chooser_dialog_export._filename_suffix_field is not None
        assert (
            file_chooser_dialog_export._filename_stem_field.value
            == TEST_INITIAL_FILE_STEM
        )
        assert file_chooser_dialog_export._filename_suffix_field.value == ".events.csv"
        assert file_chooser_dialog_export.get_file_stem() == TEST_INITIAL_FILE_STEM
        assert file_chooser_dialog_export.get_export_format_extension() == ".csv"
        assert (
            file_chooser_dialog_export.get_file_path()
            == Path.home() / f"{TEST_INITIAL_FILE_STEM}.events.csv"
        )

    @pytest.mark.asyncio
    async def test_save_mode_locked_extension_follows_format(
        self, user: User, file_chooser_dialog_save: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_save.build().open()

        await user.open(ENDPOINT_NAME)

        assert file_chooser_dialog_save._filename_stem_field is not None
        assert file_chooser_dialog_save._filename_suffix_field is not None
        assert file_chooser_dialog_save._filename_suffix_field.value == ".otconfig"
        # Switch the format dropdown
        user.find(marker=MARKER_FORMAT).click()
        user.find("otflow").click()

        assert file_chooser_dialog_save._filename_suffix_field.value == ".otflow"
        assert (
            file_chooser_dialog_save._filename_stem_field.value
            == TEST_INITIAL_FILE_STEM
        )

    @pytest.mark.asyncio
    async def test_open_mode_has_no_suffix_field(
        self, user: User, file_chooser_dialog_open: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_open.build().open()

        await user.open(ENDPOINT_NAME)

        assert file_chooser_dialog_open._filename_suffix_field is None
        # Legacy single field is still present
        assert file_chooser_dialog_open._filename_field is not None

    @pytest.mark.asyncio
    async def test_browse_strips_matching_suffix_in_export_mode(
        self, user: User, file_chooser_dialog_export: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_export.build().open()

        await user.open(ENDPOINT_NAME)

        file_chooser_dialog_export._set_filename_from_picked("trip_summary.events.csv")

        assert file_chooser_dialog_export._filename_stem_field is not None
        assert file_chooser_dialog_export._filename_stem_field.value == "trip_summary"

    @pytest.mark.asyncio
    async def test_browse_keeps_unrelated_name_as_stem(
        self, user: User, file_chooser_dialog_export: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_export.build().open()

        await user.open(ENDPOINT_NAME)

        file_chooser_dialog_export._set_filename_from_picked("unrelated.xlsx")

        assert file_chooser_dialog_export._filename_stem_field is not None
        assert file_chooser_dialog_export._filename_stem_field.value == "unrelated"
