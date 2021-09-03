from tkinter import Toplevel
import tkinter as tk
from tkinter.constants import END

# import json
from gui_dict import statepanel_txt


def new_movement(ListboxMovement, movement_dict):
    """Creates new movement and adds it to the movement listbox."""
    new_movement_creation = Toplevel()

    new_movement_creation.title("Create new movement")
    movement_name_entry = tk.Entry(new_movement_creation, textvariable="Movement")
    movement_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
    movement_name_entry.delete(0, END)
    add_movement = tk.Button(
        new_movement_creation,
        text="Add movement",
        command=lambda: recieve_movement_name(
            movement_name_entry, ListboxMovement, movement_dict, new_movement_creation
        ),
    )
    add_movement.grid(row=1, column=1, sticky="w", pady=10, padx=10)
    new_movement_creation.protocol("WM_DELETE_WINDOW")


def recieve_movement_name(
    movement_name_entry, ListboxMovement, movement_dict, new_movement_creation
):
    movement_name = movement_name_entry.get()
    ListboxMovement.insert(END, movement_name)
    movement_dict[movement_name] = []

    new_movement_creation.destroy()


def add_to_movement(
    Listbox, ListboxMovement, linedetectors, polygondetectors, movement_dict, Listbox4
):
    """Possible to add detectors and sections to the selected movement.

    Args:
        Listbox ([type]): [description]
        ListboxMovement ([type]): [description]
        linedetectors ([type]): [description]
        polygondetectors ([type]): [description]
        movement_dict ([type]): [description]
        Listbox4 ([type]): [description]
    """
    detector_selection = Listbox.curselection()
    detector_name = Listbox.get(detector_selection[0])

    movement_selection = ListboxMovement.curselection()
    movement_name = ListboxMovement.get(movement_selection[0])

    if detector_name in linedetectors:

        print(detector_name)

        movement_dict[movement_name].append(detector_name)

    else:
        movement_dict[movement_name].update(
            {detector_name: polygondetectors[detector_name]}
        )

    detector_name = (
        detector_name
        + " #"
        + str(movement_dict[movement_name].index(detector_name) + 1)
    )

    Listbox4.insert(END, detector_name)


def curselected_movement(event, Listbox4, ListboxMovement, movement_dict, statepanel):
    # shows detectors and sections belonging to selected movement

    Listbox4.delete(0, "end")

    movement_selection = ListboxMovement.curselection()
    movement_name = ListboxMovement.get(movement_selection[0])

    for detector_name in movement_dict[movement_name]:
        detector_name = (
            detector_name
            + " #"
            + str(movement_dict[movement_name].index(detector_name) + 1)
        )

        Listbox4.insert(END, detector_name)

    statepanel.update_statepanel(statepanel_txt["Add_movement_information"])
