from abc import ABC, abstractmethod


class MessageBox(ABC):
    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def update_message(self, message: str) -> None:
        pass
