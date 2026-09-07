"""Tests for the wiring of the command line application."""

from unittest.mock import Mock

from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.plugin_cli.cli_application import OtAnalyticsCliApplicationStarter
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder


class TestOtAnalyticsCliApplicationStarter:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    def test_keeps_writing_progress_to_the_console(self) -> None:
        target = OtAnalyticsCliApplicationStarter(Mock(spec=RunConfiguration))

        assert isinstance(target.progressbar_builder, TqdmBuilder)
