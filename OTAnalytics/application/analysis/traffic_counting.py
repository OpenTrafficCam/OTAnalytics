from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional

from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId, TrackRepository

LEVEL_FLOW = "flow"
LEVEL_CLASSIFICATION = "classification"
LEVEL_TIME = "time"
UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class EventPair:
    """
    Pair of events of one track to find a matching flow.
    """

    start: Event
    end: Event


@dataclass(frozen=True)
class FlowCandidate:
    """
    Possible candidate to match a flow with a track.
    """

    flow: Flow
    candidate: EventPair

    def distance(self) -> Optional[float]:
        return self.flow.distance

    def duration(self) -> timedelta:
        return self.candidate.end.occurrence - self.candidate.start.occurrence


class SplitId(ABC):
    """
    Id class to be used to identify assignments for flows.
    """

    @abstractmethod
    def combine(self, other: "SplitId") -> "SplitId":
        """
        Combine two ids to a one id.

        Args:
            other (SplitId): id to combine with

        Returns:
            SplitId: combined id
        """
        raise NotImplementedError

    @abstractmethod
    def ids(self) -> list["SplitId"]:
        """
        List all ids this id consists of.
        """
        raise NotImplementedError

    @abstractmethod
    def as_dict(self) -> dict[str, str]:
        """
        Provide a single dictionary containing the levels and names of the contained
        ids.

        Returns:
            dict[str, str]: dictionary of levels and names of ids
        """
        raise NotImplementedError


@dataclass(frozen=True)
class CombinedId(SplitId):
    id: list[SplitId]

    def combine(self, other: SplitId) -> SplitId:
        """
        Append other id to this one and return a new id object.

        Args:
            other (SplitId): id to combine with

        Returns:
            SplitId: combined id
        """
        combined_ids: list[SplitId] = self.ids() + other.ids()
        return CombinedId(id=combined_ids)

    def ids(self) -> list[SplitId]:
        """
        List all ids this id consists of.
        """
        return self.id.copy()

    def as_dict(self) -> dict[str, str]:
        """
        Provide a single dictionary containing the levels and names of the contained
        ids.

        Returns:
            dict[str, str]: dictionary of levels and names of ids
        """
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
        """
        Append other id to this one and return a new id object.

        Args:
            other (SplitId): id to combine with

        Returns:
            SplitId: combined id
        """
        return CombinedId(self.ids() + other.ids())

    def ids(self) -> list[SplitId]:
        """
        List all ids this id consists of.
        """
        return [self]

    def as_dict(self) -> dict[str, str]:
        """
        Provide a single dictionary containing the level and name of the id.

        Returns:
            dict[str, str]: dictionary of level and name of this ids
        """
        return {self.level: self.id}


@dataclass(frozen=True)
class Count(ABC):
    """
    Represents the result of counting traffic assigned to flows.
    """

    @abstractmethod
    def to_dict(self) -> dict[SplitId, int]:
        """
        Convert the count into a serializable dictionary.

        Returns:
            dict[SplitId, int]: serializable counts
        """
        raise NotImplementedError


@dataclass(frozen=True)
class CountByFlow(Count):
    """
    Class represents the counts of a single flow. Every flow is counted separately.
    The level of this count is LEVEL_FLOW
    """

    result: dict[FlowId, int]

    def to_dict(self) -> dict[SplitId, int]:
        """
        Convert the count into a serializable dictionary.

        Returns:
            dict[SplitId, int]: serializable counts
        """
        return {
            SingleId(level=LEVEL_FLOW, id=id.serialize()): value
            for id, value in self.result.items()
        }


@dataclass(frozen=True)
class GroupedCount(Count):
    """
    Group various Count objects by SplitId.
    """

    result: dict[SplitId, Count]

    def to_dict(self) -> dict[SplitId, int]:
        """
        Convert the count into a serializable dictionary.

        Returns:
            dict[SplitId, int]: serializable counts
        """

        result: dict[SplitId, int] = {}
        for split_id, sub_result in self.result.items():
            sub_dict: dict[SplitId, int] = sub_result.to_dict()
            for sub_id, value in sub_dict.items():
                result[split_id.combine(sub_id)] = value
        return result


@dataclass(frozen=True)
class RoadUserAssignment:
    """
    Assignment of a road user to a flow.
    """

    road_user: int
    assignment: FlowId
    events: EventPair


