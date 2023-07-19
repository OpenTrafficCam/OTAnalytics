import itertools
from abc import ABC

from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionRepository


class FlowIdGenerator(ABC):
    """Generate an id for a flow consisting of the given start and end sections"""

    def __call__(self, start: SectionId, end: SectionId) -> FlowId:
        """Generate an id for a flow using the given sections.

        Args:
            start (Section): section where the flow starts
            end (Section): section where the flow ends

        Returns:
            FlowId: id of the flow
        """
        raise NotImplementedError


class RepositoryFlowIdGenerator(FlowIdGenerator):
    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def __call__(self, start: SectionId, end: SectionId) -> FlowId:
        return self._flow_repository.get_id()


class FlowNameGenerator(ABC):
    """Generate a name for a flow consisting of the given start and end sections"""

    def generate_from_section(self, start: Section, end: Section) -> str:
        """Generate a name for a flow using the given sections.

        Args:
            start (Section): section where the flow starts
            end (Section): section where the flow ends

        Returns:
            str: name of the flow
        """
        raise NotImplementedError

    def generate_from_string(self, start: str, end: str) -> str:
        """Generate a name for a flow using the given sections.

        Args:
            start (str): section where the flow starts
            end (str): section where the flow ends

        Returns:
            str: name of the flow
        """
        raise NotImplementedError


class ArrowFlowNameGenerator(FlowNameGenerator):
    def generate_from_section(self, start: Section, end: Section) -> str:
        return self.generate_from_string(start.name, end.name)

    def generate_from_string(self, start: str, end: str) -> str:
        return f"{start} --> {end}"


class FlowGenerator(ABC):
    """Generate flows using the given sections"""

    def __call__(self, sections: list[Section]) -> list[Flow]:
        raise NotImplementedError


class FlowPredicate(ABC):
    """Predicate to select if a flow should be generated for a pair of sections."""

    def __call__(self, start: SectionId, end: SectionId) -> bool:
        raise NotImplementedError


class FilterSameSection(FlowPredicate):
    """Do not generate flows if start and end are equal."""

    def __call__(self, start: SectionId, end: SectionId) -> bool:
        return start != end


class CrossProductFlowGenerator(FlowGenerator):
    """Generate flows for all combinations of sections."""

    def __init__(
        self,
        id_generator: FlowIdGenerator,
        name_generator: FlowNameGenerator,
        predicate: FlowPredicate,
    ) -> None:
        self._id_generator = id_generator
        self._name_generator = name_generator
        self._predicate = predicate

    def __call__(self, sections: list[Section]) -> list[Flow]:
        return [
            self.__create_flow(start, end)
            for start, end in itertools.product(sections, sections)
            if self._predicate(start.id, end.id)
        ]

    def __create_flow(self, start: Section, end: Section) -> Flow:
        flow_id = self._id_generator(start.id, end.id)
        name = self._name_generator.generate_from_section(start, end)
        return Flow(id=flow_id, name=name, start=start.id, end=end.id, distance=0)


class GenerateFlows:
    """
    Use case to generate flows. The flow generator will be used to generate the flows
    using all sections from the section repository. The resulting flows will be stored
    in the flow repository.
    """

    def __init__(
        self,
        section_repository: SectionRepository,
        flow_repository: FlowRepository,
        flow_generator: FlowGenerator,
    ) -> None:
        self._section_repository = section_repository
        self._flow_repository = flow_repository
        self._flow_generator = flow_generator

    def generate(self) -> None:
        """
        Use all sections from the section repository to generate flows using the flow
        generator. Store the resulting flows in the flow repository.
        """
        sections = self._section_repository.get_all()
        flows = self._flow_generator(sections)
        self._flow_repository.add_all(flows)
