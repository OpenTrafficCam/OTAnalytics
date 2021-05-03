import tkinter as tk


class Statepanel:
    #class to give out states from current video and countings
    pass


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1000x950")
        self.button = tk.Button(window, text="QUIT", fg="red", command=window.quit)
        self.button.pack()

        # creates nonexisting canvas to be filled later
        self.canvas = None
        self.label_hotkeys = None

        self.window.mainloop()


def mainfunction():
    App(tk.Tk(), "Traffic Count Tool")


if __name__ == "__main__":
    mainfunction()
