from pathlib import Path

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.state import ConfigurationFile, FileState


class MissingDate(Exception):
    pass


class SaveOtconfig:
    def __init__(
        self,
        datastore: Datastore,
        config_parser: ConfigParser,
        state: FileState,
    ) -> None:
        self._datastore = datastore
        self._config_parser = config_parser
        self._state = state

    def __call__(self, file: Path) -> None:
        if self._datastore.project.start_date:
            self._config_parser.serialize(
                project=self._datastore.project,
                video_files=self._datastore.get_all_videos(),
                sections=self._datastore.get_all_sections(),
                flows=self._datastore.get_all_flows(),
                file=file,
            )
            self._state.last_saved_config.set(ConfigurationFile(file))
        else:
            raise MissingDate()
