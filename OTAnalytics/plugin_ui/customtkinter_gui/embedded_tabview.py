from typing import Any

from customtkinter import CTkTabview

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADY


class EmbeddedTabview(CTkTabview):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(border_width=0, **kwargs)
        self._override_fg_color()
        self._override_padding_above()

    def _override_padding_above(self) -> None:
        """
        Overrides the minimum size of the dummy row above the tabview to prevent
        padding.
        """
        self.grid_rowconfigure(0, weight=0, minsize=0)

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

    def _set_grid_segmented_button(self) -> None:
        """needs to be called for changes in corner_radius"""
        self._segmented_button.grid(
            row=1,
            rowspan=2,
            column=0,
            columnspan=1,
            padx=self._apply_widget_scaling(self._corner_radius),
            pady=PADY,
            sticky="ns",
        )
