from pathlib import Path
from typing import Iterable

from OTAnalytics.application.parser.deserializer import Deserializer
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.event_repository import ClearAllEvents
from OTAnalytics.application.use_cases.flow_repository import (
    AddFlow,
    ClearAllFlows,
    FlowAlreadyExists,
)
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    ClearAllSections,
    SectionAlreadyExists,
)
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.section import Section


class UnableToLoadFlowFile(Exception):
    pass


class LoadOtflow:
    """
    Load sections and flows from the given files and store them in the repositories.

    Args:
        clear_all_sections (ClearAllSections): use case to clear section repository.
        clear_all_flows (ClearAllFlows): use case to clear flow repository.
        clear_all_events (ClearAllEvents): use case to clear event repository.
        flow_parser (FlowParser): to parse sections and flows from file.
        add_section (AddSection): use case to add sections to section repository.
        add_flow (AddFlow): use case to add flows to flow repository.
    """

    def __init__(
        self,
        clear_all_sections: ClearAllSections,
        clear_all_flows: ClearAllFlows,
        clear_all_events: ClearAllEvents,
        flow_parser: FlowParser,
        add_section: AddSection,
        add_flow: AddFlow,
        deserialize: Deserializer,
    ) -> None:
        self._clear_all_sections = clear_all_sections
        self._clear_all_flows = clear_all_flows
        self._clear_all_events = clear_all_events
        self._flow_parser = flow_parser
        self._add_section = add_section
        self._add_flow = add_flow
        self._deserialize = deserialize
        self._subject = Subject[ConfigurationFile]()

    def __call__(self, file: Path) -> None:
        """
        Load sections and flows from the given files and store them in the repositories.

        Args:
            file (Path): file to load sections and flows from.
        """
        self._clear_repositories()

        sections, flows = self._flow_parser.parse(file)
        try:
            self._add_sections(sections)
            self._add_flows(flows)
            self._subject.notify(ConfigurationFile(file, self._deserialize(file)))

        except (SectionAlreadyExists, FlowAlreadyExists) as cause:
            self._clear_repositories()
            raise UnableToLoadFlowFile(
                "Error while loading otflow file. Abort loading!"
            ) from cause

    def _clear_repositories(self) -> None:
        self._clear_all_events()
        self._clear_all_sections()
        self._clear_all_flows()

    def _add_sections(self, sections: Iterable[Section]) -> None:
        for section in sections:
            self._add_section(section)

    def _add_flows(self, flows: Iterable[Flow]) -> None:
        for flow in flows:
            self._add_flow(flow)

    def register(self, observer: OBSERVER[ConfigurationFile]) -> None:
        self._subject.register(observer)
