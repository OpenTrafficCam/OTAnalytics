import tkinter as tk
import tkinter.ttk as ttk


global videoobject
global maincanvas


class FrameFiles(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Frame for treeview
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        # Files treeview
        self.tree_files = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_files.pack(fill="x")

        tree_files_cols = {
            "#0": "Video",
            "otdet": "otdet",
            "ottrk": "ottrk",
        }

        self.tree_files["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )

        for tree_files_col_id, tree_files_col_text in tree_files_cols.items():
            if tree_files_col_id == "#0":
                anchor = "w"
                width = 400
            else:
                anchor = "center"
                width = 50
            self.tree_files.column(tree_files_col_id, width=width, anchor=anchor)
            self.tree_files.heading(
                tree_files_col_id, text=tree_files_col_text, anchor=anchor
            )
        self.tree_files.pack(side="left")

        # Button for add, play, rewind, clear
        self.frame_control = tk.Frame(master=self)
        self.frame_control.pack()

        # Add Video
        self.button_add_video = tk.Button(master=self.frame_control, text="Add video")
        self.button_add_video.grid(row=0, column=0, sticky="ew")

        # Play Video
        self.button_play_video = tk.Button(master=self.frame_control, text="Play video")
        self.button_play_video.grid(row=0, column=1, sticky="ew")

        # Rewind Video
        self.button_add_rewind_video = tk.Button(
            master=self.frame_control, text="Rewind video"
        )
        self.button_add_rewind_video.grid(row=0, column=2, sticky="ew")

        # Clear Video
        self.button_add_rewind_video = tk.Button(
            master=self.frame_control, text="Rewind video"
        )
        self.button_add_rewind_video.grid(row=0, column=2, sticky="ew")

        def add_video(self):
            # load video object
            video_source = filedialog.askopenfile(
                filetypes=[("Videofiles", "*.mkv"), ("Videofiles", "*.mp4")]
            )
            filepath = video_source.name
            print(f"filepath: {filepath}")

            return Video(filepath)


class CanvasFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack()

    def create_canvas(self):
        pass


class test_gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTAnalytics")
        self.set_layout()

    def set_layout(
        self,
    ):
        self.frame_files = FrameFiles(master=self)
        self.frame_files.grid(
            **{"padx": 10, "pady": 10}, row=0, column=0, columnspan=3, sticky="ew"
        )

        self.frame_canvas = CanvasFrame(master=self)
        self.frame_canvas.grid(**{"padx": 10, "pady": 10}, row=0, column=4, sticky="ew")


def main():
    """Main function."""
    app = test_gui()
    app.mainloop()


if __name__ == "__main__":
    main()
