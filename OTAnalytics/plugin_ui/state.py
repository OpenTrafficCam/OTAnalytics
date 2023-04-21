from customtkinter import CTkBaseClass, CTkFrame


class StateChanger:
    def __init__(self) -> None:
        self._initial_widget_states: dict[CTkBaseClass, str] = {}

    def _get_initial_state(self, widget: CTkBaseClass) -> None:
        self._initial_widget_states[widget] = widget.cget("state")

    def reset_states(self) -> None:
        for widget, initial_state in self._initial_widget_states.items():
            widget.configure(state=initial_state)

    def disable_frames(self, frames: list[CTkFrame]) -> None:
        for frame in frames:
            for child in frame.winfo_children():
                self._get_initial_state(widget=child)
                child.configure(state="disabled")

    def enable_frames(self, frames: list[CTkFrame]) -> None:
        for frame in frames:
            for child in frame.winfo_children():
                self._get_initial_state(widget=child)
                child.configure(state="enabled")
