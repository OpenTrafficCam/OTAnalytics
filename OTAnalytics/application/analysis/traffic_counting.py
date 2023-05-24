from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import SectionId


class TrafficCounter(ABC):
    @abstractmethod
    def count(self, events: list[Event], flows: list[Flow]) -> dict[FlowId, int]:
        pass


class RunTrafficCounting(TrafficCounter):
    """Count road users per flow."""

    def count(self, events: list[Event], flows: list[Flow]) -> dict[FlowId, int]:
        grouped_flows = self.__group_flows_by_sections(flows)
        grouped_sections = self._group_sections_by_road_user(events)
        assigned_users = self.__assign_user_to_flow(grouped_flows, grouped_sections)
        counts = self.__count_users_per_flow(assigned_users)
        self.__fill_empty_flows(flows, counts)
        return counts

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
        for flow in flows:
            flows_by_start_and_end[(flow.start.id, flow.end.id)].append(flow)
        return flows_by_start_and_end

    def _group_sections_by_road_user(
        self, events: Iterable[Event]
    ) -> dict[int, list[SectionId]]:
        """
        Group the sections of the events by road user.
        Args:
            events (Iterable[Event]): events of a road user
        Returns:
            dict[int, list[SectionId]]: sections grouped by user
        """
        sections_by_road_user: dict[int, list[SectionId]] = defaultdict(list)
        for event in events:
            if event.section_id:
                sections_by_road_user[event.road_user_id].append(event.section_id)
        return sections_by_road_user

    def __assign_user_to_flow(
        self,
        flows: dict[tuple[SectionId, SectionId], list[Flow]],
        sections_by_road_user: dict[int, list[SectionId]],
    ) -> dict[int, FlowId]:
        """
        Assign each user to exactly one flow.
        Args:
            flows (dict[tuple[SectionId, SectionId], list[Flow]]): flows by start and
            end section
            sections_by_road_user (dict[int, list[SectionId]]): sections by road user
        Returns:
            dict[int, FlowId]: assignment of flow to road user
        """
        user_to_flow: dict[int, FlowId] = {}
        for road_user, sections in sections_by_road_user.items():
            if candidate_flows := self.__create_candidates(flows, sections):
                flow = self.__select_flow(candidate_flows)
                user_to_flow[road_user] = flow.id
        return user_to_flow

    def __create_candidates(
        self,
        flows: dict[tuple[SectionId, SectionId], list[Flow]],
        sections: list[SectionId],
    ) -> list[Flow]:
        """
        Create flow candidates to select one from in a later step.
        Args:
            flows (dict[tuple[SectionId, SectionId], list[Flow]]): _description_
            sections (list[SectionId]): _description_
        Returns:
            list[Flow]: _description_
        """
        section_pairs = self.__create_section_pairs(sections)
        return self.__create_candidate_flows(flows, section_pairs)

    def __create_section_pairs(
        self, sections: list[SectionId]
    ) -> list[tuple[SectionId, SectionId]]:
        """
        Create section pairs. This is effectively the cross product of the given list.
        Args:
            sections (list[SectionId]): sections to create the cross product from
        Returns:
            list[tuple[SectionId, SectionId]]: section pairs
        """
        candidates: list[tuple[SectionId, SectionId]] = []
        for start in sections:
            candidates.extend((start, end) for end in sections)
        return candidates

    def __create_candidate_flows(
        self,
        flows: dict[tuple[SectionId, SectionId], list[Flow]],
        section_pairs: list[tuple[SectionId, SectionId]],
    ) -> list[Flow]:
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
        candidate_flows: list[Flow] = []
        for candidate in section_pairs:
            candidate_flows.extend(flows.get(candidate, []))
        return candidate_flows

    def __select_flow(self, candidate_flows: list[Flow]) -> Flow:
        """
        Select the best matching flow for the user. Best match is defined as the flow
        with the largest distance.
        Args:
            candidate_flows (list[Flow]): candidate flows to select from
        Returns:
            Flow: best matching flow
        """
        return max(candidate_flows, key=lambda current: current.distance)

    def __count_users_per_flow(
        self, user_to_flow: dict[int, FlowId]
    ) -> dict[FlowId, int]:
        """
        Count users per flow.
        Args:
            user_to_flow (dict[int, FlowId]): assigment of users to flows
        Returns:
            dict[FlowId, int]: count per flow
        """
        flow_to_user: dict[FlowId, list[int]] = defaultdict(list)
        for user, flow in user_to_flow.items():
            flow_to_user[flow].append(user)

        return {flow: len(users) for flow, users in flow_to_user.items()}

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
        for flow in flows:
            if flow.id not in counts:
                counts[flow.id] = 0
        return counts


class CounterFilter(ABC):
    @abstractmethod
    def filter(self, events: list[Event]) -> list[Event]:
        pass


class FilteredCounter(TrafficCounter):
    def __init__(self, filter: CounterFilter, counter: TrafficCounter) -> None:
        self._filter = filter
        self._counter = counter

    def count(self, events: list[Event], flows: list[Flow]) -> dict[FlowId, int]:
        filtered_events = self._filter.filter(events)
        return self._counter.count(filtered_events, flows)
