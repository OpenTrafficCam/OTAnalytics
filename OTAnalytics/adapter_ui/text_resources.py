from dataclasses import dataclass
from typing import Iterator

COLUMN_NAME = "column_name"


@dataclass(frozen=True, order=True)
class ColumnResource:
    """
    Represents a row in a treeview with an id and a dict of values to be shown.
    The dicts keys represent the columns and the values represent the cell values.
    """

    id: str
    values: dict[str, str]


class ColumnResources:
    def __init__(
        self, resources: list[ColumnResource], lookup_column: str = COLUMN_NAME
    ) -> None:
        self._resources = resources
        self._lookup_column = lookup_column
        self._to_id = self._create_to_id(resources)
        self._to_name = self._create_to_name(resources)

    def _create_to_id(self, resources: list[ColumnResource]) -> dict[str, str]:
        return {
            resource.values[self._lookup_column]: resource.id for resource in resources
        }

    def _create_to_name(self, resources: list[ColumnResource]) -> dict[str, str]:
        return {
            resource.id: resource.values[self._lookup_column] for resource in resources
        }

    @property
    def names(self) -> list[str]:
        return [resource.values[self._lookup_column] for resource in self._resources]

    def get_name_for(self, resource_id: str) -> str:
        return self._to_name.get(resource_id, "")

    def get_id_for(self, name: str) -> str:
        return self._to_id.get(name, "")

    def has(self, resource_id: str) -> bool:
        return resource_id in [resource.id for resource in self._resources]

    def __iter__(self) -> Iterator[ColumnResource]:
        return self._resources.__iter__()