class Splitter(ABC):
    """
    Interface to split road user assignments into groups, e.g. by mode.
    """

    @abstractmethod
    def group_name(self, assignment: RoadUserAssignment) -> SplitId:
        """
        Determine a group name for the assignment, e.g. mode of the track.

        Args:
            assignment (RoadUserAssignment): assignment to determine the group name for

        Returns:
            SplitId: id of the split
        """
        raise NotImplementedError


class ModeSplitter(Splitter):
    """
    Split RoadUserAssignments by mode.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def group_name(self, assignment: RoadUserAssignment) -> SplitId:
        """
        Group name for classification of a track or UNCLASSIFIED.

        Args:
            assignment (RoadUserAssignment): assignment to determine the group name for

        Returns:
            SplitId: id of the split
        """
        track = self._track_repository.get_for(TrackId(assignment.road_user))
        split_id = track.classification if track else UNCLASSIFIED
        return SingleId(level=LEVEL_CLASSIFICATION, id=split_id)


class TimeSplitter(Splitter):
    def __init__(self, interval: timedelta) -> None:
        self._interval = interval

    def group_name(self, assignment: RoadUserAssignment) -> SplitId:
        original_time = int(assignment.events.start.occurrence.timestamp())
        interval_seconds = self._interval.total_seconds()
        result = int(original_time / interval_seconds) * interval_seconds
        time_slot = datetime.fromtimestamp(result).strftime("%H:%M")
        return SingleId(level=LEVEL_TIME, id=time_slot)


class CountableAssignments:
    """
    Class to represent countable road users.
    """

    def __init__(self, assignments: list[RoadUserAssignment]) -> None:
        self._assignments = assignments.copy()

    def count(self, flows: list[Flow]) -> Count:
        """
        Count the assignments. Flow without an assignment are assigned a zero count.

        Args:
            flows (list[Flow]): flows to count for

        Returns:
            Count: traffic counts per flow
        """
        counts = self.__count_per_flow()
        self.__fill_empty_flows(flows, counts)
        return CountByFlow(counts)

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
        if isinstance(other, CountableAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        return CountableAssignments.__name__ + repr(self._assignments)


class SplittedAssignments:
    """
    Represents a group of CountableAssignments by their id.
    """

    def __init__(self, assignments: dict[SplitId, CountableAssignments]) -> None:
        self._assignments = assignments

    def count(self, flows: list[Flow]) -> Count:
        """
        Count per assignment and assign the result to the respective id.

        Args:
            flows (list[Flow]): flows to count for

        Returns:
            Count: traffic counts per SplitId
        """
        return GroupedCount(
            {
                split_id: assignment.count(flows)
                for split_id, assignment in self._assignments.items()
            }
        )

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SplittedAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        return SplittedAssignments.__name__ + repr(self._assignments)


class RoadUserAssignments:
    """
    Represents a group of RoadUserAssignment objects.
    """

    def __init__(self, assignments: list[RoadUserAssignment]) -> None:
        self._assignments = assignments.copy()

    def split(self, by: Splitter) -> SplittedAssignments:
        """
        Split the assignments using the given splitter. Each assignment is assigned to
        exactly one part.

        Args:
            by (Splitter): splitter to determine the group name

        Returns:
            SplittedAssignments: group of RoadUserAssignments splitted by group name
        """
        splitted: dict[SplitId, list[RoadUserAssignment]] = defaultdict(list)
        for assignment in self._assignments:
            group_name = by.group_name(assignment)
            splitted[group_name].append(assignment)
        return SplittedAssignments(
            {key: CountableAssignments(value) for key, value in splitted.items()}
        )

    def as_list(self) -> list[RoadUserAssignment]:
        """
        Retrieves a copy of the contained assignments.

        Returns:
            list[RoadUserAssignment]: a copy of the assignments
        """
        return self._assignments.copy()

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoadUserAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        return RoadUserAssignments.__name__ + repr(self._assignments)


class RoadUserAssigner:
    """
    Class to assign tracks to flows.
    """

    def assign(self, events: Iterable[Event], flows: list[Flow]) -> RoadUserAssignments:
        """
        Assign each track to exactly one flow.

        Args:
            events (Iterable[Event]): events to be used during assignment
            flows (list[Flow]): flows to assign tracks to

        Returns:
            RoadUserAssignments: group of RoadUserAssignment objects
        """
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
        sorted_events = sorted(events, key=lambda event: event.occurrence)
        for event in sorted_events:
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
                    RoadUserAssignment(
                        road_user=road_user,
                        assignment=current.flow.id,
                        events=current.candidate,
                    )
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
        for index, start in enumerate(events):
            candidates.extend(
                EventPair(start=start, end=end)
                for end in events[index + 1 :]
                if end != start
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

    def __select_flow(self, candidate_flows: list[FlowCandidate]) -> FlowCandidate:
        """
        Select the best matching flow for the user. Best match is defined as the flow
        with the largest distance.
        Args:
            candidate_flows (list[Flow]): candidate flows to select from
        Returns:
            Flow: best matching flow
        """
        return max(candidate_flows, key=lambda current: current.duration())


@dataclass(frozen=True)
class CountingSpecificationDto:
    """
    Data transfer object to represent the counting.
    """

    interval_in_minutes: int
    format: str
    output_file: str


class SplitterFactory(ABC):
    """
    Factory interface to create a Splitter based on the given CountingSpecificationDto.
    """

    def create_splitter(self, specification: CountingSpecificationDto) -> Splitter:
        """
        Create a Splitter based on the given CountingSpecificationDto.

        Args:
            specification (CountingSpecificationDto): specification to create a
            splitter for

        Returns:
            Splitter: Splitter matching the given specification
        """
        raise NotImplementedError


class CombinedSplitter(Splitter):
    """
    Combine two splitters and apply both splitting operations.
    """

    def __init__(self, first: Splitter, second: Splitter) -> None:
        self._first = first
        self._second = second

    def group_name(self, assignment: RoadUserAssignment) -> SplitId:
        """
        Apply first and second splitting operations and combine both ids.

        Args:
            assignment (RoadUserAssignment): assignment to split

        Returns:
            SplitId: combined split id of both splitters
        """
        first_assignment = self._first.group_name(assignment)
        second_assignment = self._second.group_name(assignment)
        return first_assignment.combine(second_assignment)


class SimpleSplitterFactory(SplitterFactory):
    """
    Factory to create Splitter for a given CountingSpecification.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def create_splitter(self, specification: CountingSpecificationDto) -> Splitter:
        """
        Create a splitter for the given CountingSpecificationDto.

        Args:
            specification (CountingSpecificationDto): specification of the Splitter

        Returns:
            Splitter: Splitter specifiec by the given CountingSpecificationDto
        """
        mode_splitter = ModeSplitter(self._track_repository)
        time_splitter = TimeSplitter(
            timedelta(minutes=specification.interval_in_minutes)
        )
        return CombinedSplitter(mode_splitter, time_splitter)


