import tkinter as tk
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
from count import counting


class Statepanel:
    # class to give out states from current video and countings
    def __init__(self, window, row, column, sticky):
        self.scrollbar = tk.Scrollbar(window)
        self.text = tk.Text(
            window,
            height=4,
            width=100,
            state="disabled",
            yscrollcommand=self.scrollbar.set,
            bg="white",
        )
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.grid(
            row=row, column=column, columnspan=2, padx="5", pady="3", sticky="e"
        )
        self.text.grid(row=row, column=column, padx="5", pady="3", sticky=sticky)

        # new information

    def update(self, text):
        self.text.config(state="normal")
        self.text.insert(tk.END, "- " + str(text) + "\n")
        self.text.see("end")
        self.text.config(state="disabled")


class Controllbar:
    def __init__(self, window, padx, side):
        self.button1 = tk.Button(window, text="back")
        self.button2 = tk.Button(window, text="play")
        self.button3 = tk.Button(window, text="forward")
        self.button4 = tk.Button(window, text="QUIT", fg="red", command=window.quit)

        self.button1.pack(padx=padx, side=side)
        self.button2.pack(padx=padx, side=side)
        self.button3.pack(padx=padx, side=side)
        self.button4.pack(padx=padx, side=side)


class Sidepanel:
    def __init__(self, window, padx, side, anchor):
        self.button5 = tk.Button(
            window,
            text="load",
            command=lambda: counting.video_count_window(),
        )
        self.button6 = tk.Button(window, text="save")

        self.button6.pack(padx=padx, side=side, anchor=anchor)
        self.button5.pack(padx=padx, side=side, anchor=anchor)


class Filepath:
    def __init__(self, window, folder_path_bool, text, width, text_button):
        self.folder_path_bool = folder_path_bool
        self.label = tk.Label(window, text=text)
        self.entry = tk.Entry(window, width=width)

        # search for the video file in the explorer to get the file path

    def mtc_get_video_path(self, window):
        if self.folder_path_bool:
            new_filepath = filedialog.askdirectory(parent=window)
        else:
            new_filepath = filedialog.askopenfilename(parent=window)
        print(new_filepath)
        if new_filepath != "":
            self.entry.delete(0, tk.END)
            self.entry.insert(0, new_filepath)


# toplevelwindow for the junction properties and the video file path
def video_count_window(app, folder_path_bool):
    # row index for a simple change of the gui components
    row_index = 0

    # second window for the settings
    toplevelwindow = tk.Toplevel(app.window)
    toplevelwindow.title("Manuel traffic counting settings")
    toplevelwindow.geometry("550x" + str(9 * 30))


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1000x950")

        # creates nonexisting canvas to be filled later
        self.canvas = None
        self.label_hotkeys = None

        self.controllbar = Controllbar(self.window, 5, "left")
        self.sidepanel = Sidepanel(self.window, 5, "right", "ne")

        self.window.mainloop()


def mainfunction():
    App(tk.Tk(), "Traffic Count Tool")


if __name__ == "__main__":
    mainfunction()
