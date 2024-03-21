from abc import ABC, abstractmethod


class AbstractButtonQuickSaveConfig(ABC):

    @abstractmethod
    def set_state_changed_color(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_default_color(self) -> None:
        raise NotImplementedError
