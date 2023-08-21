from datetime import datetime
from typing import Any, Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import Project


class ProjectUpdater:
    """Use case to update the project information."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore

    def __call__(self, name: str, start_date: Optional[datetime]) -> Any:
        self._datastore.project = Project(name=name, start_date=start_date)
