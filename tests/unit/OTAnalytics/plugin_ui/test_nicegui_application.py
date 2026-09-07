"""Tests for the wiring of the NiceGUI application."""

from unittest.mock import Mock

from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.plugin_ui.nicegui_application import (
    OtAnalyticsNiceGuiApplicationStarter,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.progressbar import (
    NiceguiProgressbarBuilder,
)


class TestOtAnalyticsNiceGuiApplicationStarter:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    def test_shows_progress_in_the_browser(self) -> None:
        target = OtAnalyticsNiceGuiApplicationStarter(Mock(spec=RunConfiguration))

        assert isinstance(target.progressbar_builder, NiceguiProgressbarBuilder)
