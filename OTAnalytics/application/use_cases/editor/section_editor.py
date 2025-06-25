import contextlib
from typing import Awaitable, Callable

from OTAnalytics.application.application import CancelAddSection
from OTAnalytics.application.use_cases.section_repository import AddSection
from OTAnalytics.domain import geometry
from OTAnalytics.domain.geometry import coordinate_from_tuple
from OTAnalytics.domain.section import (
    ID,
    NAME,
    RELATIVE_OFFSET_COORDINATES,
    Area,
    LineSection,
    MissingSection,
    Section,
    SectionId,
    SectionRepository,
)
from OTAnalytics.domain.types import EventType

MetadataProvider = Callable[[], Awaitable[dict]]


class MissingCoordinate(Exception):
    pass


def validate_coordinates(coordinates: list[tuple[int, int]]) -> None:
    if not coordinates:
        raise MissingCoordinate("First coordinate is missing")
    elif len(coordinates) == 1:
        raise MissingCoordinate("Second coordinate is missing")


def validate_section_information(
    meta_data: dict, coordinates: list[tuple[int, int]]
) -> None:
    validate_coordinates(coordinates)
    if not meta_data:
        raise ValueError("Metadata of line_section are not defined")


class CreateSectionId:
    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def create_id(self) -> SectionId:
        return self._section_repository.get_id()


class AddNewSection:
    def __init__(self, create_section_id: CreateSectionId, add_section: AddSection):
        self._create_section_id = create_section_id
        self._add_section = add_section

    async def add_new_section(
        self,
        coordinates: list[tuple[int, int]],
        is_area_section: bool,
        get_metadata: MetadataProvider,
    ) -> Section | None:
        validate_coordinates(coordinates)
        with contextlib.suppress(CancelAddSection):
            return await self.__create_section(
                coordinates, is_area_section, get_metadata
            )
        return None

    async def __create_section(
        self,
        coordinates: list[tuple[int, int]],
        is_area_section: bool,
        get_metadata: MetadataProvider,
    ) -> Section:
        metadata = await self.__get_metadata(get_metadata)
        relative_offset_coordinates_enter = metadata[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ]
        section: Section | None = None
        if is_area_section:
            section = Area(
                id=self._create_section_id.create_id(),
                name=metadata[NAME],
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: geometry.RelativeOffsetCoordinate(
                        **relative_offset_coordinates_enter
                    )
                },
                plugin_data={},
                coordinates=await self._build_area_coordinates(coordinates),
            )
        else:
            section = LineSection(
                id=self._create_section_id.create_id(),
                name=metadata[NAME],
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: geometry.RelativeOffsetCoordinate(
                        **relative_offset_coordinates_enter
                    )
                },
                plugin_data={},
                coordinates=await self._build_coordinates(coordinates),
            )
        if section is None:
            raise TypeError("section has to be LineSection or Area, but is None")
        self._add_section(section)
        return section

    async def _build_area_coordinates(
        self, coordinates: list[tuple[int, int]]
    ) -> list[geometry.Coordinate]:
        if coordinates[-1] != coordinates[0]:
            return await self._build_coordinates(coordinates + coordinates[0:1])
        return await self._build_coordinates(coordinates)

    async def _build_coordinates(
        self, coordinates: list[tuple[int, int]]
    ) -> list[geometry.Coordinate]:
        return [coordinate_from_tuple(coordinate) for coordinate in coordinates]

    async def __get_metadata(self, get_metadata: MetadataProvider) -> dict:
        metadata = await get_metadata()
        while (
            (not metadata)
            or (NAME not in metadata)
            or (not self._add_section.is_section_name_valid(metadata[NAME]))
            or (RELATIVE_OFFSET_COORDINATES not in metadata)
        ):
            metadata = await get_metadata()
        return metadata


class UpdateSectionCoordinates:
    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def update(self, meta_data: dict, coordinates: list[tuple[int, int]]) -> SectionId:
        validate_section_information(meta_data, coordinates)
        section_id = SectionId(meta_data[ID])
        if not (section := self._section_repository.get(section_id)):
            raise MissingSection(
                f"Could not update section '{section_id.serialize()}' after editing"
            )
        section.update_coordinates(
            [coordinate_from_tuple(coordinate) for coordinate in coordinates]
        )
        self._section_repository.update(section)
        return section_id
