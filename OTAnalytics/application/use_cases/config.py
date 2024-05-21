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
            project = self._datastore.project
            video_files = self._datastore.get_all_videos()
            track_files = self._datastore._track_file_repository.get_all()
            sections = self._datastore.get_all_sections()
            flows = self._datastore.get_all_flows()

            self._config_parser.serialize(
                project=project,
                video_files=video_files,
                track_files=track_files,
                sections=sections,
                flows=flows,
                file=file,
            )
            self._state.last_saved_config.set(
                ConfigurationFile(
                    file,
                    self._config_parser.convert(
                        project, video_files, track_files, sections, flows, file
                    ),
                )
            )
        else:
            raise MissingDate()
