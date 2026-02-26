from pathlib import Path
from typing import TypedDict
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.event_repository import ClearAllEvents
from OTAnalytics.application.use_cases.flow_repository import (
    AddFlow,
    ClearAllFlows,
    FlowAlreadyExists,
)
from OTAnalytics.application.use_cases.load_otflow import (
    LoadOtflow,
    UnableToLoadFlowFile,
)
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    ClearAllSections,
    SectionAlreadyExists,
)
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section


class MockDependencies(TypedDict):
    clear_all_sections: Mock
    clear_all_flows: Mock
    clear_all_events: Mock
    flow_parser: Mock
    add_section: Mock
    add_flow: Mock
    deserialize: Mock


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
        clear_all_sections = Mock(spec=ClearAllSections)
        clear_all_flows = Mock(spec=ClearAllFlows)
        clear_all_events = Mock(spec=ClearAllEvents)

        flow_parser = Mock(spec=FlowParser)
        flow_parser.parse.return_value = (
            [mock_first_section, mock_second_section],
            [mock_flow],
        )

        add_section = Mock(spec=AddSection)
        add_flow = Mock(spec=AddFlow)
        deserializer = Mock()
        return {
            "clear_all_sections": clear_all_sections,
            "clear_all_flows": clear_all_flows,
            "clear_all_events": clear_all_events,
            "flow_parser": flow_parser,
            "add_section": add_section,
            "add_flow": add_flow,
            "deserialize": deserializer,
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
        observer = Mock()
        load_flow_file.register(observer)
        deserialization_result = Mock()
        mock_deps["deserialize"].return_value = deserialization_result

        load_flow_file(otflow_file)
        mock_deps["flow_parser"].parse.assert_called_once_with(otflow_file)
        assert mock_deps["add_section"].call_args_list == [
            call(mock_first_section),
            call(mock_second_section),
        ]
        assert mock_deps["add_flow"].call_args_list == [call(mock_flow)]
        mock_deps["clear_all_events"].assert_called_once()
        mock_deps["clear_all_flows"].assert_called_once()
        mock_deps["clear_all_sections"].assert_called_once()
        observer.assert_called_with(
            ConfigurationFile(otflow_file, deserialization_result)
        )

    def test_load_flow_file_invalid_section_file(
        self, mock_deps: MockDependencies, mock_first_section: Mock
    ) -> None:
        mock_deps["add_section"].side_effect = SectionAlreadyExists
        load_flow_file = LoadOtflow(**mock_deps)
        observer = Mock()
        load_flow_file.register(observer)
        otflow_file = Mock(spec=Path)

        with pytest.raises((SectionAlreadyExists, UnableToLoadFlowFile)):
            load_flow_file(otflow_file)

        mock_deps["add_section"].assert_called_once_with(mock_first_section)
        mock_deps["add_flow"].assert_not_called()
        assert mock_deps["clear_all_sections"].call_count == 2
        assert mock_deps["clear_all_flows"].call_count == 2
        assert mock_deps["clear_all_events"].call_count == 2
        observer.assert_not_called()

    def test_load_flow_file_invalid_flow_file(
        self,
        mock_deps: MockDependencies,
        mock_first_section: Mock,
        mock_second_section: Mock,
        mock_flow: Mock,
    ) -> None:
        mock_deps["add_flow"].side_effect = FlowAlreadyExists
        load_flow_file = LoadOtflow(**mock_deps)
        observer = Mock()
        load_flow_file.register(observer)
        otflow_file = Mock(spec=Path)

        with pytest.raises((FlowAlreadyExists, UnableToLoadFlowFile)):
            load_flow_file(otflow_file)

        assert mock_deps["add_section"].call_args_list == [
            call(mock_first_section),
            call(mock_second_section),
        ]
        mock_deps["add_flow"].assert_called_once_with(mock_flow)
        assert mock_deps["clear_all_sections"].call_count == 2
        assert mock_deps["clear_all_flows"].call_count == 2
        assert mock_deps["clear_all_events"].call_count == 2
        observer.assert_not_called()
