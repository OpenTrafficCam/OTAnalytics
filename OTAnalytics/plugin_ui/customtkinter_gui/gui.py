import tkinter
import traceback
from typing import Any, Sequence

from customtkinter import (
    CTk,
    CTkFrame,
    CTkScrollableFrame,
    CTkTabview,
    set_appearance_mode,
    set_default_color_theme,
)

from OTAnalytics.adapter_ui.abstract_main_window import AbstractMainWindow
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.plotting import Layer
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.frame_analysis import FrameAnalysis
from OTAnalytics.plugin_ui.customtkinter_gui.frame_canvas import FrameCanvas
from OTAnalytics.plugin_ui.customtkinter_gui.frame_configuration import (
    FrameConfiguration,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_filter import FrameFilter
from OTAnalytics.plugin_ui.customtkinter_gui.frame_project import FrameProject
from OTAnalytics.plugin_ui.customtkinter_gui.frame_track_plotting import (
    FrameTrackPlotting,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_tracks import TracksFrame
from OTAnalytics.plugin_ui.customtkinter_gui.frame_videos import FrameVideos
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox


class ModifiedCTk(AbstractMainWindow, CTk):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.protocol("WM_DELETE_WINDOW", self._ask_to_close)
        self._viewmodel: ViewModel = viewmodel
        self.introduce_to_viewmodel()

    def _ask_to_close(self) -> None:
        infobox = InfoBox(
            title="Close application",
            message="Do you want to close the application?",
            initial_position=get_widget_position(self),
            show_cancel=True,
        )
        if infobox.canceled:
            return
        self.quit()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_window(self)

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        x, y = get_widget_position(self, offset=offset)
        return x, y

    def report_callback_exception(self, exc: Any, val: Any, tb: Any) -> None:
        traceback.print_exception(val)
        InfoBox(message=str(val), title="Error", initial_position=self.get_position())


class TabviewInputFiles(CTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.TRACKS: str = "Tracks"
        self.VIDEOS: str = "Videos"
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.add(self.TRACKS)
        self.frame_tracks = TracksFrame(
            master=self.tab(self.TRACKS), viewmodel=self._viewmodel
        )
        self.add(self.VIDEOS)
        self.frame_videos = FrameVideos(
            master=self.tab(self.VIDEOS), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_tracks.pack(fill=tkinter.BOTH, expand=True)
        self.frame_videos.pack(fill=tkinter.BOTH, expand=True)
        self.set(self.TRACKS)


class FrameContent(CTkFrame):
    def __init__(
        self, master: Any, viewmodel: ViewModel, layers: Sequence[Layer], **kwargs: Any
    ) -> None:
        super().__init__(master, **kwargs)
        self._viewmodel = viewmodel
        self.ctkscrollableframe = CTkScrollableFrame(
            master=self, orientation="horizontal"
        )
        self.ctkscrollableframe.pack(fill=tkinter.BOTH, expand=True)

        self._frame_track_plotting = FrameTrackPlotting(
            master=self.ctkscrollableframe,
            layers=layers,
        )
        self._frame_filter = FrameFilter(
            master=self.ctkscrollableframe, viewmodel=self._viewmodel
        )
        self._frame_canvas = FrameCanvas(
            master=self.ctkscrollableframe,
            viewmodel=self._viewmodel,
        )
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)
        self._frame_track_plotting.grid(row=0, column=0, pady=PADY, sticky=STICKY)
        self._frame_filter.grid(row=0, column=1, pady=PADY, sticky=STICKY)
        self._frame_canvas.grid(row=1, column=0, columnspan=2, pady=PADY, sticky=STICKY)


class FrameNavigation(CTkFrame):
    def __init__(self, master: Any, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self._frame_project = FrameProject(
            master=self,
            viewmodel=self._viewmodel,
        )
        self._tabview_input_files = TabviewInputFiles(
            master=self, viewmodel=self._viewmodel
        )
        self._tabview_configuration = FrameConfiguration(
            master=self, viewmodel=self._viewmodel
        )
        self._frame_analysis = FrameAnalysis(master=self, viewmodel=self._viewmodel)

    def _place_widgets(self) -> None:
        self.grid_rowconfigure((1, 2), weight=1)
        self.grid_columnconfigure(0, weight=0)
        self._frame_project.grid(row=0, column=0, pady=PADY, sticky=STICKY)
        self._tabview_input_files.grid(row=1, column=0, pady=PADY, sticky=STICKY)
        self._tabview_configuration.grid(row=2, column=0, pady=PADY, sticky=STICKY)
        self._frame_analysis.grid(row=3, column=0, pady=PADY, sticky=STICKY)


class OTAnalyticsGui:
    def __init__(
        self,
        view_model: ViewModel,
        layers: Sequence[Layer],
    ) -> None:
        self._viewmodel = view_model
        self._app: ModifiedCTk = ModifiedCTk(viewmodel=view_model)
        self._layers = layers

    def start(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        set_appearance_mode("System")
        set_default_color_theme("green")

        self._app.title("OTAnalytics")
        self._app.minsize(width=1024, height=768)

        self._get_widgets()
        self._place_widgets()
        self._app.after(0, lambda: self._app.state("zoomed"))
        self._app.mainloop()

    def _get_widgets(self) -> None:
        self._app.grid_columnconfigure(0, minsize=350, weight=0)
        self._app.grid_columnconfigure(1, weight=1)
        self._app.grid_rowconfigure(0, weight=1)
        self._navigation = FrameNavigation(master=self._app, viewmodel=self._viewmodel)
        self._content = FrameContent(
            master=self._app, viewmodel=self._viewmodel, layers=self._layers
        )

    def _place_widgets(self) -> None:
        self._navigation.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._content.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
