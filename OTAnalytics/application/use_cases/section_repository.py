from typing import Iterable

from OTAnalytics.application.config import CLI_CUTTING_SECTION_MARKER
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    Section,
    SectionId,
    SectionRepository,
    SectionType,
)
from OTAnalytics.domain.types import EventType


class SectionAlreadyExists(Exception):
    pass


class SectionIdAlreadyExists(Exception):
    pass


class GetAllSections:
    """Get all sections from the repository."""

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self) -> list[Section]:
        return self._section_repository.get_all()


class GetCuttingSections:
    """Get all cutting sections from the repository."""

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self) -> list[Section]:
        cutting_sections = sorted(
            [
                section
                for section in self._section_repository.get_all()
                if section.get_type() == SectionType.CUTTING
                or section.name.startswith(CLI_CUTTING_SECTION_MARKER)
            ],
            key=lambda section: section.id.id,
        )
        return cutting_sections


class GetSectionsById:
    """Get sections by their id.

    Args:
        section_repository (SectionRepository): the section repository.
    """

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self, ids: Iterable[SectionId]) -> list[Section]:
        """Get sections by their id.

        Args:
            ids (Iterable[SectionId]): the ids to get sections from the repository.

        Returns:
            set[Section]: sections matching the ids. Otherwise, empty set.
        """
        return [
            section
            for section_id in ids
            if (section := self._section_repository.get(section_id)) is not None
        ]


class AddSection:
    """
    Add a single section to the repository.

    Args:
        section_repository (SectionRepository): the section repository to add the
            section to.
    """

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self, section: Section) -> None:
        """Adds section to the section repository.

        Raises:
            SectionAlreadyExists: if section name already exists in repository.
            SectionIdAlreadyExists: if section id already exists in repository.

        Args:
            section (Section): the section to be added.
        """
        if not self.is_section_name_valid(section.name):
            raise SectionAlreadyExists(
                f"A section with the name {section.name} already exists. "
                "Choose another name."
            )
        if not self.is_section_id_valid(section.id):
            raise SectionIdAlreadyExists(
                f"A section with id {section.id} already exists."
            )
        self._section_repository.add(section)

    def is_section_name_valid(self, section_name: str) -> bool:
        if not section_name:
            return False
        return all(
            stored_section.name != section_name
            for stored_section in self._section_repository.get_all()
        )

    def is_section_id_valid(self, section_id: SectionId) -> bool:
        return not (section_id in self._section_repository.get_section_ids())


class AddAllSections:
    def __init__(self, add_section: AddSection) -> None:
        self._add_section = add_section

    def add(self, sections: Iterable[Section]) -> None:
        for section in sections:
            self._add_section(section)


class ClearAllSections:
    """Clear the section repository.

    Args:
        section_repository: the section repository to be cleared.
    """

    def __init__(self, section_repository: SectionRepository):
        self._section_repository = section_repository

    def __call__(self) -> None:
        self._section_repository.clear()


class SectionDoesNotExistError(Exception):
    pass


class RemoveSection:
    """Use case to remove a section from the section repository.

    Args:
        section_repository: the repository to remove the section from.
    """

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self, section_id: SectionId) -> None:
        """Remove section from section repository.

        Raises:
            SectionDoesNotExistError: if section with passed id does not exist.

        Args:
            section_id (SectionId): the id of the section to be removed.
        """
        try:
            self._section_repository.remove(section_id)
        except KeyError:
            raise SectionDoesNotExistError(
                f"Trying to remove a non-existing section with id='{section_id}'."
            )


class GetSectionOffset:
    """Get section offset by event type."""

    def __init__(self, get_sections_by_id: GetSectionsById):
        self._get_sections_by_id = get_sections_by_id

    def get(
        self, section_id: SectionId, event_type: EventType
    ) -> RelativeOffsetCoordinate | None:
        """Get section offset by event type.

        Args:
            section_id: the section id.
            event_type: the event type.

        Returns:
            RelativeOffsetCoordinate | None: The offset if section exists.
                Otherwise, None.
        """
        sections = self._get_sections_by_id([section_id])
        if not sections:
            return None
        return sections[0].get_offset(event_type)
