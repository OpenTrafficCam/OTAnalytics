from unittest.mock import Mock, call

from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.update_project import ProjectUpdater


class TestResetProjectConfig:
    def test_reset(self) -> None:
        update_project = Mock(spec=ProjectUpdater)
        reset_project_config = ResetProjectConfig(update_project)
        reset_project_config()
        assert update_project.call_args_list == [call("", None, None)]
