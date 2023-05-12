from abc import abstractmethod

from customtkinter import CTkFrame


class AbstractFrameTracks(CTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        pass
