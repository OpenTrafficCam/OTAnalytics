from unittest.mock import Mock

import pytest

from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import (
    AREA,
    COORDINATES,
    END,
    ID,
    LINE,
    START,
    TYPE,
    Area,
    LineSection,
    SectionRepository,
)


class TestLineSection:
    def test_coordinates_define_point_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            LineSection("N", Coordinate(0, 0), Coordinate(0, 0))

    def test_valid_line_section(self) -> None:
        LineSection("N", Coordinate(0, 0), Coordinate(1, 0))

    def test_to_dict(self) -> None:
        section_id = "some"
        start = Coordinate(0, 0)
        end = Coordinate(1, 1)
        section = LineSection(id=section_id, start=start, end=end)

        section_dict = section.to_dict()

        assert section_dict == {
            TYPE: LINE,
            ID: section_id,
            START: start.to_dict(),
            END: end.to_dict(),
        }


class TestAreaSection:
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

    def test_to_dict(self) -> None:
        section_id = "some"
        first = Coordinate(0, 0)
        second = Coordinate(1, 0)
        third = Coordinate(1, 1)
        forth = Coordinate(0, 0)
        section = Area(id=section_id, coordinates=[first, second, third, forth])

        section_dict = section.to_dict()

        assert section_dict == {
            TYPE: AREA,
            ID: section_id,
            COORDINATES: [
                first.to_dict(),
                second.to_dict(),
                third.to_dict(),
                forth.to_dict(),
            ],
        }


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
