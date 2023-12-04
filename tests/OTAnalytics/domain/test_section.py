from unittest.mock import Mock, call

import pytest

from OTAnalytics.domain.event import EventType
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate, X, Y
from OTAnalytics.domain.section import (
    COORDINATES,
    ID,
    NAME,
    PLUGIN_DATA,
    RELATIVE_OFFSET_COORDINATES,
    TYPE,
    Area,
    LineSection,
    Section,
    SectionChangedObserver,
    SectionId,
    SectionListObserver,
    SectionListSubject,
    SectionRepository,
    SectionRepositoryEvent,
    SectionType,
)


class TestSectionListSubject:
    def test_notify_observer(self) -> None:
        changed_tracks = [SectionId("north"), SectionId("south")]
        observer = Mock(spec=SectionListObserver)
        subject = SectionListSubject()
        subject.register(observer)

        event = SectionRepositoryEvent.create_added(changed_tracks)
        subject.notify(event)

        observer.notify_sections.assert_called_with(event)


class TestSection:
    @pytest.fixture
    def section_north(self) -> Section:
        plugin_data: dict = {"key_1": "some data", "key_2": "some data"}
        id = "North"
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        return Area(
            id=SectionId(id),
            name=id,
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.5, 0.5)
            },
            plugin_data=plugin_data,
            coordinates=coordinates,
        )

    def test_get_offset(self, section_north: Section) -> None:
        assert section_north.get_offset(
            EventType.SECTION_ENTER
        ) == RelativeOffsetCoordinate(0.5, 0.5)
        assert section_north.get_offset(
            EventType.ENTER_SCENE
        ) == RelativeOffsetCoordinate(0, 0)


class TestLineSection:
    def test_coordinates_define_point_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            LineSection(
                id=SectionId("N"),
                name="N",
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
                },
                plugin_data={},
                coordinates=[Coordinate(0, 0), Coordinate(0, 0)],
            )

    def test_valid_line_section(self) -> None:
        LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(0, 0), Coordinate(1, 0)],
        )

    def test_update_coordinates(self) -> None:
        section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(0, 0), Coordinate(1, 0)],
        )

        new_coordinates = [Coordinate(1, 1), Coordinate(2, 2)]
        section.update_coordinates(new_coordinates)

        assert section.get_coordinates() == new_coordinates

    @pytest.mark.parametrize(
        "new_coordinates", [[Coordinate(1, 1)], [Coordinate(1, 1), Coordinate(1, 1)]]
    )
    def test_update_with_bad_coordinates(
        self, new_coordinates: list[Coordinate]
    ) -> None:
        section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(0, 0), Coordinate(1, 0)],
        )

        with pytest.raises(ValueError):
            section.update_coordinates(new_coordinates)

    def test_to_dict(self) -> None:
        section_id = SectionId("some")
        start = Coordinate(0, 0)
        end = Coordinate(1, 1)
        coordinates = [start, end]
        section = LineSection(
            id=section_id,
            name="some",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=coordinates,
        )

        section_dict = section.to_dict()

        assert section_dict == {
            TYPE: SectionType.LINE.value,
            ID: section_id.id,
            NAME: section.name,
            RELATIVE_OFFSET_COORDINATES: {
                EventType.SECTION_ENTER.serialize(): {X: 0, Y: 0}
            },
            COORDINATES: [coordinate.to_dict() for coordinate in coordinates],
            PLUGIN_DATA: {},
        }

    def test_initialization_with_plugin_data(self) -> None:
        plugin_data: dict = {"key_1": "some data", "key_2": "some data"}
        id = "N"
        start = Coordinate(0, 0)
        end = Coordinate(10, 10)
        coordinates = [start, end]
        line = LineSection(
            id=SectionId(id),
            name=id,
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data=plugin_data,
            coordinates=coordinates,
        )
        assert line.id == SectionId(id)
        assert line.plugin_data == plugin_data
        assert line.coordinates == coordinates


