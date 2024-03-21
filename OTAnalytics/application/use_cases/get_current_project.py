from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import Project


class GetCurrentProject:
    def __init__(self, datastore: Datastore):
        self._datastore = datastore

    def get(self) -> Project:
        return self._datastore.project
