from typing import Any

from customtkinter import CTkTabview


class EmbeddedTabview(CTkTabview):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(border_width=0, **kwargs)
        self._override_fg_color()

    def _override_fg_color(self) -> None:
        """
        Overrides the foreground color to match the foreground color of the master.
        """
        self.configure(fg_color=self.master._fg_color, require_redraw=True)

    def _set_grid_tab_by_name(self, name: str) -> None:
        """
        Overrides the _set_grid_tab_by_name method of CTkTabview by not taking into
        account the corner_radius for padding of the tab content frames.

        Resulting tabview tabs do not have inner padding.
        """
        self._tab_dict[name].grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=self._apply_widget_scaling(self._border_width),
            pady=self._apply_widget_scaling(self._border_width),
        )
