from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel, CTkTabview

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.frame_flows import FrameFlows
from OTAnalytics.plugin_ui.customtkinter_gui.frame_sections import FrameSections


class FrameConfiguration(CTkFrame):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Configuration")
        self.tabview = TabviewConfiguration(
            master=self, width=50, viewmodel=self._viewmodel
        )
        self.button_add = CTkButton(
            master=self, text="Load", width=50, command=self._viewmodel.load_sections
        )
        self.button_save = CTkButton(
            master=self, text="Save", width=50, command=self._viewmodel.save_sections
        )

    def _place_widgets(self) -> None:
        self.label.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.tabview.grid(
            row=1, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_add.grid(row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_save.grid(row=2, column=1, padx=PADX, pady=PADY, sticky=STICKY)


class TabviewConfiguration(CTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.SECTIONS: str = "Sections"
        self.FLOWS: str = "Flows"
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.add(self.SECTIONS)
        self.frame_sections = FrameSections(
            master=self.tab(self.SECTIONS), viewmodel=self._viewmodel
        )
        self.add(self.FLOWS)
        self.frame_flows = FrameFlows(
            master=self.tab(self.FLOWS), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_sections.pack()
        self.frame_flows.pack()
        self.set(self.SECTIONS)
