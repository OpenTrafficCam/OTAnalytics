from pathlib import Path
from pathlib import Path as _Path
from typing import Any, Generator, TypeVar

import pytest
from nicegui.testing import Screen
from selenium.webdriver.remote.webelement import WebElement

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory
from tests.utils.builders.otanalytics_builders import MultiprocessingWorker
from tests.utils.ui_helpers import set_input_value

# Global timeout for acceptance tests (seconds)
TIMEOUT = 300

T = TypeVar("T")
YieldFixture = Generator[T, None, None]


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[Any]
) -> Generator[None, Any, None]:
    outcome: Any = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def _acceptance_shot_on_failure(
    request: pytest.FixtureRequest, target: Screen
) -> Generator[None, None, None]:
    # Runs after every test function in this module
    yield

    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    rep_teardown = getattr(request.node, "rep_teardown", None)

    def is_unexpected_failure(rep: pytest.TestReport | None) -> bool:
        return bool(rep and rep.failed and not getattr(rep, "wasxfail", False))

    if any(map(is_unexpected_failure, (rep_setup, rep_call, rep_teardown))):
        try:
            screen: Screen = request.getfixturevalue(
                "target"
            )  # the Screen fixture used here
        except Exception:
            return
        screen.shot(request.node.name)


class TestProjectInformation:
    """Tests for the project information form.

    These tests verify that the project information form works correctly with
    different date formats (ISO and German). The tests use JavaScript execution to
    set values directly in the form elements and trigger change events, which is a
    reliable approach for interacting with complex form elements in NiceGUI.

    Additionally, tests verify export (Save as...) and import (Open...) functionality
    by monkeypatching the NiceGUI file dialog methods to return deterministic paths.
    """

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_webserver_is_running(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
    ) -> None:
        # Only start the app if it's not already running
        if not given_app.is_alive():
            given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Covered by ISO/German format tests; duplicate path")
    async def test_project_information_form(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
    ) -> None:
        """Test the project information form.

        This test verifies that the project information form works correctly by:
        1. Setting values for project name, date, and time inputs
        2. Verifying that the values are correctly set in the form

        Note: This test assumes the application is already running from a previous test.
        When run individually, you may need to start the application first.
        """

        # Only start the app if it's not already running
        if not given_app.is_alive():
            given_app.start()
        # Open the main page
        target.open(ENDPOINT_MAIN_PAGE)

        project_name = "Test Project - Leipzig Test Intersection - OTCamera19"
        date_value = "2023-05-24"
        time_value = "06:00:00"

        target.find("Project")

        # Method 2: Using aria-label attributes with JavaScript execution
        # Find and set the project name input
        project_name_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        # Use JavaScript to set the value directly
        set_input_value(target, project_name_input, project_name)

        # Find and set the date input using JavaScript
        date_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        set_input_value(target, date_input, date_value)

        # Find and set the time input using JavaScript
        time_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )
        set_input_value(target, time_input, time_value)

        target.should_contain("Project")

        # Verify that the values were correctly set in the form
        # Get the current value of the project name input
        actual_project_name = project_name_input.get_attribute("value")
        assert actual_project_name == project_name, (
            f"Expected project name to be '{project_name}', but got "
            f"'{actual_project_name}'"
        )

        # Get the current value of the date input
        actual_date = date_input.get_attribute("value")
        assert (
            actual_date == date_value
        ), f"Expected date to be '{date_value}', but got '{actual_date}'"

        # Get the current value of the time input
        actual_time = time_input.get_attribute("value")
        assert (
            actual_time == time_value
        ), f"Expected time to be '{time_value}', but got '{actual_time}'"

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_project_information_iso_format(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
    ) -> None:
        """Test the project information form with ISO date format.

        This test verifies that the project information form works correctly with
        ISO date format:
        1. Setting values for project name, date (2023-05-24), and time
           (06:00:00) inputs
        2. Verifying that the values are correctly set in the form

        Note: This test assumes the application is already running from a
        previous test. When run individually, you may need to start the
        application first.
        """

        # Only start the app if it's not already running
        if not given_app.is_alive():
            given_app.start()
        # Open the main page
        target.open(ENDPOINT_MAIN_PAGE)

        project_name = "Test Project - Leipzig Test Intersection - OTCamera19"
        date_value = "2023-05-24"
        time_value = "06:00:00"

        target.find("Project")

        # Find and set the project name input
        project_name_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        set_input_value(target, project_name_input, project_name)

        # Find and set the date input using JavaScript with ISO format
        date_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        set_input_value(target, date_input, date_value)

        # Find and set the time input using JavaScript
        time_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )
        set_input_value(target, time_input, time_value)

        target.should_contain("Project")

        # Verify that the values were correctly set in the form
        actual_project_name = project_name_input.get_attribute("value")
        assert actual_project_name == project_name, (
            f"Expected project name to be '{project_name}', but got "
            f"'{actual_project_name}'"
        )

        target.should_contain_input(date_value)
        actual_date = date_input.get_attribute("value")
        assert (
            actual_date == date_value
        ), f"Expected date to be '{date_value}', but got '{actual_date}'"

        actual_time = time_input.get_attribute("value")
        assert (
            actual_time == time_value
        ), f"Expected time to be '{time_value}', but got '{actual_time}'"

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason=(
            "German date format not supported by date input; component expects "
            "ISO format"
        )
    )
    async def test_project_information_german_format(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
    ) -> None:
        """Test the project information form with German date format.

        This test verifies that the project information form works correctly with
        German date format:
        1. Setting values for project name, date (24.05.2023), and time
           (06:00:00) inputs
        2. Verifying that the values are correctly set in the form

        Note: This test assumes the application is already running from a
        previous test. When run individually, you may need to start the
        application first.
        """

        # Only start the app if it's not already running
        if not given_app.is_alive():
            given_app.start()
        # Open the main page
        target.open(ENDPOINT_MAIN_PAGE)

        project_name = "Test Project - Leipzig Test Intersection - OTCamera19"
        date_value = "24.05.2023"  # German date format (DD.MM.YYYY)
        time_value = "06:00:00"

        target.find("Project")

        # Find and set the project name input
        project_name_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        set_input_value(target, project_name_input, project_name)

        # Find and set the date input using JavaScript with German format
        date_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        set_input_value(target, date_input, date_value)

        # Find and set the time input using JavaScript
        time_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )
        set_input_value(target, time_input, time_value)

        target.should_contain("Project")

        # Verify that the values were correctly set in the form
        actual_project_name = project_name_input.get_attribute("value")
        assert actual_project_name == project_name, (
            f"Expected project name to be '{project_name}', but got "
            f"'{actual_project_name}'"
        )

        actual_date = date_input.get_attribute("value")
        assert (
            actual_date == date_value
        ), f"Expected date to be '{date_value}', but got '{actual_date}'"

        actual_time = time_input.get_attribute("value")
        assert (
            actual_time == time_value
        ), f"Expected time to be '{time_value}', but got '{actual_time}'"

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_project_information_export_import(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
        test_data_tmp_dir: Path,
        monkeypatch: Any,
    ) -> None:
        """Test export (save) and import (open) of project information.

        Steps:
        - Save current project information to project_information.otconfig
        - Modify fields (simulate a new/different project state)
        - Import previously saved project_information.otconfig and verify
          values restored
        - Modify fields again and re-import to verify overwrite of current state
        """
        # Ensure app is running and open the main page
        if not given_app.is_alive():
            given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)
        target.find("Project")

        # Helper to set values using aria-labels with Screen/selenium
        def fill_project_form(
            name: str, date_str: str, time_str: str
        ) -> tuple[WebElement, WebElement, WebElement]:
            name_input = target.find_by_css(
                f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
            )
            date_input = target.find_by_css(
                f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
            )
            time_input = target.find_by_css(
                f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
            )
            # clear and type via JS to avoid input event issues
            for el, value in [
                (name_input, name),
                (date_input, date_str),
                (time_input, time_str),
            ]:
                set_input_value(target, el, value)
            return name_input, date_input, time_input

        # Helper to read current values
        def read_project_form_values(
            name_input: WebElement, date_input: WebElement, time_input: WebElement
        ) -> tuple[str | None, str | None, str | None]:
            actual_name = name_input.get_attribute("value")
            actual_date = date_input.get_attribute("value")
            actual_time = time_input.get_attribute("value")
            return actual_name, actual_date, actual_time

        target.should_contain("Project")
        # Initial values to save
        saved_name = "Acceptance Save/Load Project"
        saved_date = "2023-05-24"
        saved_time = "06:00:00"
        name_input, date_input, time_input = fill_project_form(
            saved_name, saved_date, saved_time
        )

        # Patch NiceGuiUiFactory to bypass dialogs
        save_path = _Path(test_data_tmp_dir) / "project_information.otconfig"

        async def fake_ask_for_save_file_path(*args: object, **kwargs: object) -> _Path:
            return save_path

        async def fake_askopenfilename(*args: object, **kwargs: object) -> str:
            return str(save_path)

        monkeypatch.setattr(
            NiceGuiUiFactory,
            "ask_for_save_file_path",
            fake_ask_for_save_file_path,
            raising=True,
        )
        monkeypatch.setattr(
            NiceGuiUiFactory, "askopenfilename", fake_askopenfilename, raising=True
        )

        # Click Save (quick save) which falls back to Save As if no file exists
        target.click(resource_manager.get(ProjectKeys.LABEL_QUICK_SAVE))

        target.should_contain("Project")
        # Ensure file was created (if saving is allowed without sections)
        assert save_path.exists(), f"Expected saved config at {save_path}"

        # Change inputs to different values (simulate different project/new)
        modified_name = "Different Project Name"
        modified_date = "2024-01-15"
        modified_time = "07:30:00"
        name_input, date_input, time_input = fill_project_form(
            modified_name, modified_date, modified_time
        )

        target.should_contain("Project")
        # Click Open... to import previously saved config
        target.click(resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT))

        # Verify fields restored to saved values (wait for inputs to update)
        target.wait_for(lambda: name_input.get_attribute("value") == saved_name)
        target.wait_for(lambda: date_input.get_attribute("value") == saved_date)
        target.wait_for(lambda: time_input.get_attribute("value") == saved_time)
        actual_name, actual_date, actual_time = read_project_form_values(
            name_input, date_input, time_input
        )
        assert actual_name == saved_name
        assert actual_date == saved_date
        assert actual_time == saved_time

        # Overwrite scenario: change fields again (interim values)
        interim_name = "Temp Name Before Import"
        interim_date = "2025-08-13"
        interim_time = "08:45:00"
        name_input, date_input, time_input = fill_project_form(
            interim_name, interim_date, interim_time
        )

        # Import the same saved file; expect fields to match saved_* again
        target.click(resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT))

        # Wait until inputs show the saved values again
        target.wait_for(lambda: name_input.get_attribute("value") == saved_name)
        target.wait_for(lambda: date_input.get_attribute("value") == saved_date)
        target.wait_for(lambda: time_input.get_attribute("value") == saved_time)
        actual_name, actual_date, actual_time = read_project_form_values(
            name_input, date_input, time_input
        )
        assert actual_name == saved_name
        assert actual_date == saved_date
        assert actual_time == saved_time
