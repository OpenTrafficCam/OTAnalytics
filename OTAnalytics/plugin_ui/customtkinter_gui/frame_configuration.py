import tkinter
from typing import Any

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import CustomCTkTabview
from OTAnalytics.plugin_ui.customtkinter_gui.frame_flows import FrameFlows
from OTAnalytics.plugin_ui.customtkinter_gui.frame_sections import FrameSections


class TabviewConfiguration(CustomCTkTabview):
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
        self.frame_sections.pack(fill=tkinter.BOTH, expand=True)
        self.frame_flows.pack(fill=tkinter.BOTH, expand=True)
        self.set(self.SECTIONS)
