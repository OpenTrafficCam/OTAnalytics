from unittest.mock import Mock

from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject


class TestGetCurrentProject:
    def test_get(self) -> None:
        expected_project = Mock()
        datastore = Mock()
        datastore.project = expected_project
        get_current = GetCurrentProject(datastore)
        actual_project = get_current.get()
        assert actual_project == expected_project
