from pathlib import Path

from OTAnalytics.application.datastore import FlowParser
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.application.use_cases.section_repository import GetAllSections


class SaveOTFlow:
    def __init__(
        self,
        flow_parser: FlowParser,
        get_sections: GetAllSections,
        get_flows: GetAllFlows,
    ) -> None:
        self._parser = flow_parser
        self._get_sections = get_sections
        self._get_flows = get_flows

    def save(self, file: Path) -> None:
        """
        Save the flows and sections from the repositories into a file.

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
        else:
            raise NoSectionsToSave()


class NoSectionsToSave(Exception):
    pass
