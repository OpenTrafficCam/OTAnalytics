from unittest.mock import Mock

import pytest

from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import Area, LineSection, SectionRepository


class TestLineSection:
    def test_coordinates_define_point_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            LineSection("N", Coordinate(0, 0), Coordinate(0, 0))

    def test_valid_line_section(self) -> None:
        LineSection("N", Coordinate(0, 0), Coordinate(1, 0))


class TestArea:
    def test_coordinates_define_point_raises_value_error(self) -> None:
        coordinates = [Coordinate(0, 0), Coordinate(0, 0)]
        with pytest.raises(ValueError):
            Area("N", coordinates)

    def test_insufficient_coordinates_raises_value_error(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        with pytest.raises(ValueError):
            Area("N", coordinates)

    def test_valid_area(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        area = Area("N", coordinates)

        assert area.id == "N"
        assert area.coordinates == coordinates


class TestSectionRepository:
    def test_add(self) -> None:
        section = Mock()
        repository = SectionRepository()

        repository.add(section)

        assert section in repository.get_all()

    def test_add_all(self) -> None:
        first_section = Mock()
        second_section = Mock()
        repository = SectionRepository()

        repository.add_all([first_section, second_section])

        assert first_section in repository.get_all()
        assert second_section in repository.get_all()

    def test_remove(self) -> None:
        first_section = Mock()
        second_section = Mock()
        repository = SectionRepository()
        repository.add_all([first_section, second_section])

        repository.remove(first_section)

        assert first_section not in repository.get_all()
        assert second_section in repository.get_all()
