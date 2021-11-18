gui_dict = {
    "linedetector_toggle": False,
    "polygondetector_toggle": False,
    "tracks_imported": False,
    "detections_drawn": False,
    "display_all_tracks_toggle": False,
    "play_video": False,
    "rewind_video": False,
    "counting_mode": False,
    "during_counting_process": False,
    "mousescroll_active": False,
    "display_bb": False,
    "display_live_track": False,
}

color_dict = {
    "car": (89, 101, 212),
    "bicycle": (73, 166, 91),
    "truck": (97, 198, 212),
    "motorcycle": (148, 52, 137),
    "person": (214, 107, 88),
    "bus": (179, 177, 68),
}

statepanel_txt = {
    "Linedetector_information": "press and drag mouse to create a line\nbutton needs to be toggled to remove sections",
    "Add_movement_information": "select and add section while movement is highlighted",
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
            "left click to create new polyogoncorner\nright button to delete previous corner\nwheelclick to close polygon\nenter to finish creation process"
        )
    else:
        button_polygondetector.config(text="Polygon")


def button_manuel_count(button_manuel_count):
    """Button to toggle manuel count

    Args:
        button_manuel_count (tkinter): ...
    """

    gui_dict["counting_mode"] = not gui_dict["counting_mode"]

    if gui_dict["counting_mode"] is False:

        button_manuel_count.config(text="count", background="SystemButtonFace")

    else:

        button_manuel_count.config(text="mc-active", background="red")


def button_display_tracks_toggle(button):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): ...
    """
    gui_dict["display_all_tracks_toggle"] = not gui_dict["display_all_tracks_toggle"]

    if gui_dict["display_all_tracks_toggle"]:
        button.config(text="hide tracks")
    else:
        button.config(text="show tracks")


def button_display_bb(button):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): ...
    """
    gui_dict["display_bb"] = not gui_dict["display_bb"]

    if gui_dict["display_bb"]:
        button.config(text="hide bb")
    else:
        button.config(text="show bb")


def button_play_video_toggle(button_play, button_rewind):
    """Toggle video play function

    Args:
        button (tkinter button): ...
    """
    gui_dict["play_video"] = not gui_dict["play_video"]

    print(gui_dict["play_video"])

    if gui_dict["play_video"]:
        button_play.config(text="Stop")
        button_rewind.config(text="Rewind")
    else:
        button_play.config(text="Play")


def button_rewind_video_toggle(button_rewind, button_play):
    """Summary.

    Args:
        button (tkinter button): ...
    """
    gui_dict["rewind_video"] = not gui_dict["rewind_video"]

    if gui_dict["rewind_video"]:
        button_rewind.config(text="Stop")
        button_play.config(text="Play")
    else:
        button_rewind.config(text="Rewind")


def button_display_live_track(button_display_tracks):
    """Summary.

    Args:
        button (tkinter button): ...
    """

    gui_dict["display_live_track"] = not gui_dict["display_live_track"]

    if gui_dict["display_live_track"]:
        button_display_tracks.config(text="Stop Livetrack")
    else:
        button_display_tracks.config(text="Livetrack")
