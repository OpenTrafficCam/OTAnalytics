from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    ExportCounts,
    ExportFormat,
    ExportSpecificationDto,
)
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowRepository
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId, TrackRepository

LEVEL_FLOW = "flow"
LEVEL_CLASSIFICATION = "classification"
LEVEL_START_TIME = "start time"
LEVEL_END_TIME = "end time"
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


class Tag(ABC):
    """
    Class to identify assignments for flows.
    """

    @abstractmethod
    def combine(self, other: "Tag") -> "Tag":
        """
        Combine two tags to one tag.

        Args:
            other (Tag): tag to combine with

        Returns:
            Tag: combined tag
        """
        raise NotImplementedError

    @abstractmethod
    def contained_tags(self) -> set["Tag"]:
        """
        List all tags this tag consists of.
        """
        raise NotImplementedError

    @abstractmethod
    def as_dict(self) -> dict[str, str]:
        """
        Provide a single dictionary containing the levels and names of the contained
        tags.

        Returns:
            dict[str, str]: dictionary of levels and names of tags
        """
        raise NotImplementedError


@dataclass(frozen=True)
class MultiTag(Tag):
    tags: set[Tag]

    def combine(self, other: Tag) -> Tag:
        """
        Append other tag to this one and return a new tag object.

        Args:
            other (Tag): tag to combine with

        Returns:
            Tag: combined tag
        """
        combined_tags: set[Tag] = self.contained_tags().union(other.contained_tags())
        return MultiTag(tags=combined_tags)

    def contained_tags(self) -> set[Tag]:
        """
        List all tags this tag consists of.
        """
        return self.tags.copy()

    def as_dict(self) -> dict[str, str]:
        """
        Provide a single dictionary containing the levels and names of the contained
        tags.

        Returns:
            dict[str, str]: dictionary of levels and names of tags
        """
        result: dict[str, str] = {}
        for tag in self.tags:
            result |= tag.as_dict()
        return result

    def __hash__(self) -> int:
        return hash(tuple(self.tags))


@dataclass(frozen=True)
class SingleTag(Tag):
    level: str
    id: str

    def combine(self, other: Tag) -> Tag:
        """
        Append other tag to this one and return a new tag object.

        Args:
            other (Tag): tag to combine with

        Returns:
            Tag: combined tag
        """
        return MultiTag(self.contained_tags().union(other.contained_tags()))

    def contained_tags(self) -> set[Tag]:
        """
        List all tags this tag consists of.
        """
        return {self}

    def as_dict(self) -> dict[str, str]:
        """
        Provide a single dictionary containing the level and name of the tag.

        Returns:
            dict[str, str]: dictionary of level and name of this tags
        """
        return {self.level: self.id}


def create_flow_tag(flow_name: str) -> Tag:
    return SingleTag(level=LEVEL_FLOW, id=flow_name)


def create_mode_tag(tag: str) -> Tag:
    return SingleTag(level=LEVEL_CLASSIFICATION, id=tag)


def create_timeslot_tag(start_of_time_slot: datetime, interval: timedelta) -> Tag:
    end_of_time_slot = start_of_time_slot + interval
    serialized_start = start_of_time_slot.strftime("%H:%M")
    serialized_end = end_of_time_slot.strftime("%H:%M")
    return MultiTag(
        {
            SingleTag(level=LEVEL_START_TIME, id=serialized_start),
            SingleTag(level=LEVEL_END_TIME, id=serialized_end),
        }
    )


@dataclass(frozen=True)
class Count(ABC):
    """
    Represents the result of counting traffic assigned to flows.
    """

    @abstractmethod
    def to_dict(self) -> dict[Tag, int]:
        """
        Convert the count into a serializable dictionary.

        Returns:
            dict[Tag, int]: serializable counts
        """
        raise NotImplementedError


@dataclass(frozen=True)
class CountByFlow(Count):
    """
    Class represents the counts of a single flow. Every flow is counted separately.
    The level of this count is LEVEL_FLOW
    """

    result: dict[Flow, int]

    def to_dict(self) -> dict[Tag, int]:
        """
        Convert the count into a serializable dictionary.

        Returns:
            dict[Tag, int]: serializable counts
        """
        return {
            create_flow_tag(flow.name): value for flow, value in self.result.items()
        }


@dataclass(frozen=True)
class CountDecorator(Count):
    other: Count

    def to_dict(self) -> dict[Tag, int]:
        return self.other.to_dict()


