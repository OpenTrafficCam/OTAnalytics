import tkinter
from typing import Any, Protocol

from customtkinter import CTkFrame, CTkScrollableFrame, CTkTabview

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADY


class EmbeddedCTkFrame(CTkFrame):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            border_width=0,
            corner_radius=0,
            fg_color="transparent",
            bg_color="transparent",
            **kwargs,
        )


class EmbeddedCTkScrollableFrame(CTkScrollableFrame):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            border_width=0,
            corner_radius=0,
            fg_color="transparent",
            bg_color="transparent",
            **kwargs,
        )


class CustomCTkTabview(CTkTabview):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(border_width=0, height=10, **kwargs)
        self.set_fg_color_as_segmented_button_color()
        self._configure_grid()

    def set_fg_color_as_segmented_button_color(self) -> None:
        """
        Sets the color of the segmented button to the same color as the whole Tabview.
        """
        self.configure(segmented_button_fg_color=self.cget("fg_color"))

    def disable_segmented_button(self) -> None:
        """
        Disables the segmented button. No response will be shown if user hovers it.
        Should be used when CustomCTkTabview is used as a Frame with segmented button
        as header.
        """
        segmented_button_fg_color = self._segmented_button.cget("fg_color")
        self.configure(segmented_button_selected_color=segmented_button_fg_color)
        self.configure(
            segmented_button_unselected_hover_color=segmented_button_fg_color
        )
        self.configure(segmented_button_selected_hover_color=segmented_button_fg_color)
        text_color = self._segmented_button.cget("text_color")
        self.configure(text_color_disabled=text_color)
        self._segmented_button.configure(state="disabled")

    def _configure_grid(self) -> None:
        """create 3 x 4 grid system"""

        self.grid_rowconfigure(0, weight=0, minsize=0)
        self.grid_rowconfigure(
            1,
            weight=0,
            minsize=self._apply_widget_scaling(self._outer_button_overhang),
        )
        self.grid_rowconfigure(
            2,
            weight=0,
            minsize=self._apply_widget_scaling(
                self._button_height - self._outer_button_overhang
            ),
        )
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0, minsize=7)
        self.grid_columnconfigure(0, weight=1)


class FrameFactory(Protocol):
    def __call__(self, **kwargs: Any) -> CTkFrame:
        raise NotImplementedError


class SingleFrameTabview(CustomCTkTabview):
    def __init__(
        self,
        frame_factory: FrameFactory,
        title: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._frame_factory = frame_factory
        self._title = title
        self._get_widgets()
        self._place_widgets()
        self.disable_segmented_button()

    def _get_widgets(self) -> None:
        self.add(self._title)
        self.frame = self._frame_factory(master=self.tab(self._title))

    def _place_widgets(self) -> None:
        self.frame.pack(fill=tkinter.BOTH, expand=True)
        self.set(self._title)


class CTkEmbeddedTabview(CTkTabview):
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
