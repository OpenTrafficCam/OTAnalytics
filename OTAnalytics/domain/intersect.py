from abc import ABC, abstractmethod
from typing import Callable, Iterable, Sequence

from OTAnalytics.domain.event import Event, EventBuilder
from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset


class IntersectImplementation(ABC):
    @abstractmethod
    def line_intersects_line(self, line_1: Line, line_2: Line) -> bool:
        """Checks if a line intersects with another line.

        Args:
            line_1 (Line): the line to be intersected.
            line_2 (Line): the other line to be intersected.

        Returns:
            bool: `True` if the lines intersect with other. Otherwise `False`.
        """
        pass

    @abstractmethod
    def line_intersects_polygon(self, line: Line, polygon: Polygon) -> bool:
        """Checks if a line intersects with a polygon.

        Args:
            line (Line): the line to be intersected.
            polygon (Polygon): the polygon to be intersected.

        Returns:
            bool: `True` if the line and polygon intersect with each other.
                `Otherwise `False`.
        """
        pass

    @abstractmethod
    def split_line_with_line(self, line: Line, splitter: Line) -> list[Line]:
        """Splits a line with the help of another line and returns a list of lines.

        If `line` intersects `splitter` then line_1 will be splitted at the
        intersection points.
        I.e. Let line_1 = [p_1, p_2, ..., p_n], n a natural number and p_x
        the intersection point.

        Then `line` will be splitted as follows:
        [[p_1, p_2, ..., p_x], [p_x, p_(x+1), ..., p_n].

        Args:
            line (Line): the line to be splitted.
            splitter (Line): the line used for the splitting.

        Returns:
            Optional[list[Line]]: The splitted lines.
        """
        pass

    @abstractmethod
    def distance_between(
        self, coordinate_1: Coordinate, coordinate_2: Coordinate
    ) -> float:
        """Returns the distance between two coordinates.

        Args:
            coordinate_1 (Coordinate): the first coordinate
            coordinate_2 (Coordinate): the second coordinate

        Returns:
            float: the distance
        """
        pass

    @abstractmethod
    def are_coordinates_within_polygon(
        self, coordinates: list[Coordinate], polygon: Polygon
    ) -> list[bool]:
        """Checks if coordinates are within a polygon.

        A coordinate is within a polygon if it is enclosed by it. Meaning that a point
        sitting on the boundary of a polygon is treated as not being within it.

        Args:
            coordinates (list[Coordinate]): the coordinates to check if they are
                contained by the polygon
            polygon (Polygon): the polygon

        Returns:
            list[bool]: the boolean mask holding information whether a point is within
                a polygon or not
        """
        pass


class IntersectParallelizationStrategy(ABC):
    @property
    @abstractmethod
    def num_processes(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        intersect: Callable[[TrackDataset, Iterable[Section]], Iterable[Event]],
        tasks: Sequence[tuple[TrackDataset, Iterable[Section]]],
    ) -> list[Event]:
        """Executes the intersection of tracks with sections with the implemented
        parallelization strategy.

        Args:
            intersect (Callable[[TrackDataset, Iterable[Section]], Iterable[Event]]):
                the function to be executed on an iterable of tracks and sections.
            tasks (Sequence[tuple[TrackDataset, Iterable[Section]]): the argument
                to intersect function.

        Returns:
            Iterable[Event]: the generated events.
        """
        raise NotImplementedError

    @abstractmethod
    def set_num_processes(self, value: int) -> None:
        """Set number of processes to run intersection in parallel.

        Args:
            value: the number of processes to run in parallel.
        """
        raise NotImplementedError


class Intersector(ABC):
    """
    Defines an interface to implement a family of algorithms to intersect tracks
    with sections.
    """

    @abstractmethod
    def intersect(
        self,
        track_dataset: TrackDataset,
        sections: Iterable[Section],
        event_builder: EventBuilder,
    ) -> list[Event]:
        """Intersect tracks with sections and generate events if they intersect.

        Args:
            track_dataset (TrackDataset): the tracks to be intersected with.
            sections (Iterable[Section]): the sections to be intersected with.
            event_builder (EventBuilder): builder to generate events

        Returns:
            list[Event]: the events if the track intersects with the sections.
                Otherwise, return empty list.
        """
        raise NotImplementedError