@dataclass(frozen=True)
class GroupedCount(Count):
    """
    Group various Count objects by Tag.
    """

    result: dict[Tag, Count]

    def to_dict(self) -> dict[Tag, int]:
        """
        Convert the count into a serializable dictionary.

        Returns:
            dict[Tag, int]: serializable counts
        """

        result: dict[Tag, int] = {}
        for tag, sub_result in self.result.items():
            sub_dict: dict[Tag, int] = sub_result.to_dict()
            for sub_tag, value in sub_dict.items():
                result[tag.combine(sub_tag)] = value
        return result


@dataclass(frozen=True)
class FillEmptyCount(CountDecorator):
    """
    Fill counts with zeros if empty.
    """

    tags: list[Tag]

    def to_dict(self) -> dict[Tag, int]:
        empty = {tag: 0 for tag in self.tags}
        other_result = super().to_dict()
        return empty | other_result


@dataclass(frozen=True)
class RoadUserAssignment:
    """
    Assignment of a road user to a flow.
    """

    road_user: int
    assignment: Flow
    events: EventPair


class Tagger(ABC):
    """
    Interface to split road user assignments into groups, e.g. by mode.
    """

    @abstractmethod
    def create_tag(self, assignment: RoadUserAssignment) -> Tag:
        """
        Determine a tag for the assignment, e.g. mode of the track.

        Args:
            assignment (RoadUserAssignment): assignment to determine the tag for

        Returns:
            Tag: tag of the assignment
        """
        raise NotImplementedError


class ModeTagger(Tagger):
    """
    Split RoadUserAssignments by mode.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def create_tag(self, assignment: RoadUserAssignment) -> Tag:
        """
        Group name for classification of a track or UNCLASSIFIED.

        Args:
            assignment (RoadUserAssignment): assignment to determine the tag for

        Returns:
            Tag: tag of the assignment
        """
        track = self._track_repository.get_for(TrackId(assignment.road_user))
        tag = track.classification if track else UNCLASSIFIED
        return create_mode_tag(tag)


class TimeslotTagger(Tagger):
    def __init__(self, interval: timedelta) -> None:
        self._interval = interval

    def create_tag(self, assignment: RoadUserAssignment) -> Tag:
        original_time = int(assignment.events.start.occurrence.timestamp())
        interval_seconds = self._interval.total_seconds()
        result = int(original_time / interval_seconds) * interval_seconds
        start_of_time_slot = datetime.fromtimestamp(result)
        return create_timeslot_tag(start_of_time_slot, self._interval)


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

    def __count_per_flow(self) -> dict[Flow, int]:
        """
        Count users per flow.

        Returns:
            dict[FlowId, int]: count per flow
        """
        flow_to_user: dict[Flow, list[int]] = defaultdict(list)
        for assignment in self._assignments:
            flow_to_user[assignment.assignment].append(assignment.road_user)
        return {current: len(users) for current, users in flow_to_user.items()}

    def __fill_empty_flows(
        self, flows: Iterable[Flow], counts: dict[Flow, int]
    ) -> dict[Flow, int]:
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
            if current not in counts:
                counts[current] = 0
        return counts

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CountableAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        return CountableAssignments.__name__ + repr(self._assignments)


class TaggedAssignments:
    """
    Represents a group of CountableAssignments by their tag.
    """

    def __init__(self, assignments: dict[Tag, CountableAssignments]) -> None:
        self._assignments = assignments

    def count(self, flows: list[Flow]) -> Count:
        """
        Count per assignment and assign the result to the respective tag.

        Args:
            flows (list[Flow]): flows to count for

        Returns:
            Count: traffic counts per Tag
        """
        return GroupedCount(
            {
                tag: assignment.count(flows)
                for tag, assignment in self._assignments.items()
            }
        )

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TaggedAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        return TaggedAssignments.__name__ + repr(self._assignments)


class RoadUserAssignments:
    """
    Represents a group of RoadUserAssignment objects.
    """

    def __init__(self, assignments: list[RoadUserAssignment]) -> None:
        self._assignments = assignments.copy()

    def tag(self, by: Tagger) -> TaggedAssignments:
        """
        Split the assignments using the given tagger. Each assignment is assigned to
        exactly one part.

        Args:
            by (Tagger): tagger to determine the tag

        Returns:
            TaggedAssignments: group of RoadUserAssignments split by tag
        """
        tagged: dict[Tag, list[RoadUserAssignment]] = defaultdict(list)
        for assignment in self._assignments:
            tag = by.create_tag(assignment)
            tagged[tag].append(assignment)
        return TaggedAssignments(
            {key: CountableAssignments(value) for key, value in tagged.items()}
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
        grouped_events = self.__group_events_by_road_user(events)
        return self.__assign_user_to_flow(grouped_flows, grouped_events)

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
        Group events by road user.

        Args:
            events (Iterable[Event]): events of a road user

        Returns:
            dict[int, list[Event]]: events grouped by user
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
            events_by_road_user (dict[int, list[Event]]): events by road user

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
                        assignment=current.flow,
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
            flows (dict[tuple[SectionId, SectionId], list[Flow]]): flows by start and
                end section
            events (list[Event]): events belonging to road user

        Returns:
            list[FlowCandidate]: the flow candidates pertaining to road user
        """
        event_pairs = self.__create_event_pairs(events)
        return self.__create_candidate_flows(flows, event_pairs)

    def __create_event_pairs(self, events: list[Event]) -> list[EventPair]:
        """
        Create event pairs.

        Requires and assumes events to be sorted by occurrence.

        Args:
            events(list[Event]): events to create the event pairs with

        Returns:
            list[EventPair]: event pairs
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
            event_pairs (list[EventPair]): pairs of events to match with flows

        Returns:
            list[FlowCandidate]: flows matching one pair of events
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
        with the largest distance by time.
        Args:
            candidate_flows (list[FlowCandidate]): flow candidates to select from
        Returns:
            Flow: best matching flow candidate
        """
        return max(candidate_flows, key=lambda current: current.duration())


