from pathlib import Path
from typing import Any, Generator, TypeVar

import pytest
from nicegui.testing import Screen
from selenium.webdriver.remote.webelement import WebElement

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from tests.utils.builders.otanalytics_builders import MultiprocessingWorker
from tests.utils.ui_helpers import set_input_value

T = TypeVar("T")
YieldFixture = Generator[T, None, None]


class TestProjectInformation:
    """Tests for the project information form.

    These tests verify that the project information form works correctly with
    different date formats (ISO and German). The tests use JavaScript execution to
    set values directly in the form elements and trigger change events, which is a
    reliable approach for interacting with complex form elements in NiceGUI.

    Additionally, tests verify export (Save as...) and import (Open...) functionality
    by monkeypatching the NiceGUI file dialog methods to return deterministic paths.
    """

    @pytest.mark.timeout(300)
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
        target.shot("dummy")

    @pytest.mark.timeout(300)
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

        # Wait a moment for the UI to update
        target.wait(0.5)

        # Take a screenshot of the page
        target.shot("project_information_page")

        # Verify that the values were correctly set in the form
        # Get the current value of the project name input
        actual_project_name = target.selenium.execute_script(
            "return arguments[0].value;", project_name_input
        )
        assert actual_project_name == project_name, (
            f"Expected project name to be '{project_name}', but got "
            f"'{actual_project_name}'"
        )

        # Get the current value of the date input
        actual_date = target.selenium.execute_script(
            "return arguments[0].value;", date_input
        )
        assert (
            actual_date == date_value
        ), f"Expected date to be '{date_value}', but got '{actual_date}'"

        # Get the current value of the time input
        actual_time = target.selenium.execute_script(
            "return arguments[0].value;", time_input
        )
        assert (
            actual_time == time_value
        ), f"Expected time to be '{time_value}', but got '{actual_time}'"

    @pytest.mark.timeout(300)
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

        # Wait a moment for the UI to update
        target.wait(0.5)

        # Take a screenshot of the page
        target.shot("project_information_iso_format")

        # Verify that the values were correctly set in the form
        actual_project_name = target.selenium.execute_script(
            "return arguments[0].value;", project_name_input
        )
        assert actual_project_name == project_name, (
            f"Expected project name to be '{project_name}', but got "
            f"'{actual_project_name}'"
        )

        actual_date = target.selenium.execute_script(
            "return arguments[0].value;", date_input
        )
        assert (
            actual_date == date_value
        ), f"Expected date to be '{date_value}', but got '{actual_date}'"

        actual_time = target.selenium.execute_script(
            "return arguments[0].value;", time_input
        )
        assert (
            actual_time == time_value
        ), f"Expected time to be '{time_value}', but got '{actual_time}'"

    @pytest.mark.timeout(300)
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

        # Wait a moment for the UI to update
        target.wait(0.5)

        # Take a screenshot of the page
        target.shot("project_information_german_format")

        # Verify that the values were correctly set in the form
        actual_project_name = target.selenium.execute_script(
            "return arguments[0].value;", project_name_input
        )
        assert actual_project_name == project_name, (
            f"Expected project name to be '{project_name}', but got "
            f"'{actual_project_name}'"
        )

        actual_date = target.selenium.execute_script(
            "return arguments[0].value;", date_input
        )
        assert (
            actual_date == date_value
        ), f"Expected date to be '{date_value}', but got '{actual_date}'"

        actual_time = target.selenium.execute_script(
            "return arguments[0].value;", time_input
        )
        assert (
            actual_time == time_value
        ), f"Expected time to be '{time_value}', but got '{actual_time}'"

    @pytest.mark.timeout(300)
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
        def set_inputs(
            name: str, date_str: str, time_str: str
        ) -> tuple[WebElement, WebElement, WebElement]:
            name_el = target.find_by_css(
                f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
            )
            date_el = target.find_by_css(
                f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
            )
            time_el = target.find_by_css(
                f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
            )
            # clear and type via JS to avoid input event issues
            for el, value in [
                (name_el, name),
                (date_el, date_str),
                (time_el, time_str),
            ]:
                set_input_value(target, el, value)
            return name_el, date_el, time_el

        # Helper to read current values
        def get_inputs(
            name_el: WebElement, date_el: WebElement, time_el: WebElement
        ) -> tuple[str, str, str]:
            name_v = target.selenium.execute_script(
                "return arguments[0].value;", name_el
            )
            date_v = target.selenium.execute_script(
                "return arguments[0].value;", date_el
            )
            time_v = target.selenium.execute_script(
                "return arguments[0].value;", time_el
            )
            return name_v, date_v, time_v

        # Initial values to save
        v1_name = "Acceptance Save/Load Project"
        v1_date = "2023-05-24"
        v1_time = "06:00:00"
        name_el, date_el, time_el = set_inputs(v1_name, v1_date, v1_time)
        target.wait(0.3)

        # Patch NiceGuiUiFactory to bypass dialogs
        from pathlib import Path as _Path

        from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory

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

        # Helper to click a button by its label text
        def click_by_text(label: str) -> bool:
            script = (
                "var label=arguments[0];"
                "var candidates = Array.from(document.querySelectorAll('button, "
                ".q-btn'));"
                "var el = candidates.find(e => (e.innerText || e.textContent || '' )"
                ".trim() === label);"
                "if(!el){el = candidates.find(e => (e.innerText || e.textContent || "
                "'').includes(label));}"
                "if(el){el.click(); return true;} return false;"
            )
            return bool(target.selenium.execute_script(script, label))

        # Click Save (quick save) which falls back to Save As if no file exists
        assert click_by_text(
            resource_manager.get(ProjectKeys.LABEL_QUICK_SAVE)
        ), "Save button not found"
        target.wait(0.7)
        # Ensure file was created (if saving is allowed without sections)
        assert save_path.exists(), f"Expected saved config at {save_path}"

        # Change inputs to different values (simulate different project/new)
        v2_name = "Different Project Name"
        v2_date = "2024-01-15"
        v2_time = "07:30:00"
        name_el, date_el, time_el = set_inputs(v2_name, v2_date, v2_time)
        target.wait(0.2)

        # Click Open... to import previously saved config
        assert click_by_text(
            resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT)
        ), "Open button not found"
        # Wait for UI model to refresh
        target.wait(0.7)

        # Verify fields restored to saved values
        n, d, t = get_inputs(name_el, date_el, time_el)
        assert n == v1_name
        assert d == v1_date
        assert t == v1_time

        # Overwrite scenario: change fields again
        v3_name = "Temp Name Before Import"
        v3_date = "2025-08-13"
        v3_time = "08:45:00"
        name_el, date_el, time_el = set_inputs(v3_name, v3_date, v3_time)
        target.wait(0.2)

        # Import the same saved file; expect fields to match v1_* again
        assert click_by_text(
            resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT)
        ), "Open button not found (2nd time)"
        target.wait(0.7)
        n, d, t = get_inputs(name_el, date_el, time_el)
        assert n == v1_name
        assert d == v1_date
        assert t == v1_time


@pytest.mark.timeout(300)
def test_download_and_unzip_otcamera19(otcamera19_extracted_dir: Path) -> None:
    """Ensure the OTCamera19 test data can be downloaded and extracted.

    This also serves as a guard that the acceptance environment can access the
    public testdata release and that the fixture remembers the location under
    tests/data.
    """
    assert otcamera19_extracted_dir.exists(), "Expected tests/data directory to exist"
    matches = list(otcamera19_extracted_dir.glob("OTCamera19_FR20_2023-05-24*"))
    assert matches, "Expected extracted OTCamera19 test data in tests/data"
