from datetime import datetime
from typing import Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import Project
from OTAnalytics.domain.observer import OBSERVER, Subject


class ProjectUpdater:
    """Use case to update the project information."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore
        self._subject = Subject[Project]()

    def __call__(self, name: str, start_date: Optional[datetime]) -> None:
        project = Project(name=name, start_date=start_date)
        self._datastore.project = project
        self._subject.notify(project)

    def update_name(self, name: str) -> None:
        old_project = self._datastore.project
        new_project = Project(name, old_project.start_date)
        self._datastore.project = new_project
        self._subject.notify(new_project)

    def update_start_date(self, start_date: Optional[datetime]) -> None:
        old_project = self._datastore.project
        new_project = Project(old_project.name, start_date)
        self._datastore.project = new_project
        self._subject.notify(new_project)

    def register(self, observer: OBSERVER[Project]) -> None:
        self._subject.register(observer)
