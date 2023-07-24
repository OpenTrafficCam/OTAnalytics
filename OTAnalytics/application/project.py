from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from application.datastore import Datastore

NAME: str = "name"
START_DATE: str = "start_date"


class StartDateMissing(Exception):
    pass


@dataclass
class Project:
    name: str
    start_date: Optional[datetime]

    def to_dict(self) -> dict:
        if self.start_date:
            return {
                NAME: self.name,
                START_DATE: self.start_date.timestamp(),
            }
        raise StartDateMissing()


class ProjectUpdater:
    """Use case to update the project information."""

    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore

    def __call__(self, name: str, start_date: Optional[datetime]) -> Any:
        self._datastore.project = Project(name=name, start_date=start_date)
