"""Dictionary with helpfull bool-toggles."""

gui_dict = {
    "linedetector_toggle": False,
    "polygondetector_toggle": False,
    "tracks_imported": False,
    "detections_drawn": False,
    "display_all_tracks_toggle": False,
    "play_video": False
}

statepanel_txt = {"Linedetector_information": "press and drag mouse to create a line \
                  Button needs to be toggled to remove sections",
                  "Add_movement_information": "select and add section while \
                  movement is highlighted"}


def button_information_line(button, statepanel):
    """Prints information on the statepanel when Linedetector button is pressed.

    Args:
        button ([tkinter button]): simple button
        statepanel ([textfield]): shows information
    """
    gui_dict["linedetector_toggle"] = not gui_dict["linedetector_toggle"]

    if gui_dict["linedetector_toggle"] is True and \
       gui_dict["polygondetector_toggle"] is False:
        button.config(text="Finish")
        statepanel.update(statepanel_txt["Linedetector_information"])
    else:
        button.config(text="Line")
        statepanel.update("")


def button_information_polygon(button, statepanel):
    """Prints information on the statepanel when Polygondetector button is pressed.

    Args:
        button ([tkinter button]): simple button
        statepanel ([textfield]): shows information
    """

    gui_dict["polygondetector_toggle"] = not gui_dict["polygondetector_toggle"]
    if gui_dict["polygondetector_toggle"] is True and \
       gui_dict["linedetector_toggle"] is False:
        button.config(text="Finish")
        statepanel.update("left click to create new polyogon \
        corner\nmiddle button to delete previous corner\nright click to close polygon")
    else:
        button.config(text="Polygon")


def button_display_tracks_toggle(button):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): ...
    """
    gui_dict["display_all_tracks_toggle"] = not gui_dict["display_all_tracks_toggle"]

    print(gui_dict["display_all_tracks_toggle"])

    if gui_dict["display_all_tracks_toggle"] is True:
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

    if gui_dict["play_video"] is True:
        button.config(text="Stop")
    else:
        button.config(text="Play")
