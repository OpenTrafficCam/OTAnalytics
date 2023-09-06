from abc import ABC, abstractmethod

from OTAnalytics.domain.section import COORDINATES, Section


class SectionRefPointCalculator(ABC):
    def coordinates_from_section(self, section: Section) -> list[tuple[int, int]]:
        coordinates_dicts = section.to_dict()[COORDINATES]
        return [(d["x"], d["y"]) for d in coordinates_dicts]

    @abstractmethod
    def get_reference_point(self, section: Section) -> tuple[float, float]:
        """
        Calculates a reference point on a section.
        Raises:
            NotImplementedError: If derived classes have not implemented this method
        Returns:
            tuple[float, float]: Reference point
        """
        raise NotImplementedError


class InnerSegmentsCenterCalculator(SectionRefPointCalculator):
    def get_reference_point(self, section: Section) -> tuple[float, float]:
        coordinates = self.coordinates_from_section(section)
        num_coordinates = len(coordinates)
        if num_coordinates == 0:
            raise ValueError("LineSection has no coordinates")
        if num_coordinates % 2 == 0:
            # Calculate center between innermost two points
            innermost_coordinates = coordinates[
                num_coordinates // 2 - 1 : num_coordinates // 2 + 1
            ]
            center_x = (innermost_coordinates[0][0] + innermost_coordinates[1][0]) / 2
            center_y = (innermost_coordinates[0][1] + innermost_coordinates[1][1]) / 2
        else:
            # Calculate innermost point
            innermost_coordinate_index = len(coordinates) // 2
            center_x, center_y = coordinates[innermost_coordinate_index]
        return center_x, center_y


class GeometricCenterCalculator(SectionRefPointCalculator):
    def get_reference_point(self, section: Section) -> tuple[float, float]:
        coordinates = self.coordinates_from_section(section)
        total_x = 0
        total_y = 0
        num_points = len(coordinates)
        for x, y in coordinates:
            total_x += x
            total_y += y
        center_x = total_x / num_points
        center_y = total_y / num_points
        return center_x, center_y
