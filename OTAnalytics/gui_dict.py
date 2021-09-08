"""Dictionary with helpfull bool-toggles."""

from tkinter.constants import FALSE


gui_dict = {
    "linedetector_toggle": False,
    "polygondetector_toggle": False,
    "tracks_imported": False,
    "detections_drawn": False,
    "display_all_tracks_toggle": False,
    "play_video": False,
    "counting_mode": False,
}

statepanel_txt = {
    "Linedetector_information": "press and drag mouse to create a line \
                  Button needs to be toggled to remove sections",
    "Add_movement_information": "select and add section while \
                  movement is highlighted",
}


def button_information_line(button_linedetector, button_polygondetector, statepanel):
    """Prints information on the statepanel when Linedetector button is pressed.

    Args:
        button ([tkinter button]): simple button
        statepanel ([textfield]): shows information
    """
    gui_dict["linedetector_toggle"] = not gui_dict["linedetector_toggle"]

    gui_dict["polygondetector_toggle"] = False

    if gui_dict["linedetector_toggle"]:
        button_linedetector.config(text="Finish")
        button_polygondetector.config(text="Polygon")
        statepanel.update_statepanel(statepanel_txt["Linedetector_information"])
    else:
        button_linedetector.config(text="Line")
        statepanel.update_statepanel("")


def button_information_polygon(
    button_polygondetector, button_linedetetector, statepanel
):
    """Prints information on the statepanel when Polygondetector button is pressed.

    Args:
        button ([tkinter button]): simple button
        statepanel ([textfield]): shows information
    """

    gui_dict["polygondetector_toggle"] = not gui_dict["polygondetector_toggle"]

    gui_dict["linedetector_toggle"] = False

    if gui_dict["polygondetector_toggle"]:
        button_polygondetector.config(text="Finish")
        button_linedetetector.config(text="Line")
        statepanel.update_statepanel(
            "left click to create new polyogon \
        corner\nright button to delete previous corner\nwheelbutton click to close polygon\nEnter to finish creation process"
        )
    else:
        button_polygondetector.config(text="Polygon")


def button_manuel_count(button_manuel_count):

    gui_dict["counting_mode"] = not gui_dict["counting_mode"]

    print(gui_dict["counting_mode"])

    if gui_dict["counting_mode"] is False:

        button_manuel_count.config(text="mancount", background="SystemButtonFace")

    else:

        button_manuel_count.config(text="mc-active", background="red")


def button_display_tracks_toggle(button):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): ...
    """
    gui_dict["display_all_tracks_toggle"] = not gui_dict["display_all_tracks_toggle"]

    print(gui_dict["display_all_tracks_toggle"])

    if gui_dict["display_all_tracks_toggle"]:
        button.config(text="hide tracks")
    else:
        button.config(text="show tracks")


def button_play_video_toggle(button):
    """Summary.

    Args:
        button ([type]): [description]
    """
    gui_dict["play_video"] = not gui_dict["play_video"]

    print(gui_dict["play_video"])

    if gui_dict["play_video"]:
        button.config(text="Stop")
    else:
        button.config(text="Play")
