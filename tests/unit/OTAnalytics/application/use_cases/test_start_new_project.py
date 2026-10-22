from unittest.mock import Mock, call

from OTAnalytics.application.use_cases.reset_application import ResetApplication
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.start_new_project import StartNewProject


class TestStartNewProject:
    def test_start_new_project(self) -> None:
        reset_application = Mock(spec=ResetApplication)
        reset_project_config = Mock(spec=ResetProjectConfig)
        order = Mock()
        order.attach_mock(reset_application.reset, "reset_application")
        order.attach_mock(reset_project_config, "reset_project_config")

        StartNewProject(reset_application, reset_project_config)()

        assert order.mock_calls == [
            call.reset_application(),
            call.reset_project_config(),
        ]
