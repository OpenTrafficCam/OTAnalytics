"""Tests that a file named on the command line cannot stop the server starting.

The web UI preloads `--config` while the webserver is still being constructed,
so anything the load raises propagates out of startup and the process dies
before it binds a port. The user is then left with a traceback and no
application, for a file they could simply have opened again by hand.

#Requirement https://openproject.platomo.de/wp/10325
"""

from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.plugin_ui.nicegui_application import (
    OtAnalyticsNiceGuiApplicationStarter,
)


@dataclass
class Given:
    run_config: Mock
    preload_input_files: Mock


def create_given(load_error: Exception | None = None) -> Given:
    preload_input_files = Mock()
    if load_error is not None:
        preload_input_files.load.side_effect = load_error
    return Given(run_config=Mock(), preload_input_files=preload_input_files)


def create_target(given: Given) -> OtAnalyticsNiceGuiApplicationStarter:
    target = OtAnalyticsNiceGuiApplicationStarter(given.run_config)
    # The starter builds its own collaborators through cached_property, so
    # seeding the cache is how one of them is substituted.
    target.__dict__["preload_input_files"] = given.preload_input_files
    return target


class TestPreloadingTheProject:
    def test_loads_the_files_named_on_the_command_line(self) -> None:
        """
        #Requirement https://openproject.platomo.de/wp/10325
        """
        given = create_given()

        create_target(given).preload_project()

        given.preload_input_files.load.assert_called_once_with(given.run_config)

    def test_a_file_that_cannot_be_loaded_does_not_stop_the_server(self) -> None:
        """
        #Requirement https://openproject.platomo.de/wp/10325

        @bug by randy-seng
        """
        given = create_given(load_error=FileNotFoundError("no such otconfig"))

        create_target(given).preload_project()

    def test_survives_a_failure_of_any_kind(self) -> None:
        """Deliberately broad: the point is that startup continues, and every
        exception type reaching here has already cost the user their server
        once.

        #Requirement https://openproject.platomo.de/wp/10325

        @bug by randy-seng
        """
        given = create_given(load_error=RuntimeError("anything at all"))

        create_target(given).preload_project()
