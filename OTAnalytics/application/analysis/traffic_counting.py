from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, Optional

from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId, TrackRepository


@dataclass(frozen=True)
class EventPair:
    start: Event
    end: Event


@dataclass(frozen=True)
class FlowCandidate:
    flow: Flow
    candidate: EventPair

    def distance(self) -> Optional[float]:
        return self.flow.distance

    def duration(self) -> timedelta:
        return self.candidate.end.occurrence - self.candidate.start.occurrence


class SplitId(ABC):
    @abstractmethod
    def combine(self, other: "SplitId") -> "SplitId":
        raise NotImplementedError

    @abstractmethod
    def ids(self) -> list["SplitId"]:
        raise NotImplementedError

    @abstractmethod
    def as_dict(self) -> dict[str, str]:
        raise NotImplementedError


@dataclass(frozen=True)
class CombinedId(SplitId):
    id: list[SplitId]

    def combine(self, other: SplitId) -> SplitId:
        combined_ids: list[SplitId] = self.ids() + other.ids()
        return CombinedId(id=combined_ids)

    def ids(self) -> list[SplitId]:
        return self.id.copy()

    def as_dict(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for id in self.id:
            result |= id.as_dict()
        return result

    def __hash__(self) -> int:
        return hash(tuple(self.id))


@dataclass(frozen=True)
class SingleId(SplitId):
    level: str
    id: str

    def combine(self, other: SplitId) -> SplitId:
        return CombinedId(self.ids() + other.ids())

    def ids(self) -> list[SplitId]:
        return [self]

    def as_dict(self) -> dict[str, str]:
        return {self.level: self.id}


@dataclass(frozen=True)
class Count(ABC):
    @abstractmethod
    def to_dict(self) -> dict[SplitId, int]:
        pass


@dataclass(frozen=True)
class SimpleCount(Count):
    result: dict[FlowId, int]

    def to_dict(self) -> dict[SplitId, int]:
        return {
            SingleId(level="flow", id=id.serialize()): value
            for id, value in self.result.items()
        }


@dataclass(frozen=True)
class GroupedCount(Count):
    result: dict[SplitId, Count]

    def to_dict(self) -> dict[SplitId, int]:
        result: dict[SplitId, int] = {}
        for split_id, sub_result in self.result.items():
            sub_dict: dict[SplitId, int] = sub_result.to_dict()
            for sub_id, value in sub_dict.items():
                result[split_id.combine(sub_id)] = value
        return result


@dataclass(frozen=True)
class RoadUserAssignment:
    road_user: int
    assignment: FlowId


class Splitter(ABC):
    @abstractmethod
    def group_name(self, assignment: RoadUserAssignment) -> SplitId:
        raise NotImplementedError


UNCLASSIFIED = "unclassified"
CLASSIFICATION = "classification"


class ModeSplitter(Splitter):
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def group_name(self, assignment: RoadUserAssignment) -> SplitId:
        track = self._track_repository.get_for(TrackId(assignment.road_user))
        split_id = track.classification if track else UNCLASSIFIED
        return SingleId(level=CLASSIFICATION, id=split_id)


class CountableRoadUserAssignments:
    def __init__(self, assignments: list[RoadUserAssignment]) -> None:
        self._assignments = assignments.copy()

    def count(self, flows: list[Flow]) -> Count:
        counts = self.__count_per_flow()
        self.__fill_empty_flows(flows, counts)
        return SimpleCount(counts)

    def __count_per_flow(self) -> dict[FlowId, int]:
        """
        Count users per flow.
        Args:
            user_to_flow (dict[int, FlowId]): assigment of users to flows
        Returns:
            dict[FlowId, int]: count per flow
        """
        flow_to_user: dict[FlowId, list[int]] = defaultdict(list)
        for assignment in self._assignments:
            flow_to_user[assignment.assignment].append(assignment.road_user)
        return {current: len(users) for current, users in flow_to_user.items()}

    def __fill_empty_flows(
        self, flows: Iterable[Flow], counts: dict[FlowId, int]
    ) -> dict[FlowId, int]:
        """
        Assign all flows a counting of zero if they are not present in the counts
        dictionary.
        Args:
            flows (Iterable[Flow]): all flows to count for
            counts (dict[FlowId, int]): counted users per flow
        Returns:
            dict[FlowId, int]: counted users per flow, filled with zero for empty flows
        """
        for current in flows:
            if current.id not in counts:
                counts[current.id] = 0
        return counts

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CountableRoadUserAssignments):
            return self._assignments == other._assignments
        return False


class RoadUserAssignments:
    def __init__(self, assignments: list[RoadUserAssignment]) -> None:
        self._assignments = assignments.copy()

    def split(self, by: Splitter) -> dict[SplitId, CountableRoadUserAssignments]:
        splitted: dict[SplitId, list[RoadUserAssignment]] = defaultdict(list)
        for assignment in self._assignments:
            group_name = by.group_name(assignment)
            splitted[group_name].append(assignment)
        return {
            key: CountableRoadUserAssignments(value) for key, value in splitted.items()
        }

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoadUserAssignments):
            return self._assignments == other._assignments
        return False


