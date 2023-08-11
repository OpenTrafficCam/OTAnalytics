from typing import Iterable

from OTAnalytics.domain.section import Section, SectionId, SectionRepository


class SectionAlreadyExists(Exception):
    pass


class GetAllSections:
    """Get all sections from the repository."""

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self) -> list[Section]:
        return self._section_repository.get_all()


class GetSectionsById:
    """Get sections by their id.

    Args:
        section_repository (SectionRepository): the section repository.
    """

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self, ids: Iterable[SectionId]) -> set[Section]:
        """Get sections by their id.

        Args:
            ids (Iterable[SectionId]): the ids to get sections from the repository.

        Returns:
            set[Section]: sections matching the ids. Otherwise, empty set.
        """
        return {
            section
            for section_id in ids
            if (section := self._section_repository.get(section_id)) is not None
        }


class AddSection:
    """
    Add a single section to the repository.
    """

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def add(self, section: Section) -> None:
        if not self.is_section_name_valid(section.name):
            raise SectionAlreadyExists(
                f"A section with the name {section.name} already exists. "
                "Choose another name."
            )
        self._section_repository.add(section)

    def is_section_name_valid(self, section_name: str) -> bool:
        if not section_name:
            return False
        return all(
            stored_section.name != section_name
            for stored_section in self._section_repository.get_all()
        )
