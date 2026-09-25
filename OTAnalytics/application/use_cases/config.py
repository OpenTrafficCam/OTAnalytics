from pathlib import Path

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.state import ConfigurationFile, CurrentKeyPrefix, FileState
from OTAnalytics.application.use_cases.get_current_remark import GetCurrentRemark


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class SaveOtconfig:
    def __init__(
        self,
        datastore: Datastore,
        config_parser: ConfigParser,
        state: FileState,
        get_current_remark: GetCurrentRemark,
        current_key_prefix: CurrentKeyPrefix,
    ) -> None:
        self._datastore = datastore
        self._config_parser = config_parser
        self._state = state
        self._get_current_remark = get_current_remark
        self._current_key_prefix = current_key_prefix

    def __call__(self, file: Path) -> None:
        project = self._datastore.project

        # Collect all validation errors
        errors = []
        if not project.name or not project.name.strip():
            errors.append("Project name is missing or empty")
        if not project.start_date:
            errors.append("Start date and time are missing or incomplete")

        if errors:
            raise ConfigValidationError(errors)

        video_files = self._datastore.get_all_videos()
        track_files = self._datastore._track_file_repository.get_all()
        sections = self._datastore.get_all_sections()
        flows = self._datastore.get_all_flows()
        remark = self._get_current_remark.get()
        # The same value reaches `convert` below. Passing it to only one of the
        # two would make every project report itself as permanently unsaved.
        s3_key_prefix = self._current_key_prefix.get()
        self._config_parser.serialize(
            project=project,
            video_files=video_files,
            track_files=track_files,
            sections=sections,
            flows=flows,
            file=file,
            remark=remark,
            s3_key_prefix=s3_key_prefix,
        )
        self._state.last_saved_config.set(
            ConfigurationFile(
                file,
                self._config_parser.convert(
                    project,
                    video_files,
                    track_files,
                    sections,
                    flows,
                    file,
                    remark,
                    s3_key_prefix,
                ),
            )
        )
