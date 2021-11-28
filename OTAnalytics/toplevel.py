import tkinter as tk


class SectionEntryWindow(tk.Toplevel):
    def __init__(self, tuple_func_arg, **kwargs):
        super().__init__(**kwargs)

        func = tuple_func_arg[0]
        arg = tuple_func_arg[1]

        self.command = lambda x=arg: func(x)
        self.detector_name_entry = tk.Entry(self)

        self.detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.detector_name_entry.focus()

        self.add_section = tk.Button(self, text="Add section", command=self.command)
        self.add_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        # makes the background window unavailable
        self.grab_set()
