#load video
import tkinter as tk


def video_count_window():
    # row index for a simple change of the gui components
    row_index = 0

    # second window for the settings
    toplevelwindow = tk.Toplevel()
    toplevelwindow.title("Manuel traffic counting settings")
    toplevelwindow.geometry("550x" + str(9*30))