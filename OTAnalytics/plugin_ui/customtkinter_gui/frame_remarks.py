import tkinter as tk
from typing import Any

from customtkinter import CTkTextbox

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame


class FrameRemarks(AbstractCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any):
        super().__init__(**kwargs)

        self.viewmodel = viewmodel  # Store the ViewModel for data binding
        self.create_widgets()
        self.introduce_to_viewmodel()

    def create_widgets(self) -> None:
        self.text_remarks = CTkTextbox(self, wrap=tk.WORD, height=10, width=30)
        self.text_remarks.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    def introduce_to_viewmodel(self) -> None:
        self.viewmodel.set_remark_frame(self)

    def load_remark(self) -> None:
        self.text_remarks.delete("1.0", tk.END)
        remark = "No Comment"
        if self.viewmodel.get_remark():
            remark = self.viewmodel.get_remark()
        self.text_remarks.insert(tk.INSERT, remark)
