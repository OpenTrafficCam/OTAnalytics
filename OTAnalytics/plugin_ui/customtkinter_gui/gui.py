import tkinter
from functools import partial
from typing import Any, Sequence

from customtkinter import CTk, CTkFrame, set_appearance_mode, set_default_color_theme

from OTAnalytics.adapter_ui.abstract_main_window import AbstractMainWindow
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.config import ON_MAC
from OTAnalytics.application.exception import gather_exception_messages
from OTAnalytics.application.logger import logger
from OTAnalytics.application.plotting import LayerGroup
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.use_cases.preload_input_files import PreloadInputFiles
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STICKY,
    TkEvents,
)
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import (
    CustomCTkTabview,
    EmbeddedCTkScrollableFrame,
    SingleFrameTabview,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_analysis import TabviewAnalysis
from OTAnalytics.plugin_ui.customtkinter_gui.frame_canvas import FrameCanvas
from OTAnalytics.plugin_ui.customtkinter_gui.frame_configuration import (
    TabviewConfiguration,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_files import FrameFiles
from OTAnalytics.plugin_ui.customtkinter_gui.frame_filter import FrameFilter
from OTAnalytics.plugin_ui.customtkinter_gui.frame_project import TabviewProject
from OTAnalytics.plugin_ui.customtkinter_gui.frame_remarks import FrameRemarks
from OTAnalytics.plugin_ui.customtkinter_gui.frame_track_plotting import (
    FrameTrackPlotting,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_track_statistics import (
    FrameTrackStatistics,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_tracks import TracksFrame
from OTAnalytics.plugin_ui.customtkinter_gui.frame_videos import FrameVideos
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import CtkInfoBox

CANVAS: str = "Canvas"
FILES: str = "Files"


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
        self._bind_events()

    def _bind_events(self) -> None:
        self.bind(TkEvents.LEFT_BUTTON_DOWN, lambda event: event.widget.focus_set())

    def _ask_to_close(self) -> None:
        infobox = CtkInfoBox(
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

    def report_callback_exception(
        self, exc: BaseException | BaseExceptionGroup, val: Any, tb: Any
    ) -> None:
        messages = gather_exception_messages(val)
        message = "\n".join(messages)
        logger().exception(messages, exc_info=True)
        CtkInfoBox(message=message, title="Error", initial_position=self.get_position())


class TabviewInputFiles(CustomCTkTabview):
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
        self,
        master: Any,
        viewmodel: ViewModel,
        layers: Sequence[LayerGroup],
        **kwargs: Any,
    ) -> None:
        super().__init__(master=master, **kwargs)
        self._viewmodel = viewmodel

        self._frame_track_plotting = FrameTrackPlotting(
            master=self,
            viewmodel=viewmodel,
            layers=layers,
        )
        self._frame_canvas = FrameCanvas(
            master=self,
            viewmodel=self._viewmodel,
        )
        self._frame_canvas_controls = FrameCanvasControls(
            master=self, viewmodel=self._viewmodel
        )
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self._frame_canvas.grid(row=0, column=0, pady=PADY, sticky=STICKY)
        self._frame_track_plotting.grid(
            row=0, column=1, pady=PADY, sticky="ne", rowspan=2
        )
        self._frame_canvas_controls.grid(row=1, column=0, pady=PADY, sticky=STICKY)


class FrameCanvasControls(CTkFrame):
    def __init__(
        self,
        master: Any,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(master=master, bg_color="transparent", **kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self._remarks = SingleFrameTabview(
            master=self,
            title="Remarks",
            frame_factory=partial(FrameRemarks, viewmodel=self._viewmodel),
        )
        self._frame_track_statistics = SingleFrameTabview(
            master=self,
            title="Track Statistics",
            frame_factory=partial(FrameTrackStatistics, viewmodel=self._viewmodel),
        )
        self._frame_filter = SingleFrameTabview(
            master=self,
            title="Visualization Filters",
            frame_factory=partial(FrameFilter, viewmodel=self._viewmodel),
        )

    def _place_widgets(self) -> None:
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self._remarks.grid(row=2, column=0, pady=PADY, sticky=STICKY)
        self._frame_track_statistics.grid(row=0, column=0, pady=PADY, sticky=STICKY)
        self._frame_filter.grid(row=1, column=0, pady=PADY, sticky=STICKY)


class FrameNavigation(EmbeddedCTkScrollableFrame):
    def __init__(self, master: Any, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(master=master, **kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self._frame_project = TabviewProject(
            master=self,
            viewmodel=self._viewmodel,
        )
        self._tabview_input_files = TabviewInputFiles(
            master=self, viewmodel=self._viewmodel
        )
        self._tabview_configuration = TabviewConfiguration(
            master=self, viewmodel=self._viewmodel
        )
        self._frame_analysis = TabviewAnalysis(master=self, viewmodel=self._viewmodel)

    def _place_widgets(self) -> None:
        self.grid_rowconfigure((1, 2), weight=1)
        self.grid_columnconfigure((0, 3), weight=0)
        self._frame_project.grid(row=0, column=0, pady=PADY, sticky=STICKY)
        self._tabview_input_files.grid(row=1, column=0, pady=PADY, sticky=STICKY)
        self._tabview_configuration.grid(row=2, column=0, pady=PADY, sticky=STICKY)
        self._frame_analysis.grid(row=3, column=0, pady=PADY, sticky=STICKY)


class TabviewContent(CustomCTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        layers: Sequence[LayerGroup],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._layers = layers
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.add(CANVAS)
        self.frame_tracks = FrameContent(
            master=self.tab(CANVAS), viewmodel=self._viewmodel, layers=self._layers
        )
        self.add(FILES)
        self.frame_track_files = FrameFiles(
            master=self.tab(FILES), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_tracks.pack(fill=tkinter.BOTH, expand=True)
        self.frame_track_files.pack(fill=tkinter.BOTH, expand=True)
        self.set(CANVAS)


class OTAnalyticsGui:
    def __init__(
        self,
        app: ModifiedCTk,
        view_model: ViewModel,
        layers: Sequence[LayerGroup],
        preload_input_files: PreloadInputFiles,
        run_config: RunConfiguration,
    ) -> None:
        self._viewmodel = view_model
        self._app = app
        self._layers = layers
        self._preload_input_files = preload_input_files
        self._run_config = run_config

    def start(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        set_appearance_mode("System")
        set_default_color_theme("green")

        self._app.title("OTAnalytics")
        self._app.minsize(width=1024, height=768)

        self._get_widgets()
        self._place_widgets()
        self._register_global_keybindings()
        self._app.after(0, lambda: self._app.state("zoomed"))
        self._app.after(1000, lambda: self._preload_input_files.load(self._run_config))
        self._app.mainloop()

    def _get_widgets(self) -> None:
        self._navigation = FrameNavigation(
            master=self._app,
            viewmodel=self._viewmodel,
            width=336,
        )
        self._content = TabviewContent(
            master=self._app, viewmodel=self._viewmodel, layers=self._layers
        )

    def _place_widgets(self) -> None:
        self._app.grid_columnconfigure(0, minsize=300, weight=0)
        self._app.grid_columnconfigure(1, weight=1)
        self._app.grid_rowconfigure(0, weight=1)
        self._navigation.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._content.grid(
            row=0,
            column=1,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )

    def _register_global_keybindings(self) -> None:
        cmd_ctrl = "Command" if ON_MAC else "Control"
        opt_alt = "Option" if ON_MAC else "Alt"
        shift = "Shift"
        next_key = "Right"
        previous_key = "Left"
        self._app.bind(f"<{next_key}>", lambda event: self._viewmodel.next_frame())
        self._app.bind(
            f"<{cmd_ctrl}-{next_key}>", lambda event: self._viewmodel.next_second()
        )
        self._app.bind(
            f"<{cmd_ctrl}-{shift}-{next_key}>",
            lambda event: self._viewmodel.switch_to_next_date_range(),
        )
        self._app.bind(
            f"<{cmd_ctrl}-{opt_alt}-{shift}-{next_key}>",
            lambda event: self._viewmodel.next_event(),
        )
        self._app.bind(
            f"<{previous_key}>", lambda event: self._viewmodel.previous_frame()
        )
        self._app.bind(
            f"<{cmd_ctrl}-{previous_key}>",
            lambda event: self._viewmodel.previous_second(),
        )
        self._app.bind(
            f"<{cmd_ctrl}-{shift}-{previous_key}>",
            lambda event: self._viewmodel.switch_to_prev_date_range(),
        )
        self._app.bind(
            f"<{cmd_ctrl}-{opt_alt}-{shift}-{previous_key}>",
            lambda event: self._viewmodel.previous_event(),
        )
        self._app.bind(
            f"<{cmd_ctrl}-s>", lambda event: self._viewmodel.quick_save_configuration()
        )
        self._app.bind(
            f"<{cmd_ctrl}-{shift}-S>",
            lambda event: self._viewmodel.save_configuration(),
        )
