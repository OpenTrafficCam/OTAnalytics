from pathlib import Path as _Path
from typing import Any

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    FileChooserDialogKeys,
    ProjectKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory
from tests.conftest import NiceGUITestServer

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


def _set_input_value(page: Page, selector: str, value: str) -> None:
    """Robustly set a value on an input and ensure NiceGUI backend receives it.

    Strategy:
    - Click, fill, press Enter to commit, and blur to trigger NiceGUI's value change.
    - Additionally set value via evaluate() and dispatch input/change as a fallback.
    """
    loc = page.locator(selector).first
    loc.wait_for(state="visible")
    try:
        loc.click()
    except Exception:
        pass
    try:
        loc.fill("")
        loc.fill(value)
        # Commit value like a user would
        try:
            loc.press("Enter")
        except Exception:
            pass
    except Exception:
        # ignore fill issues, fallback to JS below
        pass
    # Fallback: ensure events are dispatched and element is blurred
    loc.evaluate(
        "(el, v) => {\n"
        "  el.value = v;\n"
        "  el.dispatchEvent(new Event('input', { bubbles: true }));\n"
        "  el.dispatchEvent(new Event('change', { bubbles: true }));\n"
        "  if (el.blur) el.blur();\n"
        "}",
        value,
    )
    # Give the backend a short moment to process the websocket event
    page.wait_for_timeout(50)


