from abc import ABC, abstractmethod


class NumberOfTracksToBeValidated(ABC):
    @abstractmethod
    def calculate(self) -> int:
        raise NotImplementedError
