from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.generate_flows import (
    CrossProductFlowGenerator,
    FlowGenerator,
    FlowIdGenerator,
    FlowNameGenerator,
    GenerateFlows,
)
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionRepository


def create_test_cases() -> list[tuple[list[Section], list[Flow]]]:
    south_section_id = SectionId("south")
    south_section = Mock(spec=Section)
    south_section.id = south_section_id
    north_section_id = SectionId("north")
    north_section = Mock(spec=Section)
    north_section.id = north_section_id
    south_to_south_id = FlowId("1")
    south_to_south = Flow(
        south_to_south_id,
        name="south to south",
        start=south_section_id,
        end=south_section_id,
        distance=0,
    )
    south_to_north_id = FlowId("2")
    south_to_north = Flow(
        south_to_north_id,
        name="south to north",
        start=south_section_id,
        end=north_section_id,
        distance=0,
    )
    north_to_south_id = FlowId("3")
    north_to_south = Flow(
        north_to_south_id,
        name="north to south",
        start=north_section_id,
        end=south_section_id,
        distance=0,
    )
    north_to_north_id = FlowId("4")
    north_to_north = Flow(
        north_to_north_id,
        name="north to north",
        start=north_section_id,
        end=north_section_id,
        distance=0,
    )
    no_sections_sections: list[Section] = []
    no_sections_flows: list[Flow] = []
    no_sections_result = (no_sections_sections, no_sections_flows)
    single_section_sections: list[Section] = [south_section]
    single_section_result = (single_section_sections, [south_to_south])
    multiple_sections_sections: list[Section] = [south_section, north_section]
    multiple_sections_flows: list[Flow] = [
        south_to_south,
        south_to_north,
        north_to_south,
        north_to_north,
    ]
    multiple_sections_result = (multiple_sections_sections, multiple_sections_flows)
    return [no_sections_result, single_section_result, multiple_sections_result]


class TestCrossProductFlowGenerator:
    @pytest.mark.parametrize("sections,expected_flows", create_test_cases())
    def test_generate_crossproduct(
        self, sections: list[Section], expected_flows: list[Flow]
    ) -> None:
        id_generator = Mock(spec=FlowIdGenerator)
        id_generator.generate_id.side_effect = [flow.id for flow in expected_flows]
        name_generator = Mock(spec=FlowNameGenerator)
        name_generator.generate_name.return_value = "name"
        generator = CrossProductFlowGenerator(id_generator, name_generator)

        flows = generator.generate(sections)

        assert all(
            (current.start == expected.start) and (current.end == expected.end)
            for current, expected in zip(flows, expected_flows)
        )

        assert id_generator.generate_id.call_args_list == [
            call(flow.start, flow.end) for flow in expected_flows
        ]
        assert name_generator.generate_name.call_args_list == [
            call(flow.start, flow.end) for flow in expected_flows
        ]


class TestGenerateFlows:
    def test_generate_all_flows(self) -> None:
        sections: list[Section] = []
        created_flows: list[Flow] = []
        section_repository = Mock(spec=SectionRepository)
        section_repository.get_all.return_value = sections
        flow_generator = Mock(spec=FlowGenerator)
        flow_generator.generate.return_value = created_flows
        flow_repository = Mock(spec=FlowRepository)
        generator = GenerateFlows(section_repository, flow_repository, flow_generator)

        generator.generate()

        section_repository.get_all.assert_called_once()
        flow_generator.generate.assert_called_with(sections)
        flow_repository.add_all.assert_called_with(created_flows)
