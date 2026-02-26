from pathlib import Path as _Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    MARKER_PROJECT_NAME,
    MARKER_START_DATE,
    MARKER_START_TIME,
)
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_FINAL_TIMEOUT_MS,
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    PLAYWRIGHT_POLL_INTERVAL_MS,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    fill_project_information,
    import_project_and_assert_values,
    open_project_otconfig,
    save_project_otconfig,
    search_for_marker_element,
)


# Small helper to assert the tuple of project values
def assert_project_info_equals(
    actual: tuple[str, str, str], expected: tuple[str, str, str]
) -> None:
    assert actual == expected


# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


class TestProjectInformationPlaywright:
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_webserver_is_running_playwright(
        self, page: Page, external_app: NiceGUITestServer
    ) -> None:
        """Open the main page to confirm the server is reachable (Playwright)."""
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)
        # Sanity check: page should contain Project section (pick first occurrence)
        page.get_by_text("Project").first.wait_for(
            state="visible", timeout=ACCEPTANCE_TEST_FINAL_TIMEOUT_MS
        )

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
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

        # Fill using shared helper, then verify via test-id markers
        fill_project_information(
            page,
            resource_manager,
            name=project_name,
            date_value=date_value,
            time_value=time_value,
        )

        # Assertions
        assert (
            search_for_marker_element(page, MARKER_PROJECT_NAME).input_value()
            == project_name
        )
        assert (
            search_for_marker_element(page, MARKER_START_DATE).input_value()
            == date_value
        )
        assert (
            search_for_marker_element(page, MARKER_START_TIME).input_value()
            == time_value
        )

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
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

        # Fill using shared helper (expected to fail due to invalid date format)
        fill_project_information(
            page,
            resource_manager,
            name=project_name,
            date_value=date_value,
            time_value=time_value,
        )

        assert (
            search_for_marker_element(page, MARKER_PROJECT_NAME).input_value()
            == project_name
        )
        # Expected to fail on the following assertion per xfail reason
        assert (
            search_for_marker_element(page, MARKER_START_DATE).input_value()
            == date_value
        )
        assert (
            search_for_marker_element(page, MARKER_START_TIME).input_value()
            == time_value
        )

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_project_information_export_import_playwright(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        test_data_tmp_dir: _Path,
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

        saved_name = "Acceptance Save/Load Project"
        saved_date = "2023-05-24"
        saved_time = "06:00:00"
        fill_project_information(
            page,
            resource_manager,
            name=saved_name,
            date_value=saved_date,
            time_value=saved_time,
        )

        # Use a simple filename as requested by the issue (test_name)
        save_path = _Path(test_data_tmp_dir) / "test_name.otconfig"

        # Save using shared helper to interact with the file dialog
        save_project_otconfig(page, resource_manager, save_path)

        while True:
            if save_path.exists():
                break
            page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
        assert save_path.exists(), f"Expected saved config at {save_path}"

        # Modify fields
        modified_name = "Different Project Name"
        modified_date = "2024-01-15"
        modified_time = "07:30:00"
        fill_project_information(
            page,
            resource_manager,
            name=modified_name,
            date_value=modified_date,
            time_value=modified_time,
        )

        # Import previously saved config (use shared helper)
        open_project_otconfig(page, resource_manager, save_path)

        # Wait and verify imported values via shared helper
        import_project_and_assert_values(
            page,
            resource_manager,
            save_path,
            (saved_name, saved_date, saved_time),
        )

        # Overwrite scenario: change and re-import
        fill_project_information(
            page,
            resource_manager,
            name="Temp Name Before Import",
            date_value="2025-08-13",
            time_value="08:45:00",
        )
        open_project_otconfig(page, resource_manager, save_path)

        import_project_and_assert_values(
            page,
            resource_manager,
            save_path,
            (saved_name, saved_date, saved_time),
        )