class TaggerFactory(ABC):
    """
    Factory interface to create a Tagger based on the given CountingSpecificationDto.
    """

    def create_tagger(self, specification: CountingSpecificationDto) -> Tagger:
        """
        Create a Tagger based on the given CountingSpecificationDto.

        Args:
            specification (CountingSpecificationDto): specification to create a
            tagger for

        Returns:
            Tagger: Tagger matching the given specification
        """
        raise NotImplementedError


class CombinedTagger(Tagger):
    """
    Combine two taggers and apply both tagging operations.
    """

    def __init__(self, first: Tagger, second: Tagger) -> None:
        self._first = first
        self._second = second

    def create_tag(self, assignment: RoadUserAssignment) -> Tag:
        """
        Apply first and second tagging operations and combine both tags.

        Args:
            assignment (RoadUserAssignment): assignment to tag

        Returns:
            Tag: combined tags of both taggers
        """
        first_assignment = self._first.create_tag(assignment)
        second_assignment = self._second.create_tag(assignment)
        return first_assignment.combine(second_assignment)


class SimpleTaggerFactory(TaggerFactory):
    """
    Factory to create Tagger for a given CountingSpecification.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def create_tagger(self, specification: CountingSpecificationDto) -> Tagger:
        """
        Create a tagger for the given CountingSpecificationDto.

        Args:
            specification (CountingSpecificationDto): specification of the Tagger

        Returns:
            Tagger: Tagger specified by the given CountingSpecificationDto
        """
        mode_tagger = ModeTagger(self._track_repository)
        time_tagger = TimeslotTagger(
            timedelta(minutes=specification.interval_in_minutes)
        )
        return CombinedTagger(mode_tagger, time_tagger)


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

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        """
        Create the exporter for the given CountingSpecificationDto.

        Args:
            specification (CountingSpecificationDto): specification of the Exporter

        Returns:
            Exporter: Exporter to export counts
        """
        raise NotImplementedError


def create_export_specification(
    flows: list[Flow], counting_specification: CountingSpecificationDto
) -> ExportSpecificationDto:
    flow_names = [flow.name for flow in flows]
    return ExportSpecificationDto(counting_specification, flow_names)


class ExportTrafficCounting(ExportCounts):
    """
    Use case to export traffic countings.
    """

    def __init__(
        self,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        assigner: RoadUserAssigner,
        tagger_factory: TaggerFactory,
        exporter_factory: ExporterFactory,
    ) -> None:
        self._event_repository = event_repository
        self._flow_repository = flow_repository
        self._assigner = assigner
        self._tagger_factory = tagger_factory
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
        tagger = self._tagger_factory.create_tagger(specification)
        tagged_assignments = assigned_flows.tag(tagger)
        counts = tagged_assignments.count(flows)
        export_specification = create_export_specification(flows, specification)
        exporter = self._exporter_factory.create_exporter(export_specification)
        exporter.export(counts)

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats
        """
        return self._exporter_factory.get_supported_formats()
