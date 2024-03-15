from datetime import datetime

from OTAnalytics.application.project import NAME, START_DATE, Project


class TestProject:
    def test_to_dict(self) -> None:
        timestamp = 12345678
        project = Project(name="some", start_date=datetime.fromtimestamp(timestamp))

        result = project.to_dict()

        assert result == {NAME: "some", START_DATE: timestamp}
