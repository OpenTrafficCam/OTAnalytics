from typing import Iterable

from OTAnalytics.domain.section import Section, SectionId, SectionRepository


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


class ClearAllSections:
    """Clear the section repository.

    Args:
        section_repository: the section repository to be cleared.
    """

    def __init__(self, section_repository: SectionRepository):
        self._section_repository = section_repository

    def __call__(self) -> None:
        self._section_repository.clear()
