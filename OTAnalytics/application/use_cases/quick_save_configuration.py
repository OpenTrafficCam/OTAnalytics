from OTAnalytics.application.state import FileState
from OTAnalytics.application.use_cases.config import SaveOtconfig
from OTAnalytics.application.use_cases.save_otflow import SaveOtflow


class QuickSaveConfiguration:
    def __init__(
        self,
        state: FileState,
        save_otflow: SaveOtflow,
        save_otconfig: SaveOtconfig,
    ) -> None:
        self._state = state
        self._save_otflow = save_otflow
        self._save_otconfig = save_otconfig

    def save(self) -> None:
        if not (config := self._state.last_saved_config.get()):
            raise NoExistingFileToSave("No saved file to save configuration to")

        if config.is_otflow:
            self._save_otflow.save(config.file)
        elif config.is_otconfig:
            self._save_otconfig(config.file)
        else:
            raise UnsupportedConfiguration(
                "Unable to save configuration. "
                f"Unsupported configuration format '{config.file_type}'"
            )


class UnsupportedConfiguration(Exception):
    pass


class NoExistingFileToSave(Exception):
    pass
