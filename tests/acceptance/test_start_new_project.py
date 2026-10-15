import shutil
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY,
    MARKER_CANCEL,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    MARKER_PROJECT_NEW,
)
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_FINAL_TIMEOUT_MS,
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    import_project_and_assert_values,
    load_main_page,
    read_project_info_values,
    search_for_marker_element,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

PROJECT = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00"
LOADED_PROJECT = ("My Test Project", "2020-01-01", "11:11:17")
NEW_PROJECT = ("", "", "")
A_SECTION = "Süd"


@pytest.fixture
def otconfig(test_data_dir: Path, test_data_tmp_dir: Path) -> Path:
    for suffix in [".otconfig", ".ottrk", ".mp4"]:
        shutil.copy(test_data_dir / f"{PROJECT}{suffix}", test_data_tmp_dir)
    return test_data_tmp_dir / f"{PROJECT}.otconfig"


class TestStartNewProject:
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_new_project_clears_the_loaded_project(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        otconfig: Path,
    ) -> None:
        load_main_page(page, external_app)
        import_project_and_assert_values(
            page, resource_manager, otconfig, LOADED_PROJECT
        )
        expect(page.get_by_text(A_SECTION).first).to_be_visible()

        search_for_marker_element(page, MARKER_PROJECT_NEW).first.click()
        search_for_marker_element(page, MARKER_APPLY).first.click()

        expect(page.get_by_text(A_SECTION)).to_have_count(
            0, timeout=ACCEPTANCE_TEST_FINAL_TIMEOUT_MS
        )
        assert read_project_info_values(page) == NEW_PROJECT

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_cancelling_keeps_the_loaded_project(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        otconfig: Path,
    ) -> None:
        load_main_page(page, external_app)
        import_project_and_assert_values(
            page, resource_manager, otconfig, LOADED_PROJECT
        )

        search_for_marker_element(page, MARKER_PROJECT_NEW).first.click()
        search_for_marker_element(page, MARKER_CANCEL).first.click()

        expect(page.get_by_text(A_SECTION).first).to_be_visible()
        assert read_project_info_values(page) == LOADED_PROJECT
