import tkinter as tk


class StatePanel:
    """Statepanel that contains usefull information."""

    # initialize StatePanel
    def __init__(
        self,
        window,
        row,
        column,
        sticky,
        rowspan,
        columnspan,
        inittext="Statepanel initialized",
    ):
        """Initial class information.

        Args:
            window (tkinter Frame): window where statepanel ist shown.
            row (tk row): row number
            column (tk column): column number
            sticky (arg): text alignment
            columnspan (arg): button span
        """
        self.scrollbar = tk.Scrollbar(window)
        self.text = tk.Text(
            window,
            height=3,
            width=50,
            yscrollcommand=self.scrollbar.set,
            state="disabled",
        )
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.grid(
            row=row, column=column, columnspan=2, padx="5", pady="3", sticky="w"
        )
        self.text.grid(
            row=row,
            column=column,
            padx="5",
            pady="3",
            sticky=sticky,
            rowspan=rowspan,
            columnspan=columnspan,
        )

        self.update_statepanel(inittext)

    def update_statepanel(self, text):
        """Function to update statepanel with wanted text.

        Args:
            text (string): Text to be shown.
        """
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert(tk.END, str(text))
        self.text.see("end")
        self.text.config(state="disabled")

    def move(self, row, column, sticky, columnspan=2):
        """Scroll up and down statepaneltext.

        Args:
            row (tk.row): Grid.rownumber.
            column (tk.column): Grid.columnnumber.
            sticky (arg): Expensionsarguments.
            columnspan (int, optional): Columndimensionspan.
        """
        self.scrollbar.grid(row=row, column=column, padx="5", pady="3", sticky="e")
        self.text.grid(
            row=row,
            column=column,
            padx="5",
            pady="3",
            sticky=sticky,
            columnspan=columnspan,
        )