class TestProjectInformationPlaywright:
    @pytest.mark.timeout(300)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_webserver_is_running_playwright(
        self, page: Page, external_app: NiceGUITestServer
    ) -> None:
        """Open the main page to confirm the server is reachable (Playwright)."""
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)
        # Sanity check: page should contain Project section (pick first occurrence)
        page.get_by_text("Project").first.wait_for(state="visible", timeout=5000)

    @pytest.mark.timeout(300)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_project_information_iso_format_playwright(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Verify project information form accepts ISO date format using Playwright."""
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        project_name = "Test Project - Leipzig Test Intersection - OTCamera19"
        date_value = "2023-05-24"
        time_value = "06:00:00"

        # Locate inputs via aria-labels
        name_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        date_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        time_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )

        _set_input_value(page, name_sel, project_name)
        _set_input_value(page, date_sel, date_value)
        _set_input_value(page, time_sel, time_value)

        # Assertions
        assert page.locator(name_sel).input_value() == project_name
        assert page.locator(date_sel).input_value() == date_value
        assert page.locator(time_sel).input_value() == time_value

    @pytest.mark.timeout(300)
    @pytest.mark.playwright
    @pytest.mark.xfail(
        reason=(
            "German date format not supported by date input; component expects ISO format"  # noqa
        )
    )
    @pytest.mark.usefixtures("external_app")
    def test_project_information_german_format_playwright(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Attempt to set German date format (expected to fail, mirrors Selenium test)."""  # noqa
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        project_name = "Test Project - Leipzig Test Intersection - OTCamera19"
        date_value = "24.05.2023"  # German format
        time_value = "06:00:00"

        name_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        date_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        time_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )

        _set_input_value(page, name_sel, project_name)
        _set_input_value(page, date_sel, date_value)
        _set_input_value(page, time_sel, time_value)

        assert page.locator(name_sel).input_value() == project_name
        # Expected to fail on the following assertion per xfail reason
        assert page.locator(date_sel).input_value() == date_value
        assert page.locator(time_sel).input_value() == time_value

    @pytest.mark.timeout(300)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_project_information_export_import_playwright(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        test_data_tmp_dir: _Path,
        monkeypatch: Any,
    ) -> None:
        """Playwright: export and import project information via patched file dialogs.

        Steps:
        - Save current project information to project_information.otconfig
        - Modify fields (simulate a new state)
        - Import previously saved otconfig and verify values restored
        - Modify fields again and re-import to verify overwrite
        """
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        name_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
        )
        date_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
        )
        time_sel = (
            f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
        )

        def fill(name: str, date_str: str, time_str: str) -> None:
            _set_input_value(page, name_sel, name)
            _set_input_value(page, date_sel, date_str)
            _set_input_value(page, time_sel, time_str)

        def read_values() -> tuple[str, str, str]:
            return (
                page.locator(name_sel).input_value(),
                page.locator(date_sel).input_value(),
                page.locator(time_sel).input_value(),
            )

        saved_name = "Acceptance Save/Load Project"
        saved_date = "2023-05-24"
        saved_time = "06:00:00"
        fill(saved_name, saved_date, saved_time)

        save_path = _Path(test_data_tmp_dir) / "project_information.otconfig"

        async def fake_ask_for_save_file_path(*args: object, **kwargs: object) -> _Path:
            return save_path

        async def fake_askopenfilename(*args: object, **kwargs: object) -> str:
            return str(save_path)

        # Patch NiceGuiUiFactory to bypass dialogs
        monkeypatch.setattr(
            NiceGuiUiFactory,
            "ask_for_save_file_path",
            fake_ask_for_save_file_path,
            raising=True,
        )
        monkeypatch.setattr(
            NiceGuiUiFactory, "askopenfilename", fake_askopenfilename, raising=True
        )

        # First save must use "Save As" (Quick Save requires an existing file)
        try:
            page.locator('[test-id="marker-project-save-as"]').first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(ProjectKeys.LABEL_SAVE_AS_PROJECT), exact=True
            ).click()

        # Wait for Apply button to ensure the dialog is open
        page.locator('[test-id="apply"]').first.wait_for(state="visible")
        dir_label = resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY)
        file_label = resource_manager.get(FileChooserDialogKeys.LABEL_FILENAME)
        page.get_by_label(dir_label, exact=True).fill(str(save_path.parent))
        page.get_by_label(file_label, exact=True).fill(save_path.name)
        # Apply the dialog
        page.locator('[test-id="apply"]').first.click()

        # Wait until file is created (async server write)
        for _ in range(200):  # up to ~10s
            if save_path.exists():
                break
            page.wait_for_timeout(50)
        assert save_path.exists(), f"Expected saved config at {save_path}"

        # Modify fields
        modified_name = "Different Project Name"
        modified_date = "2024-01-15"
        modified_time = "07:30:00"
        fill(modified_name, modified_date, modified_time)

        # Import previously saved config
        try:
            page.locator('[test-id="marker-project-open"]').first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT), exact=True
            ).click()

        # Interact with the FileChooserDialog to choose the saved file
        page.locator('[test-id="apply"]').first.wait_for(state="visible")
        dir_label = resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY)
        file_label = resource_manager.get(FileChooserDialogKeys.LABEL_FILENAME)
        page.get_by_label(dir_label, exact=True).fill(str(save_path.parent))
        page.get_by_label(file_label, exact=True).fill(save_path.name)
        page.locator('[test-id="apply"]').first.click()

        # Wait for values to change back
        page.wait_for_timeout(150)
        name_v, date_v, time_v = read_values()
        # Retry a few times in case of async update
        for _ in range(120):
            if (name_v, date_v, time_v) == (saved_name, saved_date, saved_time):
                break
            page.wait_for_timeout(50)
            name_v, date_v, time_v = read_values()
        assert (name_v, date_v, time_v) == (saved_name, saved_date, saved_time)

        # Overwrite scenario: change and re-import
        fill("Temp Name Before Import", "2025-08-13", "08:45:00")
        try:
            page.locator('[test-id="marker-project-open"]').first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT), exact=True
            ).click()
        page.locator('[test-id="apply"]').first.wait_for(state="visible")
        page.get_by_label(dir_label, exact=True).fill(str(save_path.parent))
        page.get_by_label(file_label, exact=True).fill(save_path.name)
        page.locator('[test-id="apply"]').first.click()

        for _ in range(120):
            name_v, date_v, time_v = read_values()
            if (name_v, date_v, time_v) == (saved_name, saved_date, saved_time):
                break
            page.wait_for_timeout(50)
        assert (name_v, date_v, time_v) == (saved_name, saved_date, saved_time)
