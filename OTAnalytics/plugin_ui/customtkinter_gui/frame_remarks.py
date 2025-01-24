import tkinter as tk
from typing import Any

from OTAnalytics.adapter_ui.view_model import ViewModel


class FrameRemarks(tk.Frame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any):
        super().__init__(**kwargs)

        self.viewmodel = viewmodel  # Store the ViewModel for data binding
        self.create_widgets()

    def create_widgets(self) -> None:

        # Create a text box for remarks
        self.text_remarks = tk.Text(self, wrap=tk.WORD, height=10, width=40)
        self.text_remarks.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
