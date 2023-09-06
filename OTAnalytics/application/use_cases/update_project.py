from datetime import datetime
from typing import Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import Project


class ProjectUpdater:
    """Use case to update the project information."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore

    def __call__(self, name: str, start_date: Optional[datetime]) -> None:
        self._datastore.project = Project(name=name, start_date=start_date)

    def update_name(self, name: str) -> None:
        old_project = self._datastore.project
        self._datastore.project = Project(name, old_project.start_date)

    def update_start_date(self, start_date: Optional[datetime]) -> None:
        old_project = self._datastore.project
        self._datastore.project = Project(old_project.name, start_date)