class Exporter(ABC):
    """
    Interface to abstract various export formats.
    """

    def export(self, counts: Count) -> None:
        """
        Export the given counts.

        Args:
            counts (Count): counts to export
        """
        raise NotImplementedError


@dataclass(frozen=True)
class ExportFormat:
    name: str
    file_extension: str


class ExporterFactory(ABC):
    """
    Factory to create the exporter for the given CountingSpecificationDto.
    """

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats
        """
        raise NotImplementedError

    def create_exporter(self, specification: CountingSpecificationDto) -> Exporter:
        """
        Create the exporter for the given CountingSpecificationDto.

        Args:
            specification (CountingSpecificationDto): specification of the Exporter

        Returns:
            Exporter: Exporter to export counts
        """
        raise NotImplementedError


class ExportTrafficCounting:
    """
    Use case to export traffic countings.
    """

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
        """
        Export the traffic countings based on the currently available evens and flows.

        Args:
            specification (CountingSpecificationDto): specification of the export
        """
        events = self._event_repository.get_all()
        flows = self._flow_repository.get_all()
        assigned_flows = self._assigner.assign(events, flows)
        splitter = self._splitter_factory.create_splitter(specification)
        splitted_assignments = assigned_flows.split(splitter)
        counts = splitted_assignments.count(flows)
        exporter = self._exporter_factory.create_exporter(specification)
        exporter.export(counts)

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats
        """
        return self._exporter_factory.get_supported_formats()
