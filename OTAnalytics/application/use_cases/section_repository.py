from OTAnalytics.domain.section import Section, SectionRepository


class SectionAlreadyExists(Exception):
    pass


class GetAllSections:
    """Get all sections from the repository."""

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def __call__(self) -> list[Section]:
        return self._section_repository.get_all()


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
