from pathlib import Path
from typing import TypedDict
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.datastore import FlowParser
from OTAnalytics.application.use_cases.event_repository import ClearAllEvents
from OTAnalytics.application.use_cases.flow_repository import (
    AddFlow,
    ClearFlows,
    FlowAlreadyExists,
)
from OTAnalytics.application.use_cases.load_otflow import (
    LoadOtflow,
    UnableToLoadFlowFile,
)
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    ClearSections,
    SectionAlreadyExists,
)
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section


class MockDependencies(TypedDict):
    clear_sections: Mock
    clear_flows: Mock
    clear_all_events: Mock
    flow_parser: Mock
    add_section: Mock
    add_flow: Mock


class TestLoadOtflow:
    @pytest.fixture
    def mock_first_section(self) -> Mock:
        return Mock(spec=Section)

    @pytest.fixture
    def mock_second_section(self) -> Mock:
        return Mock(spec=Section)

    @pytest.fixture
    def mock_flow(self) -> Mock:
        return Mock(spec=Flow)

    @pytest.fixture
    def mock_deps(
        self, mock_first_section: Mock, mock_second_section: Mock, mock_flow: Mock
    ) -> MockDependencies:
        clear_sections = Mock(spec=ClearSections)
        clear_flows = Mock(spec=ClearFlows)
        clear_all_events = Mock(spec=ClearAllEvents)

        flow_parser = Mock(spec=FlowParser)
        flow_parser.parse.return_value = (
            [mock_first_section, mock_second_section],
            [mock_flow],
        )

        add_section = Mock(spec=AddSection)
        add_flow = Mock(spec=AddFlow)
        return {
            "clear_sections": clear_sections,
            "clear_flows": clear_flows,
            "clear_all_events": clear_all_events,
            "flow_parser": flow_parser,
            "add_section": add_section,
            "add_flow": add_flow,
        }

    def test_load_flow_file(
        self,
        mock_deps: MockDependencies,
        mock_first_section: Mock,
        mock_second_section: Mock,
        mock_flow: Mock,
    ) -> None:
        load_flow_file = LoadOtflow(**mock_deps)

        otflow_file = Mock(spec=Path)
        load_flow_file(otflow_file)

        mock_deps["flow_parser"].parse.assert_called_once_with(otflow_file)
        assert mock_deps["add_section"].call_args_list == [
            call(mock_first_section),
            call(mock_second_section),
        ]
        assert mock_deps["add_flow"].call_args_list == [call(mock_flow)]
        mock_deps["clear_all_events"].assert_called_once()
        mock_deps["clear_flows"].assert_called_once()
        mock_deps["clear_sections"].assert_called_once()

    def test_load_flow_file_invalid_section_file(
        self, mock_deps: MockDependencies, mock_first_section: Mock
    ) -> None:
        mock_deps["add_section"].side_effect = SectionAlreadyExists
        load_flow_file = LoadOtflow(**mock_deps)
        otflow_file = Mock(spec=Path)

        with pytest.raises((SectionAlreadyExists, UnableToLoadFlowFile)):
            load_flow_file(otflow_file)

        mock_deps["add_section"].assert_called_once_with(mock_first_section)
        mock_deps["add_flow"].assert_not_called()
        assert mock_deps["clear_sections"].call_count == 2
        assert mock_deps["clear_flows"].call_count == 2
        assert mock_deps["clear_all_events"].call_count == 2

    def test_load_flow_file_invalid_flow_file(
        self,
        mock_deps: MockDependencies,
        mock_first_section: Mock,
        mock_second_section: Mock,
        mock_flow: Mock,
    ) -> None:
        mock_deps["add_flow"].side_effect = FlowAlreadyExists
        load_flow_file = LoadOtflow(**mock_deps)
        otflow_file = Mock(spec=Path)

        with pytest.raises((FlowAlreadyExists, UnableToLoadFlowFile)):
            load_flow_file(otflow_file)

        assert mock_deps["add_section"].call_args_list == [
            call(mock_first_section),
            call(mock_second_section),
        ]
        mock_deps["add_flow"].assert_called_once_with(mock_flow)
        assert mock_deps["clear_sections"].call_count == 2
        assert mock_deps["clear_flows"].call_count == 2
        assert mock_deps["clear_all_events"].call_count == 2
