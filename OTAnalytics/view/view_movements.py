import tkinter as tk
import tkinter.ttk as ttk
from view.helpers.gui_helper import info_message
import helpers.file_helper as file_helper


class FrameMovements(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Movement", **kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack()

        self.frame_controls = tk.Frame(master=self)
        self.frame_controls.pack()

        # Movements treeview
        self.tree_movements = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_movements.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        tree_files_cols = {"#0": "Movements", "Composition": "Section Order"}
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
        self.button_new_movement.grid(
            row=0, column=0, padx=(10, 0), pady=(0, 10), sticky="ew"
        )

        # remove movement
        self.button_remove_movement = tk.Button(
            master=self.frame_controls, text="Remove", command=self.delete_movement
        )
        self.button_remove_movement.grid(row=0, column=1, pady=(0, 10), sticky="ew")

        # clear movement
        self.button_clear = tk.Button(
            master=self.frame_controls,
            text="Clear",
        )
        self.button_clear.grid(row=0, column=2, pady=(0, 10), sticky="ew")

        # # rename movement
        self.button_rename_movement = tk.Button(
            master=self.frame_controls,
            text="Rename",
            command=self.create_movement_rename_window,
        )
        self.button_rename_movement.grid(row=0, column=3, pady=(0, 10), sticky="ew")

        self.button_autocreate_movement = tk.Button(
            master=self.frame_controls,
            text="Autofill",
            command=self.create_movement_autofill_window,
        )
        self.button_autocreate_movement.grid(
            row=0, column=4, padx=(0, 10), pady=(0, 10), sticky="ew"
        )

    def new_movement(self, entrywidget):
        """Saves created movement to flowfile.

        Args:
            flow_dict (dictionary): Dictionary with sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in movementname.
        """
        movement_name = entrywidget.get()

        if movement_name in file_helper.flow_dict["Movements"].keys():
            tk.messagebox.showinfo(
                title="Warning", message="Movementname already exists!"
            )

        else:

            file_helper.flow_dict["Movements"][movement_name] = []

            self.tree_movements.insert(parent="", index="end", text=movement_name)

            entrywidget.delete(0, tk.END)

    def create_movement_entry_window(self):
        """Creates toplevel window to name movements."""

        new_movement_creation = tk.Toplevel()
        new_movement_creation.geometry("%dx%d+%d+%d" % (260, 50, 850, 350))

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

    def delete_movement(self):
        """Deletes selected section  from flowfile and listboxwidget."""

        itemlist = list(self.tree_movements.selection())

        if not itemlist:
            info_message("Warning", "Please select movement you wish to delete!")

            return

        for movementitem in itemlist:

            movement_name = self.tree_movements.item(movementitem, "text")

            self.tree_movements.delete(movementitem)

            del file_helper.flow_dict["Movements"][movement_name]

    def create_movement_rename_window(self):

        item = self.tree_movements.selection()
        movement_name = self.tree_movements.item(item, "text")

        if not movement_name:
            info_message("Warning", "Please select movement you wish to rename!")

            return

        self.item = self.tree_movements.selection()
        movement_name = self.tree_movements.item(self.item, "text")

        self.rename_movement_creation = tk.Toplevel()

        self.rename_movement_creation.title("Rename movement")
        movement_name_entry = tk.Entry(
            self.rename_movement_creation, textvariable="Movement"
        )

        # delete old text
        movement_name_entry.delete(0, tk.END)

        # insert text from selection
        movement_name_entry.insert(0, movement_name)
        movement_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
        movement_name_entry.focus()
        rename_movement = tk.Button(
            self.rename_movement_creation,
            text="rename movement",
            command=lambda: self.rename_movement(movement_name, movement_name_entry),
        )
        rename_movement.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        self.rename_movement_creation.protocol("WM_DELETE_WINDOW")
        self.rename_movement_creation.grab_set()

    def rename_movement(self, old_movement_name, entrywidget):

        movement_new_name = entrywidget.get()

        if movement_new_name not in file_helper.flow_dict["Movements"].keys():
            file_helper.flow_dict["Movements"][
                movement_new_name
            ] = file_helper.flow_dict["Movements"].pop(old_movement_name)

            self.tree_movements.item(self.item, text=movement_new_name)

            self.rename_movement_creation.destroy()

        else:
            tk.messagebox.showinfo(
                title="Warning", message="Please enter a different movement name!"
            )

    def create_movement_autofill_window(self):

        if len(file_helper.flow_dict["Detectors"]) <= 1:
            tk.messagebox.showinfo(
                title="Warning", message="Please at least two sections!"
            )
            return

        autofill_topwindow = tk.Toplevel()

        textfield = tk.Label(
            autofill_topwindow, text="Selected section will be combined to movements."
        )

        textfield.pack(
            fill="x",
            padx=10,
        )

        # selection treeview
        tree_select_section = ttk.Treeview(
            master=autofill_topwindow,
            height=len(file_helper.flow_dict["Detectors"]),
        )
        tree_select_section.pack(
            fill="x",
            padx=10,
        )

        tree_files_cols = {"#0": "Sections"}
        tree_select_section["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        tree_select_section.column("#0", anchor="center", width=100)
        tree_select_section.heading("#0", text=tree_files_cols["#0"], anchor="center")
        for detector in file_helper.flow_dict["Detectors"]:
            tree_select_section.insert(parent="", index="end", text=detector)

        autofill_button = tk.Button(
            autofill_topwindow,
            text="Autocreation of movements",
            command=lambda: self.autofill_movement(tree_select_section),
        )
        autofill_button.pack(pady=10, padx=5)

        autofill_topwindow.grab_set()

    def autofill_movement(self, treeview):
        """Autocreates movement from sections (maxpermutation 2)

        Args:
            treeview (tkinter treeview): treeview to input movements.
        """
        items = treeview.selection()
        sectionlist = [treeview.item(section, "text") for section in items]

        permutation_list = file_helper.permutation_of_list(sectionlist)

        for permutation in permutation_list:

            if list(permutation) in file_helper.flow_dict["Movements"].values():
                tk.messagebox.showinfo(
                    title="Warning",
                    message="Combination "
                    + permutation[0]
                    + " and "
                    + permutation[1]
                    + " already exists!",
                )
                continue
            file_helper.flow_dict["Movements"][
                permutation[0] + "-" + permutation[1]
            ] = list(permutation)

            self.tree_movements.insert(
                parent="",
                index="end",
                text=permutation[0] + "-" + permutation[1],
                value=[
                    file_helper.flow_dict["Movements"][
                        permutation[0] + "-" + permutation[1]
                    ]
                ],
            )
