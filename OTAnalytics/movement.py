from tkinter import Toplevel
import tkinter as tk
from tkinter.constants import END

# import json
from gui_dict import statepanel_txt


def new_movement(listbox_movement, movement_dict):
    """Creates new movement and adds it to the movement listbox.

    Args:
        listbox_movement ([type]): tkinter listbox to display created movements
        movement_dict ([type]): dictionary with movements, second key in flow file
    """
    new_movement_creation = Toplevel()

    new_movement_creation.title("Create new movement")
    movement_name_entry = tk.Entry(new_movement_creation, textvariable="Movement")
    movement_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
    movement_name_entry.delete(0, END)
    movement_name_entry.focus()
    add_movement = tk.Button(
        new_movement_creation,
        text="Add movement",
        command=lambda: recieve_movement_name(
            movement_name_entry, listbox_movement, movement_dict, new_movement_creation
        ),
    )
    add_movement.grid(row=1, column=1, sticky="w", pady=10, padx=10)
    new_movement_creation.protocol("WM_DELETE_WINDOW")


def recieve_movement_name(
    movement_name_entry, listbox_movement, movement_dict, new_movement_creation
):
    movement_name = movement_name_entry.get()
    listbox_movement.insert(END, movement_name)
    movement_dict[movement_name] = []

    new_movement_creation.destroy()


def add_to_movement(
    listbox,
    listbox_movement,
    linedetectors,
    polygondetectors,
    movement_dict,
    listbox_movement_detector,
):
    """Possible to add detectors and sections to the selected movement.

    Args:
        listbox ([type]): [description]
        listbox_movement ([type]): [description]
        linedetectors ([type]): [description]
        polygondetectors ([type]): [description]
        movement_dict ([type]): [description]
        listbox_movement_detector ([type]): [description]
    """
    detector_selection = listbox.curselection()
    detector_name = listbox.get(detector_selection[0])

    movement_selection = listbox_movement.curselection()
    movement_name = listbox_movement.get(movement_selection[0])

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

    listbox_movement_detector.insert(END, detector_name)


def curselected_movement(
    event, listbox_movement_detector, listbox_movement, movement_dict, statepanel
):
    # shows detectors and sections belonging to selected movement

    listbox_movement_detector.delete(0, "end")

    movement_selection = listbox_movement.curselection()
    movement_name = listbox_movement.get(movement_selection[0])

    for detector_name in movement_dict[movement_name]:
        detector_name = (
            detector_name
            + " #"
            + str(movement_dict[movement_name].index(detector_name) + 1)
        )

        listbox_movement_detector.insert(END, detector_name)

    statepanel.update_statepanel(statepanel_txt["Add_movement_information"])
