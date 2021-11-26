import tkinter


class App:
    def __init__(self):
        ...  # some code
        window_button = tkinter.Button(
            universe_window,
            text="0",
            font=(font, font_size_small),
            command=self.get_number,
        )
        window_button.place(x=654, y=310)

    def get_number(self):
        self.value = Get_Number("Display_Commands", "0")
