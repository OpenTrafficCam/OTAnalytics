from datetime import datetime

import pytest

from OTAnalytics.application.project import NAME, START_DATE, Project, StartDateMissing


class TestProject:
    def test_to_dict(self) -> None:
        timestamp = 12345678
        project = Project(name="some", start_date=datetime.fromtimestamp(timestamp))

        result = project.to_dict()

        assert result == {NAME: "some", START_DATE: timestamp}

    def test_to_dict_missing_start_date(self) -> None:
        project = Project(name="some", start_date=None)

        with pytest.raises(StartDateMissing):
            project.to_dict()
