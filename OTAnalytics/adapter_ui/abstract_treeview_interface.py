from abc import abstractmethod


class AbstractTreeviewInterface:
    # TODO: add property viewmodel

    @abstractmethod
    def _introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_items(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_selected_items(self, item_ids: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        raise NotImplementedError
