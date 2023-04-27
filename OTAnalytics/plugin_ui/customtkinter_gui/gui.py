import customtkinter
from customtkinter import CTk

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.frame_analysis import FrameAnalysis
from OTAnalytics.plugin_ui.customtkinter_gui.frame_canvas import FrameCanvas
from OTAnalytics.plugin_ui.customtkinter_gui.frame_sections import FrameSections
from OTAnalytics.plugin_ui.customtkinter_gui.frame_tracks import TracksFrame


class OTAnalyticsGui:
    def __init__(
        self,
        view_model: ViewModel,
        app: CTk = CTk(),
    ) -> None:
        self._view_model = view_model
        self._app: CTk = app

    def start(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")

        self._app.title("OTAnalytics")

        self._get_widgets()
        self._place_widgets()
        self._app.mainloop()

    def _get_widgets(self) -> None:
        self.frame_canvas = FrameCanvas(
            master=self._app,
            viewmodel=self._view_model,
        )
        self.frame_tracks = TracksFrame(
            master=self._app,
            viewmodel=self._view_model,
        )
        self.frame_sections = FrameSections(
            master=self._app,
            viewmodel=self._view_model,
        )
        self.frame_analysis = FrameAnalysis(
            master=self._app, viewmodel=self._view_model
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.frame_canvas.grid(
            row=0, column=0, rowspan=3, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.frame_tracks.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_sections.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_analysis.grid(row=2, column=1, padx=PADX, pady=PADY, sticky=STICKY)
