from abc import ABC, abstractmethod
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.message_box import MessageBox


class UiFactory(ABC):

    @abstractmethod
    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        pass

    @abstractmethod
    def askopenfilename(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
    ) -> str:
        pass

    @abstractmethod
    def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        pass
