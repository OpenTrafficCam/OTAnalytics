from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class DataclassValidation(ABC):
    """Abstract class extending a `dataclass` with a hook method called
    `self._validate` to put in all validation logic of the classes attribute.

    This `dataclass` will call the `self._validate` hook in the `self.__post_init__`
    method.

    """

    def __post_init__(self) -> None:
        """Validate attributes.

        Will be called after `__init__`.
        """
        self._validate()

    def _validate(self) -> None:
        """Hook to put in attribute validation logic.

        It will be called in the __post_init__ method.
        """
        pass