class RoadUserAssigner:
    def assign(self, events: Iterable[Event], flows: list[Flow]) -> RoadUserAssignments:
        grouped_flows = self.__group_flows_by_sections(flows)
        grouped_sections = self.__group_events_by_road_user(events)
        return self.__assign_user_to_flow(grouped_flows, grouped_sections)

    def __group_flows_by_sections(
        self, flows: Iterable[Flow]
    ) -> dict[tuple[SectionId, SectionId], list[Flow]]:
        """
        Group the flows by start and end section.
        Args:
            flows (Iterable[Flow]): flows to group
        Returns:
            dict[tuple[SectionId, SectionId], list[Flow]]: flows grouped by start and
            end section
        """
        flows_by_start_and_end: dict[
            tuple[SectionId, SectionId], list[Flow]
        ] = defaultdict(list)
        for current in flows:
            flows_by_start_and_end[(current.start, current.end)].append(current)
        return flows_by_start_and_end

    def __group_events_by_road_user(
        self, events: Iterable[Event]
    ) -> dict[int, list[Event]]:
        """
        Group the sections of the events by road user.
        Args:
            events (Iterable[Event]): events of a road user
        Returns:
            dict[int, list[SectionId]]: sections grouped by user
        """
        events_by_road_user: dict[int, list[Event]] = defaultdict(list)
        for event in events:
            if event.section_id:
                events_by_road_user[event.road_user_id].append(event)
        return events_by_road_user

    def __assign_user_to_flow(
        self,
        flows: dict[tuple[SectionId, SectionId], list[Flow]],
        events_by_road_user: dict[int, list[Event]],
    ) -> RoadUserAssignments:
        """
        Assign each user to exactly one flow.
        Args:
            flows (dict[tuple[SectionId, SectionId], list[Flow]]): flows by start and
            end section
            sections_by_road_user (dict[int, list[SectionId]]): sections by road user
        Returns:
            dict[int, FlowId]: assignment of flow to road user
        """
        assignments: list[RoadUserAssignment] = []
        for road_user, events in events_by_road_user.items():
            if candidate_flows := self.__create_candidates(flows, events):
                current = self.__select_flow(candidate_flows)
                assignments.append(
                    RoadUserAssignment(road_user=road_user, assignment=current.id)
                )
        return RoadUserAssignments(assignments)

    def __create_candidates(
        self,
        flows: dict[tuple[SectionId, SectionId], list[Flow]],
        events: list[Event],
    ) -> list[FlowCandidate]:
        """
        Create flow candidates to select one from in a later step.
        Args:
            flows (dict[tuple[SectionId, SectionId], list[Flow]]): _description_
            sections (list[SectionId]): _description_
        Returns:
            list[Flow]: _description_
        """
        event_pairs = self.__create_event_pairs(events)
        return self.__create_candidate_flows(flows, event_pairs)

    def __create_event_pairs(self, events: list[Event]) -> list[EventPair]:
        """
        Create section pairs. This is effectively the cross product of the given list.
        Args:
            sections (list[SectionId]): sections to create the cross product from
        Returns:
            list[tuple[SectionId, SectionId]]: section pairs
        """
        candidates: list[EventPair] = []
        for start in events:
            candidates.extend(
                EventPair(start=start, end=end) for end in events if end != start
            )
        return candidates

    def __create_candidate_flows(
        self,
        flows: dict[tuple[SectionId, SectionId], list[Flow]],
        event_pairs: list[EventPair],
    ) -> list[FlowCandidate]:
        """
        Intersect the section pairs with the flows. Emit a candidate per match.
        Args:
            flows (dict[tuple[SectionId, SectionId], list[Flow]]): flows grouped by
            start and end section
            section_pairs (list[tuple[SectionId, SectionId]]): pairs of sections
            to match with flows
        Returns:
            list[Flow]: flows matching one pair of events
        """
        candidate_flows: list[FlowCandidate] = []
        for candidate in event_pairs:
            if start_section := candidate.start.section_id:
                if end_section := candidate.end.section_id:
                    candidate_id: tuple[SectionId, SectionId] = (
                        start_section,
                        end_section,
                    )
                    for current in flows.get(candidate_id, []):
                        candidate_flow = FlowCandidate(
                            flow=current, candidate=candidate
                        )
                        candidate_flows.append(candidate_flow)
        return candidate_flows

    def __select_flow(self, candidate_flows: list[FlowCandidate]) -> Flow:
        """
        Select the best matching flow for the user. Best match is defined as the flow
        with the largest distance.
        Args:
            candidate_flows (list[Flow]): candidate flows to select from
        Returns:
            Flow: best matching flow
        """
        return max(candidate_flows, key=lambda current: current.duration()).flow


@dataclass(frozen=True)
class CountingSpecificationDto:
    interval_in_minutes: int
    format: str
    output_file: str


class SplitterFactory(ABC):
    def create_splitter(self, specification: CountingSpecificationDto) -> Splitter:
        raise NotImplementedError


class SimpleSplitterFactory(SplitterFactory):
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def create_splitter(self, specification: CountingSpecificationDto) -> Splitter:
        return ModeSplitter(self._track_repository)


class Exporter(ABC):
    def export(self, counts: Count) -> None:
        raise NotImplementedError


class ExporterFactory(ABC):
    def create_exporter(self, specification: CountingSpecificationDto) -> Exporter:
        raise NotImplementedError


class ExportTrafficCounting:
    def __init__(
        self,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        assigner: RoadUserAssigner,
        splitter_factory: SplitterFactory,
        exporter_factory: ExporterFactory,
    ) -> None:
        self._event_repository = event_repository
        self._flow_repository = flow_repository
        self._assigner = assigner
        self._splitter_factory = splitter_factory
        self._exporter_factory = exporter_factory

    def export(self, specification: CountingSpecificationDto) -> None:
        events = self._event_repository.get_all()
        flows = self._flow_repository.get_all()
        assigned_flows = self._assigner.assign(events, flows)
        splitter = self._splitter_factory.create_splitter(specification)
        splitted_assignments = assigned_flows.split(by=splitter)
        counts = GroupedCount(
            {
                split_id: assignment.count(flows)
                for split_id, assignment in splitted_assignments.items()
            }
        )
        exporter = self._exporter_factory.create_exporter(specification)
        exporter.export(counts)
