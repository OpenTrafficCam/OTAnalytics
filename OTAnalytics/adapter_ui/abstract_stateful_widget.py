from abc import abstractmethod


class AbstractStatefulWidget:
    @abstractmethod
    def _introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def activate(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def deactivate(self) -> None:
        raise NotImplementedError
