from abc import ABC, abstractmethod

from customtkinter import CTkButton

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"


class AbstractFrame(ABC):
    def set_enabled(self, enabled: bool) -> None:
        new_state = STATE_NORMAL if enabled else STATE_DISABLED
        for button in self.action_buttons():
            button.configure(state=new_state)

    @abstractmethod
    def action_buttons(self) -> list[CTkButton]:
        pass