class TestAreaSection:
    def test_coordinates_define_point_raises_value_error(self) -> None:
        coordinates = [Coordinate(0, 0), Coordinate(0, 0)]
        with pytest.raises(ValueError):
            Area(
                id=SectionId("N"),
                name="N",
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
                },
                plugin_data={},
                coordinates=coordinates,
            )

    def test_insufficient_coordinates_raises_value_error(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        with pytest.raises(ValueError):
            Area(
                id=SectionId("N"),
                name="N",
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
                },
                plugin_data={},
                coordinates=coordinates,
            )

    def test_valid_area(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        area = Area(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=coordinates,
        )

        assert area.id == SectionId("N")
        assert area.coordinates == coordinates

    def test_update_coordinates(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        area = Area(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=coordinates,
        )

        new_coordinates = [
            Coordinate(1, 1),
            Coordinate(2, 2),
            Coordinate(3, 3),
            Coordinate(1, 1),
        ]
        area.update_coordinates(new_coordinates)

        assert area.get_coordinates() == new_coordinates

    @pytest.mark.parametrize(
        "new_coordinates",
        [
            [Coordinate(1, 1), Coordinate(2, 2), Coordinate(3, 3), Coordinate(4, 4)],
            [Coordinate(1, 1), Coordinate(2, 2), Coordinate(1, 1)],
        ],
    )
    def test_update_with_bad_coordinates(
        self, new_coordinates: list[Coordinate]
    ) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        area = Area(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=coordinates,
        )

        with pytest.raises(ValueError):
            area.update_coordinates(new_coordinates)

    def test_to_dict(self) -> None:
        section_id = SectionId("some")
        first = Coordinate(0, 0)
        second = Coordinate(1, 0)
        third = Coordinate(1, 1)
        forth = Coordinate(0, 0)
        section = Area(
            id=section_id,
            name="some",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[first, second, third, forth],
        )

        section_dict = section.to_dict()

        assert section_dict == {
            TYPE: SectionType.AREA.value,
            ID: section_id.id,
            NAME: section.name,
            RELATIVE_OFFSET_COORDINATES: {
                EventType.SECTION_ENTER.serialize(): {X: 0, Y: 0}
            },
            COORDINATES: [
                first.to_dict(),
                second.to_dict(),
                third.to_dict(),
                forth.to_dict(),
            ],
            PLUGIN_DATA: {},
        }

    def test_initialization_with_plugin_data(self) -> None:
        plugin_data: dict = {"key_1": "some data", "key_2": "some data"}
        id = "N"
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        line = Area(
            id=SectionId(id),
            name=id,
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data=plugin_data,
            coordinates=coordinates,
        )
        assert line.id == SectionId(id)
        assert line.plugin_data == plugin_data
        assert line.coordinates == coordinates


class TestSectionRepository:
    def test_get_id(self) -> None:
        section = Mock(spec=Section)
        section.id = SectionId("3")
        repository = SectionRepository()
        repository.add(section)

        first_id = repository.get_id()
        second_id = repository.get_id()
        third_id = repository.get_id()

        assert first_id == SectionId("1")
        assert second_id == SectionId("2")
        assert third_id == SectionId("4")

    def test_add(self) -> None:
        section_id = SectionId("north")
        section = Mock()
        section.id = section_id
        observer = Mock(spec=SectionListObserver)
        repository = SectionRepository()
        repository.register_sections_observer(observer)

        repository.add(section)

        assert section in repository.get_all()
        observer.notify_sections.assert_called_with(
            SectionRepositoryEvent.create_added([section_id])
        )

    def test_add_all(self) -> None:
        section_id_north = SectionId("north")
        section_id_south = SectionId("south")
        first_section = Mock()
        first_section.id = section_id_north
        second_section = Mock()
        second_section.id = section_id_south
        observer = Mock(spec=SectionListObserver)
        repository = SectionRepository()
        repository.register_sections_observer(observer)

        repository.add_all([first_section, second_section])

        assert first_section in repository.get_all()
        assert second_section in repository.get_all()
        observer.notify_sections.assert_called_with(
            SectionRepositoryEvent.create_added([section_id_north, section_id_south])
        )

    def test_remove(self) -> None:
        first_section = Mock()
        first_section.id = SectionId("first")
        second_section = Mock()
        second_section.id = SectionId("second")
        observer = Mock(spec=SectionListObserver)
        repository = SectionRepository()
        repository.register_sections_observer(observer)
        repository.add_all([first_section, second_section])

        repository.remove(first_section.id)

        assert first_section not in repository.get_all()
        assert second_section in repository.get_all()
        observer.notify_sections.assert_called_with(
            SectionRepositoryEvent.create_removed([first_section.id])
        )

    def test_update(self) -> None:
        section_id = Mock()
        section_id.id = SectionId("first")
        original_section = Mock(spec=Section)
        original_section.id = section_id
        updated_section = Mock(spec=Section)
        updated_section.id = section_id
        observer = Mock(spec=SectionChangedObserver)
        repository = SectionRepository()
        repository.register_section_changed_observer(observer)

        repository.add(original_section)
        repository.update(updated_section)

        assert repository.get(section_id) is updated_section
        observer.assert_called_once_with(section_id)

    def test_update_section_plugin_data_not_existing(self) -> None:
        section_id = SectionId("my section")
        name = "my section"
        plugin_data = {"some": "new_value"}

        section = LineSection(
            section_id,
            name,
            {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
            {},
            coordinates=[Coordinate(0, 0), Coordinate(10, 10)],
        )

        repository = SectionRepository()

        repository.add(section)
        repository.set_section_plugin_data(
            section_id=section_id,
            plugin_data=plugin_data,
        )

        stored_section = repository.get(section_id)

        assert stored_section == section
        assert section.plugin_data == plugin_data

    def test_update_section_plugin_data_with_existing_data(self) -> None:
        key = "my data for plugins"
        section_id = SectionId("my section")
        old_plugin_data = {"some": "value"}
        new_plugin_data = {"other": "new_value"}

        section = LineSection(
            section_id,
            "my section",
            {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
            {key: old_plugin_data},
            coordinates=[Coordinate(0, 0), Coordinate(10, 10)],
        )

        repository = SectionRepository()
        repository.add(section)
        repository.set_section_plugin_data(
            section_id=section_id,
            plugin_data=new_plugin_data,
        )

        stored_section = repository.get(section_id)

        assert stored_section == section
        assert section.plugin_data == new_plugin_data

    def test_clear(self) -> None:
        section_id_north = SectionId("north")
        section_id_south = SectionId("south")
        first_section = Mock()
        first_section.id = section_id_north
        second_section = Mock()
        second_section.id = section_id_south
        observer = Mock(spec=SectionListObserver)
        repository = SectionRepository()
        repository.register_sections_observer(observer)

        repository.add_all([first_section, second_section])
        repository.clear()

        assert not list(repository.get_all())
        assert observer.notify_sections.call_args_list == [
            call(
                SectionRepositoryEvent.create_added(
                    [section_id_north, section_id_south]
                )
            ),
            call(
                SectionRepositoryEvent.create_removed(
                    [section_id_north, section_id_south]
                )
            ),
        ]

    def test_get_section_ids(self) -> None:
        section_id = SectionId("North")
        section = Mock(spec=Section)
        section.id = section_id

        repository = SectionRepository()
        repository.add(section)
        result = repository.get_section_ids()
        assert list(result) == [section_id]
