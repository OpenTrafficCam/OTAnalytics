import itertools
from abc import ABC

from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionRepository


class FlowIdGenerator(ABC):
    def generate_id(self, start: SectionId, end: SectionId) -> FlowId:
        raise NotImplementedError


class FlowNameGenerator(ABC):
    def generate_name(self, start: SectionId, end: SectionId) -> str:
        raise NotImplementedError


class FlowGenerator(ABC):
    def generate(self, sections: list[Section]) -> list[Flow]:
        raise NotImplementedError


class FlowPredicate(ABC):
    def should_generate(self, start: SectionId, end: SectionId) -> bool:
        raise NotImplementedError


class CrossProductFlowGenerator(FlowGenerator):
    def __init__(
        self,
        id_generator: FlowIdGenerator,
        name_generator: FlowNameGenerator,
        predicate: FlowPredicate,
    ) -> None:
        self._id_generator = id_generator
        self._name_generator = name_generator
        self._predicate = predicate

    def generate(self, sections: list[Section]) -> list[Flow]:
        return [
            self.__create_flow(start, end)
            for start, end in itertools.product(sections, sections)
            if self._predicate.should_generate(start.id, end.id)
        ]

    def __create_flow(self, start: Section, end: Section) -> Flow:
        flow_id = self._id_generator.generate_id(start.id, end.id)
        name = self._name_generator.generate_name(start.id, end.id)
        return Flow(id=flow_id, name=name, start=start.id, end=end.id, distance=0)


class GenerateFlows:
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
        sections = self._section_repository.get_all()
        flows = self._flow_generator.generate(sections)
        self._flow_repository.add_all(flows)
