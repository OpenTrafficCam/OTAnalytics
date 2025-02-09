from pathlib import Path

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.state import ConfigurationFile, FileState
from OTAnalytics.application.use_cases.get_current_remark import GetCurrentRemark


class MissingDate(Exception):
    pass


class SaveOtconfig:
    def __init__(
        self,
        datastore: Datastore,
        config_parser: ConfigParser,
        state: FileState,
        get_current_remark: GetCurrentRemark,
    ) -> None:
        self._datastore = datastore
        self._config_parser = config_parser
        self._state = state
        self._get_current_remark = get_current_remark

    def __call__(self, file: Path) -> None:
        if self._datastore.project.start_date:
            project = self._datastore.project
            video_files = self._datastore.get_all_videos()
            track_files = self._datastore._track_file_repository.get_all()
            sections = self._datastore.get_all_sections()
            flows = self._datastore.get_all_flows()
            remark = self._get_current_remark.get()
            self._config_parser.serialize(
                project=project,
                video_files=video_files,
                track_files=track_files,
                sections=sections,
                flows=flows,
                file=file,
                remark=remark,
            )
            self._state.last_saved_config.set(
                ConfigurationFile(
                    file,
                    self._config_parser.convert(
                        project, video_files, track_files, sections, flows, file, remark
                    ),
                )
            )
        else:
            raise MissingDate()
