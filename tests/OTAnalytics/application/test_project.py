from datetime import datetime

from OTAnalytics.application.project import METADATA, NAME, START_DATE, Project


class TestProject:
    def test_to_dict(self) -> None:
        name = "some"
        timestamp = 12345678
        metadata = {"metadata": "svz"}
        project = Project(
            name=name, start_date=datetime.fromtimestamp(timestamp), metadata=metadata
        )

        result = project.to_dict()

        assert result == {NAME: name, START_DATE: timestamp, METADATA: metadata}
