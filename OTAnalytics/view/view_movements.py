import tkinter as tk
import tkinter.ttk as ttk
import image_alteration
import file_helper


class FrameMovements(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack()

        self.frame_controls = tk.Frame(master=self)
        self.frame_controls.pack()

        # Movements treeview
        self.tree_movements = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_movements.pack(fill="x")

        tree_files_cols = {"#0": "Movements", "Composition": "Composition"}
        self.tree_movements["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_movements.column("#0", anchor="center", width=100)
        self.tree_movements.column("Composition", anchor="center")
        self.tree_movements.heading("#0", text=tree_files_cols["#0"], anchor="center")
        self.tree_movements.heading(
            "Composition", text=tree_files_cols["Composition"], anchor="center"
        )

        # new_movement
        self.button_new_movement = tk.Button(
            master=self.frame_controls,
            text="New movement",
            command=self.create_movement_entry_window,
        )
        self.button_new_movement.grid(row=0, column=0, sticky="ew")

        # rename movement
        self.button_rename_movement = tk.Button(
            master=self.frame_controls,
            text="Rename",
        )
        self.button_rename_movement.grid(row=0, column=1, sticky="ew")

        # Rename movement
        self.button_remove_movement = tk.Button(
            master=self.frame_controls,
            text="Remove",
        )
        self.button_remove_movement.grid(row=0, column=2, sticky="ew")

        # clear movement
        self.button_clear = tk.Button(
            master=self.frame_controls,
            text="Clear",
        )
        self.button_clear.grid(row=0, column=3, sticky="ew")

        # Add save flow_dict
        self.button_save_flowfile = tk.Button(
            master=self.frame_controls,
            text="Save",
        )
        self.button_remove_movement.grid(row=0, column=4, sticky="ew")

        # Add to movement
        self.button_load_flowfile = tk.Button(
            master=self.frame_controls,
            text="Load",
        )
        self.button_clear.grid(row=0, column=5, sticky="ew")

    def new_movement(self, entrywidget):
        """Saves created movement to flowfile.

        Args:
            flow_dict (dictionary): Dictionary with sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in movementname.
        """
        movement_name = entrywidget.get()

        file_helper.flow_dict["Movements"][movement_name] = []

        self.tree_movements.insert(parent="", index="end", text=movement_name)

        entrywidget.delete(0, tk.END)

    def create_movement_entry_window(self):
        """Creates toplevel window to name movements."""

        new_movement_creation = tk.Toplevel()

        new_movement_creation.title("Create new movement")
        movement_name_entry = tk.Entry(new_movement_creation, textvariable="Movement")
        movement_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
        movement_name_entry.delete(0, tk.END)
        movement_name_entry.focus()
        add_movement = tk.Button(
            new_movement_creation,
            text="Add movement",
            command=lambda: self.new_movement(movement_name_entry),
        )
        add_movement.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        new_movement_creation.protocol("WM_DELETE_WINDOW")
        new_movement_creation.grab_set()
