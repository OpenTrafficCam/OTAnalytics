import tkinter as tk
from view_movements import FrameMovements
from view_helpers import FrameFiles
from canvas import CanvasFrame
from view_sections import FrameSection
from view_objects import FrameObject


class test_gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTAnalytics")
        self.set_layout()

        self.title("OTAnalytics")

    def set_layout(
        self,
    ):
        self.frame_controll_panel = tk.Frame(master=self)
        self.frame_controll_panel.pack(side="left", anchor="n")

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(side="right")

        self.canvas = CanvasFrame(master=self.frame_canvas)
        self.canvas.pack()

        self.frame_files = FrameFiles(master=self.frame_controll_panel)
        self.frame_files.grid(
            **{"padx": 10, "pady": 10}, row=0, column=0, columnspan=2, sticky="ew"
        )

        self.videolabel = tk.Label(
            master=self.frame_controll_panel,
            text="Sections and Objects",
            fg="white",
            bg="#37483E",
        )
        self.videolabel.grid(
            **{"padx": 10, "pady": 10}, row=1, column=0, columnspan=2, sticky="ew"
        )

        self.frame_sections = FrameSection(master=self.frame_controll_panel)
        self.frame_sections.grid(
            **{"padx": 10, "pady": 0}, row=2, column=0, sticky="ew"
        )

        self.frame_objects = FrameObject(master=self.frame_controll_panel)
        self.frame_objects.grid(**{"padx": 10, "pady": 0}, row=2, column=1, sticky="ew")

        self.frame_movements = FrameMovements(master=self.frame_controll_panel)
        self.frame_movements.grid(
            **{"padx": 10, "pady": 10}, row=3, column=0, sticky="ew"
        )


def main():
    """Main function."""
    app = test_gui()
    app.mainloop()


if __name__ == "__main__":
    main()
