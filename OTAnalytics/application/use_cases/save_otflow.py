from pathlib import Path

from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.state import ConfigurationFile, FileState
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.application.use_cases.section_repository import GetAllSections


class SaveOtflow:
    def __init__(
        self,
        flow_parser: FlowParser,
        get_sections: GetAllSections,
        get_flows: GetAllFlows,
        state: FileState,
    ) -> None:
        self._parser = flow_parser
        self._get_sections = get_sections
        self._get_flows = get_flows
        self._state = state

    def save(self, file: Path) -> None:
        """
        Save the flows and sections from the repositories into a file.

        Notifies observers that an OTFlow file has been saved.

        Args:
            file (Path): file to save the flows and sections to.
        """
        if sections := self._get_sections():
            flows = self._get_flows.get()
            self._parser.serialize(
                sections=sections,
                flows=flows,
                file=file,
            )
            self._state.last_saved_config.set(ConfigurationFile(file))
        else:
            raise NoSectionsToSave()


class NoSectionsToSave(Exception):
    pass


class QuickSaveOtflow:
    def __init__(self, state: FileState, save_otflow: SaveOtflow) -> None:
        self._state = state
        self._save_otflow = save_otflow

    def save(self) -> None:
        if not (config := self._state.last_saved_config.get()):
            raise NoExistingFileToSave("No saved file to save otflow to")
        self._save_otflow.save(config.file)


class NoExistingFileToSave(Exception):
    pass
