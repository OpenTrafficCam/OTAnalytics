from itertools import chain, repeat
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.use_cases.create_events import (
    FilterOutCuttingSections,
    SectionProvider,
)
from OTAnalytics.application.use_cases.generate_flows import (
    AndPredicate,
    CrossProductFlowGenerator,
    FilterExisting,
    FilterSameSection,
    FlowGenerator,
    FlowIdGenerator,
    FlowNameGenerator,
    FlowPredicate,
    GenerateFlows,
)
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionType


class TestFilterSameSection:
    def test_filter_sections_with_same_id(self) -> None:
        south_id = SectionId("south")
        north_id = SectionId("north")

        predicate = FilterSameSection()

        assert not predicate(south_id, south_id)
        assert predicate(south_id, north_id)


class TestFilterExisting:
    def test_filter_existing_flows(self) -> None:
        south_id = SectionId("south")
        north_id = SectionId("north")
        south_to_north = Flow(
            FlowId("1"),
            name="south to north",
            start=south_id,
            end=north_id,
            distance=0,
        )
        flow_repository = Mock(spec=FlowRepository)
        flow_repository.get_all.return_value = [south_to_north]

        predicate = FilterExisting(flow_repository)

        assert not predicate(south_id, north_id)
        assert predicate(north_id, south_id)


class TestAndPredicate:
    @pytest.mark.parametrize(
        "first_value, second_value, expected_result",
        [
            (False, False, False),
            (False, True, False),
            (True, False, False),
            (True, True, True),
        ],
    )
    def test_and_then(
        self, first_value: bool, second_value: bool, expected_result: bool
    ) -> None:
        south_id = SectionId("south")
        north_id = SectionId("north")
        first = Mock(spec=FlowPredicate)
        second = Mock(spec=FlowPredicate)
        first.return_value = first_value
        second.return_value = second_value

        and_predicate = AndPredicate(first, second)

        assert and_predicate(south_id, north_id) is expected_result
        first.assert_called_once_with(south_id, north_id)
        if first_value:
            second.assert_called_once_with(south_id, north_id)


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
        predicate = Mock(spec=FlowPredicate)
        predicate.return_value = True
        self.__execute_test(sections, expected_flows, predicate)

    @pytest.mark.parametrize("sections,expected_flows", create_test_cases())
    def test_only_generate_first(
        self, sections: list[Section], expected_flows: list[Flow]
    ) -> None:
        predicate = Mock(spec=FlowPredicate)
        should_generate = chain([True], repeat(False))
        predicate.side_effect = should_generate

        self.__execute_test(sections, expected_flows[:1], predicate)

    def __execute_test(
        self,
        sections: list[Section],
        expected_flows: list[Flow],
        predicate: FlowPredicate,
    ) -> None:
        id_generator = Mock(spec=FlowIdGenerator)
        id_generator.side_effect = [flow.id for flow in expected_flows]
        name_generator = Mock(spec=FlowNameGenerator)
        name_generator.generate_from_section.return_value = [
            flow.name for flow in expected_flows
        ]
        generator = CrossProductFlowGenerator(id_generator, name_generator, predicate)

        flows = generator(sections)

        assert all(
            (current.start == expected.start) and (current.end == expected.end)
            for current, expected in zip(flows, expected_flows)
        )

        assert id_generator.call_args_list == [
            call(flow.start, flow.end) for flow in expected_flows
        ]
        sections_by_id = {section.id: section for section in sections}
        assert name_generator.generate_from_section.call_args_list == [
            call(sections_by_id[flow.start], sections_by_id[flow.end])
            for flow in expected_flows
        ]


class TestGenerateFlows:
    def test_generate_all_flows(self) -> None:
        sections: list[Section] = []
        created_flows: list[Flow] = []
        section_provider = Mock(spec=SectionProvider)
        section_provider.return_value = sections
        flow_generator = Mock(spec=FlowGenerator)
        flow_generator.return_value = created_flows
        flow_repository = Mock(spec=FlowRepository)
        generator = GenerateFlows(section_provider, flow_repository, flow_generator)

        generator.generate()

        section_provider.assert_called_once()
        flow_generator.assert_called_with(sections)
        flow_repository.add_all.assert_called_with(created_flows)

    def test_cutting_sections_are_filtered_before(self) -> None:
        """
        # Bugfix https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/4892

        @bug by randy-seng
        """  # noqa
        line_section = create_section("line_section", SectionType.LINE)
        area_section = create_section("area_section", SectionType.AREA)
        cli_cutting_section = create_section("#clicut_section", SectionType.LINE)
        cutting_section = create_section("#cut_section", SectionType.CUTTING)

        given_sections = [
            line_section,
            area_section,
            cli_cutting_section,
            cutting_section,
        ]
        expected_flows: list[Flow] = [Mock()]
        given_flow_repository = Mock()
        given_flow_generator = create_flow_generator(expected_flows)
        given = create_section_provider(given_sections)

        target = GenerateFlows(given, given_flow_repository, given_flow_generator)
        target.generate()

        given_flow_generator.assert_called_with([line_section, area_section])
        given_flow_repository.add_all.assert_called_with(expected_flows)


def create_section_provider(sections: list[Section]) -> SectionProvider:
    section_provider = Mock()
    section_provider.return_value = sections
    return FilterOutCuttingSections(section_provider)


def create_flow_generator(flows: list[Flow]) -> Mock:
    flow_generator = Mock()
    flow_generator.return_value = flows
    return flow_generator


def create_section(name: str, section_type: SectionType) -> Section:
    section = Mock()
    section.name = name
    section.get_type.return_value = section_type
    return section
