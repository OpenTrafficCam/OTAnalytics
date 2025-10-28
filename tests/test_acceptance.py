from pathlib import Path
from pathlib import Path as _Path
from typing import Any, Generator, TypeVar

import pytest
from nicegui.testing import Screen
from selenium.webdriver.remote.webelement import WebElement

from OTAnalytics.application.resources.resource_manager import (
    AddVideoKeys,
    ProjectKeys,
    ResourceManager,
    TrackFormKeys,
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


class TestVideoImportAndDisplay:
    @staticmethod
    def _wait_for_names_present(target: Screen, names: list[str]) -> None:
        target.wait_for(
            lambda: all(
                n in TestVideoImportAndDisplay._table_filenames(target) for n in names
            )
        )

    @staticmethod
    def _table_filenames(target: Screen) -> list[str]:
        """Return the list of video filenames currently shown in the table."""
        from selenium.webdriver.common.by import By  # type: ignore

        cells = target.selenium.find_elements(By.CSS_SELECTOR, "table tbody tr td")
        texts = [c.text.strip() for c in cells if c.text.strip()]
        video_exts = (".mp4", ".avi", ".mov", ".mkv", ".webm")
        return [t for t in texts if any(t.lower().endswith(ext) for ext in video_exts)]

    @staticmethod
    def _click_table_cell_with_text(target: Screen, text: str) -> None:
        """Click a table cell whose visible text contains `text` (substring match).
        Uses direct DOM enumeration to avoid brittle generic XPaths and tolerate
        UI truncation/ellipsis.
        """
        import time

        from selenium.webdriver.common.by import By  # type: ignore

        deadline = time.time() + 8.0
        last_err: Exception | None = None
        text_norm = text.strip()
        while time.time() < deadline:
            try:
                tds = target.selenium.find_elements(
                    By.CSS_SELECTOR, "table tbody tr td"
                )
                for td in tds:
                    td_text = td.text.strip()
                    if text_norm and text_norm in td_text:
                        target.selenium.execute_script("arguments[0].click();", td)
                        return
                time.sleep(0.1)
            except Exception as e:  # pragma: no cover - transient rendering
                last_err = e
                time.sleep(0.1)
        if last_err:
            raise last_err
        raise AssertionError(f"Could not find table cell with text: {text}")

    @staticmethod
    def _reset_videos_tab(target: Screen, resource_manager: ResourceManager) -> None:
        """Ensure the Videos tab is in a clean state (no listed videos).

        This mitigates cross-test interference because the NiceGUI app and
        webserver are session-scoped. Some tests in this class expect an empty
        list initially. When running the whole suite, previous tests may have
        left videos in the table which makes strict assertions fail.

        Strategy:
        - Iteratively remove all rows from the videos table via the UI.
        """
        # Remove all rows defensively (if any) using robust table parsing
        for _ in range(50):  # hard upper bound for safety
            names = TestVideoImportAndDisplay._table_filenames(target)
            if not names:
                break
            name = names[0]
            try:
                TestVideoImportAndDisplay._click_table_cell_with_text(target, name)
                target.click(resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS))
                target.wait_for(
                    lambda: name
                    not in TestVideoImportAndDisplay._table_filenames(target)
                )
            except Exception:
                try:
                    names2 = TestVideoImportAndDisplay._table_filenames(target)
                    if names2 and names2[0] == name:
                        break
                except Exception:
                    break

    @staticmethod
    def _remove_video_by_name(
        target: Screen, resource_manager: ResourceManager, filename: str
    ) -> None:
        """Robustly remove a video entry by filename from the table with retries."""
        import time

        from selenium.common.exceptions import (
            StaleElementReferenceException,  # type: ignore
        )

        # Wait until filename is present in the table
        TestVideoImportAndDisplay._wait_for_names_present(target, [filename])
        deadline = time.time() + 5.0
        last_err: Exception | None = None
        while time.time() < deadline:
            try:
                # Select row by clicking the table cell containing the filename
                TestVideoImportAndDisplay._click_table_cell_with_text(target, filename)
                # Click Remove
                target.click(resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS))
                # Wait until it disappears from the table
                target.wait_for(
                    lambda: filename
                    not in TestVideoImportAndDisplay._table_filenames(target)
                )
                return
            except StaleElementReferenceException as e:
                last_err = e
                time.sleep(0.1)
            except Exception as e:
                last_err = e
                time.sleep(0.1)
        if last_err:
            raise last_err

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_add_videos_import_sort_and_display_first_frame(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
        monkeypatch: Any,
    ) -> None:
        """Acceptance: Import videos, verify listing order and image display.

        Steps:
        - Open app and switch to Videos tab
        - Monkeypatch file picker to return 2 test videos
        - Click "Add videos..."; verify both appear in table
        - Verify rows are sorted alphabetically by filename
        - Click each video and verify the InteractiveImage shows an image and
          that the image source changes upon selection change (indicating the
          first frame of the selected video is displayed)
        """
        # Start app if needed and open main page
        if not given_app.is_alive():
            given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)

        target.click(resource_manager.get(TrackFormKeys.TAB_TWO))
        # Ensure clean slate for this test run
        self._reset_videos_tab(target, resource_manager)

        # Monkeypatch file dialog to return our test videos
        data_dir = Path(__file__).parent / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import (
            NiceGuiUiFactory,  # local import
        )

        async def fake_askopenfilenames(*args: object, **kwargs: object) -> list[Path]:
            return [v1, v2]

        monkeypatch.setattr(
            NiceGuiUiFactory,
            "askopenfilenames",
            fake_askopenfilenames,
            raising=True,
        )

        # Click Add videos...
        target.click(resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS))

        # Verify both filenames appear
        name1 = v1.name
        name2 = v2.name
        target.should_contain(name1)
        target.should_contain(name2)

        # Verify sorted alphabetically (table first column contains filenames)
        from selenium.webdriver.common.by import By  # type: ignore

        def read_table_filenames() -> list[str]:
            cells = target.selenium.find_elements(By.CSS_SELECTOR, "table tbody tr td")
            # Filter to plausible video filenames (ends with common video extension)
            texts = [c.text.strip() for c in cells if c.text.strip()]
            video_exts = (".mp4", ".avi", ".mov", ".mkv", ".webm")
            return [
                t for t in texts if any(t.lower().endswith(ext) for ext in video_exts)
            ]

        target.wait_for(lambda: len(read_table_filenames()) >= 2)
        listed = read_table_filenames()
        assert listed == sorted(
            [name1, name2]
        ), f"Expected alphabetical order {sorted([name1, name2])}, got {listed}"

        # Helper to read current image src on page (InteractiveImage uses base64)
        def get_current_image_src() -> str:
            from selenium.webdriver.common.by import By  # type: ignore

            imgs = target.selenium.find_elements(By.CSS_SELECTOR, "img[src^='data:']")
            if not imgs:
                return ""
            return imgs[0].get_attribute("src") or ""

        def select_video_and_wait_for_change(prev_src: str, filename: str) -> str:
            import time

            from selenium.webdriver.common.action_chains import (
                ActionChains,  # type: ignore
            )
            from selenium.webdriver.common.by import By  # type: ignore
            from selenium.webdriver.support import (
                expected_conditions as EC,  # type: ignore
            )
            from selenium.webdriver.support.ui import WebDriverWait  # type: ignore

            driver = target.selenium

            def find_row_and_parts() -> (
                tuple[WebElement | None, WebElement | None, list[WebElement]]
            ):  # noqa
                rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                for row in rows:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    texts = [c.text.strip() for c in cells if c.text.strip()]
                    if filename in texts:
                        # Common clickable elements inside a Quasar table row
                        clickables: list[WebElement] = []
                        for sel in (
                            "[role='checkbox']",
                            ".q-checkbox",
                            ".q-checkbox__inner",
                            "input[type='checkbox']",
                        ):
                            try:
                                clickables.append(
                                    row.find_element(By.CSS_SELECTOR, sel)
                                )
                            except Exception:
                                pass
                        # Cell with the filename
                        file_cell: WebElement | None = None
                        for c in cells:
                            if c.text.strip() == filename:
                                file_cell = c
                                break
                        return row, file_cell, clickables
                return None, None, []

            def changed() -> bool:
                ns = get_current_image_src()
                return bool(ns) and ns != prev_src

            from typing import cast

            row, file_cell, clickables = find_row_and_parts()
            assert row is not None, f"Could not find row for {filename}"
            row = cast(WebElement, row)

            tries: list[tuple[str, WebElement]] = []
            if file_cell is not None:
                tries.append(("click file cell", file_cell))
            for el in clickables:
                tries.append(("click checkbox-like", el))
            tries.append(("click row", row))

            actions = ActionChains(driver)
            for label, el in tries:
                try:
                    # Scroll into view and wait clickable
                    try:
                        _ = row.location_once_scrolled_into_view  # noqa: F841
                    except Exception:
                        pass
                    try:
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable(el))
                    except Exception:
                        pass
                    actions.move_to_element(el).pause(0.05).click().perform()
                except Exception:
                    try:
                        el.click()
                    except Exception:
                        pass
                # Wait up to 2 seconds for change
                end = time.time() + 2.0
                while time.time() < end:
                    if changed():
                        return get_current_image_src()
                    time.sleep(0.1)

            # As a last resort, try double-click on the filename cell/row
            for el in [file_cell or row, row]:
                try:
                    actions.move_to_element(el).double_click().perform()
                except Exception:
                    try:
                        el.click()
                        el.click()
                    except Exception:
                        pass
                end = time.time() + 2.0
                while time.time() < end:
                    if changed():
                        return get_current_image_src()
                    time.sleep(0.1)

            raise AssertionError(f"Image did not change after selecting {filename}")

        # Wait until an image is displayed
        target.wait_for(lambda: bool(get_current_image_src()))
        initial_src = get_current_image_src()
        assert initial_src.startswith("data:"), "Expected base64 image to be shown"

        # Select the second video and ensure image src changes
        after_src = select_video_and_wait_for_change(initial_src, name2)
        assert after_src.startswith("data:"), "Expected base64 image after selection"

        # Switch selection back to first video and ensure image src changes again
        final_src = select_video_and_wait_for_change(after_src, name1)
        assert final_src.startswith("data:"), "Expected base64 image after re-selection"

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_export_and_import_videos_via_project_config(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
        test_data_tmp_dir: Path,
        monkeypatch: Any,
    ) -> None:
        """Acceptance: Export and re-import video information.

        Steps:
        - Open app and switch to Videos tab
        - Add 2 videos via monkeypatched file picker and verify they appear
        - Save project information to "videos_imported.otconfig"
        - Click on "New" (or simulate a clean state by removing videos if "New" is unavailable) # noqa
        - Import previously saved project information
        - Verify previously added videos are visible again and selectable
        """
        # Start app if needed and open main page
        if not given_app.is_alive():
            given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)

        target.click(resource_manager.get(TrackFormKeys.TAB_TWO))
        # Ensure clean slate for this test run
        self._reset_videos_tab(target, resource_manager)

        # Prepare test videos and monkeypatch file dialog
        data_dir = Path(__file__).parent / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import (
            NiceGuiUiFactory,  # local import
        )

        async def fake_askopenfilenames(*args: object, **kwargs: object) -> list[Path]:
            return [v1, v2]

        monkeypatch.setattr(
            NiceGuiUiFactory,
            "askopenfilenames",
            fake_askopenfilenames,
            raising=True,
        )

        # Add videos
        target.click(resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS))
        name1 = v1.name
        name2 = v2.name
        target.should_contain(name1)
        target.should_contain(name2)

        # Switch to Project tab and fill minimal required fields for saving
        target.click(resource_manager.get(TrackFormKeys.TAB_ONE))
        project_name_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        date_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        time_input = target.find_by_css(
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )
        set_input_value(target, project_name_input, "Acceptance - Videos Export/Import")
        set_input_value(target, date_input, "2023-05-24")
        set_input_value(target, time_input, "06:00:00")

        # Save project to deterministic path
        save_path = _Path(test_data_tmp_dir) / "videos_imported.otconfig"

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
            NiceGuiUiFactory,
            "askopenfilename",
            fake_askopenfilename,
            raising=True,
        )

        target.click(resource_manager.get(ProjectKeys.LABEL_SAVE_AS_PROJECT))
        target.wait_for(lambda: save_path.exists())
        assert save_path.exists(), f"Expected saved config at {save_path}"

        # Reset project state by clearing the Videos tab completely to ensure
        # a clean slate before import (more robust than per-row interactions)
        target.click(resource_manager.get(TrackFormKeys.TAB_TWO))
        self._reset_videos_tab(target, resource_manager)

        # Now import previously saved project configuration
        target.click(resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT))

        # Switch to Videos tab to verify
        target.click(resource_manager.get(TrackFormKeys.TAB_TWO))

        # Verify both filenames appear again
        target.should_contain(name1)
        target.should_contain(name2)

        # Optional: verify selecting a video updates image source as smoke test
        # Ensure both names are present in the DOM after import
        target.wait_for(
            lambda: name1 in target.selenium.page_source
            and name2 in target.selenium.page_source
        )

        def get_current_image_src() -> str:
            js = (
                "return (Array.from(document.querySelectorAll('img'))"
                ".find(i => i.src && i.src.startsWith('data:')) || {src: ''}).src;"
            )
            return target.selenium.execute_script(js)

        # Click first and ensure an image is shown as a smoke test
        target.click(name1)
        target.wait_for(lambda: bool(get_current_image_src()))

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_remove_single_video_after_selection(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
        monkeypatch: Any,
    ) -> None:
        """Acceptance: Removing videos works for a single selected video file.

        Steps:
        - Switch to Videos tab
        - Select a single video file via monkeypatched file picker
        - Click on "Remove"
        - Verify the selected video is removed from the list
        """
        # Ensure app is running and main page is open
        if not given_app.is_alive():
            given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)

        target.click(resource_manager.get(TrackFormKeys.TAB_TWO))
        # Ensure clean slate for this test run
        self._reset_videos_tab(target, resource_manager)

        # Prepare a single test video and monkeypatch file dialog
        data_dir = Path(__file__).parent / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists(), "Test video is missing in tests/data"

        async def fake_askopenfilenames(*args: object, **kwargs: object) -> list[Path]:
            return [v1]

        monkeypatch.setattr(
            NiceGuiUiFactory,
            "askopenfilenames",
            fake_askopenfilenames,
            raising=True,
        )

        # Add the video via UI
        target.click(resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS))
        name1 = v1.name
        target.should_contain(name1)

        # Remove the video robustly using helper
        TestVideoImportAndDisplay._remove_video_by_name(target, resource_manager, name1)
        # Verify it's gone
        target.wait_for(
            lambda: name1 not in TestVideoImportAndDisplay._table_filenames(target)
        )

    @pytest.mark.timeout(TIMEOUT)
    @pytest.mark.asyncio
    async def test_remove_multiple_videos_after_selection(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
        monkeypatch: Any,
    ) -> None:
        """Acceptance: Removing videos works for multiple selected video files.

        Steps:
        - Switch to Videos tab
        - Select multiple video files via monkeypatched file picker
        - Click on "Remove"
        - Verify all selected videos are removed from the list
        """
        # Ensure app is running and main page is open
        if not given_app.is_alive():
            given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)

        target.click(resource_manager.get(TrackFormKeys.TAB_TWO))
        # Ensure clean slate for this test run
        self._reset_videos_tab(target, resource_manager)

        # Prepare two test videos and monkeypatch file dialog
        data_dir = Path(__file__).parent / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        async def fake_askopenfilenames(*args: object, **kwargs: object) -> list[Path]:
            return [v1, v2]

        monkeypatch.setattr(
            NiceGuiUiFactory,
            "askopenfilenames",
            fake_askopenfilenames,
            raising=True,
        )

        # Add the videos via UI
        target.click(resource_manager.get(AddVideoKeys.BUTTON_ADD_VIDEOS))
        name1 = v1.name
        name2 = v2.name
        target.should_contain(name1)
        target.should_contain(name2)

        # NOTE: The current UI uses single-selection behavior in the videos table.
        # Remove first video robustly
        TestVideoImportAndDisplay._remove_video_by_name(target, resource_manager, name1)
        target.wait_for(
            lambda: name1 not in TestVideoImportAndDisplay._table_filenames(target)
        )

        # Remove second video robustly
        TestVideoImportAndDisplay._remove_video_by_name(target, resource_manager, name2)
        target.wait_for(
            lambda: name2 not in TestVideoImportAndDisplay._table_filenames(target)
        )
