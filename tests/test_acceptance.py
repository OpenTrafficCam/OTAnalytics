import multiprocessing

import pytest
from conftest import YieldFixture
from nicegui.testing import Screen
from selenium import webdriver
from utils.builders.otanalytics_builders import (
    MultiprocessingWorker,
    NiceguiOtanalyticsBuilder,
)

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_application import Webserver
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE


@pytest.fixture
def chrome_options() -> webdriver.ChromeOptions:
    """Create Chrome options for Selenium testing.

    This fixture creates a ChromeOptions instance that can be used by the
    nicegui_chrome_options fixture for Selenium testing.

    Returns:
        webdriver.ChromeOptions: Chrome options for Selenium testing.
    """
    options = webdriver.ChromeOptions()
    return options


@pytest.fixture(scope="session")
def given_builder() -> NiceguiOtanalyticsBuilder:
    return NiceguiOtanalyticsBuilder()


@pytest.fixture(scope="session")
def given_app(
    given_builder: NiceguiOtanalyticsBuilder,
) -> YieldFixture[MultiprocessingWorker]:
    multiprocessing.set_start_method("fork", force=True)
    app = given_builder.build()
    yield app
    app.stop()


@pytest.fixture(scope="session")
def given_webserver(given_builder: NiceguiOtanalyticsBuilder) -> Webserver:
    return given_builder.webserver


@pytest.fixture
async def target(screen: Screen, given_webserver: Webserver) -> Screen:
    given_webserver.build_pages()
    return screen


@pytest.fixture
def resource_manager() -> ResourceManager:
    return ResourceManager()


class TestProjectInformation:
    @pytest.mark.timeout(300)
    @pytest.mark.asyncio
    async def test_webserver_is_running(
        self,
        target: Screen,
        given_app: MultiprocessingWorker,
        resource_manager: ResourceManager,
    ) -> None:
        given_app.start()
        target.open(ENDPOINT_MAIN_PAGE)
        target.shot("dummy")
