"""Tests that each user interface gets the progressbar it can actually show."""

from unittest.mock import Mock

from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.plugin_cli.cli_application import OtAnalyticsCliApplicationStarter
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from OTAnalytics.plugin_ui.nicegui_application import (
    OtAnalyticsNiceGuiApplicationStarter,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.progressbar import (
    NiceguiProgressbarBuilder,
)


class TestProgressbarWiring:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    def test_webui_shows_progress_in_the_browser(self) -> None:
        target = OtAnalyticsNiceGuiApplicationStarter(Mock(spec=RunConfiguration))

        assert isinstance(target.progressbar_builder, NiceguiProgressbarBuilder)

    def test_cli_keeps_writing_progress_to_the_console(self) -> None:
        target = OtAnalyticsCliApplicationStarter(Mock(spec=RunConfiguration))

        assert isinstance(target.progressbar_builder, TqdmBuilder)
