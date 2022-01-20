button_bool = {
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
    "slider": False,
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
    "Linedetector_information": "press and drag mouse to create a line\nbutton needs to"
    + " be toggled to remove sections",
    "Add_movement_information": "select and add section while movement is highlighted",
}


def button_play_video_switch(button_play, button_rewind):
    """Toggle video play function.

    Args:
        button (tkinter.button): play and rewind button.
    """
    button_bool["play_video"] = not button_bool["play_video"]

    if button_bool["play_video"]:
        button_play.config(text="Stop")
        button_rewind.config(text="Rewind")
    else:
        button_play.config(text="Play")


def button_rewind_switch(button_rewind, button_play):
    """Toggle video rewind function.

    Args:
        button (tkinter button): play and rewind button.
    """
    button_bool["rewind_video"] = not button_bool["rewind_video"]

    if button_bool["rewind_video"]:
        button_rewind.config(text="Stop")
        button_play.config(text="Play")
    else:
        button_rewind.config(text="Rewind")


def button_line_switch(button_linedetector, button_polygondetector, statepanel):
    """Prints information on the statepanel when linedetector button is pressed.

    Args:
        button (tkinter button): Buttons.
        statepanel (textfield.class): Shows information.
    """
    button_bool["linedetector_toggle"] = not button_bool["linedetector_toggle"]

    button_bool["polygondetector_toggle"] = False

    if button_bool["linedetector_toggle"]:
        button_linedetector.config(text="Finish")
        button_polygondetector.config(text="Polygon")
        statepanel.update_statepanel(statepanel_txt["Linedetector_information"])
    else:
        button_linedetector.config(text="Line")
        statepanel.update_statepanel("")


def button_polygon_switch(button_polygondetector, button_linedetector, statepanel):
    """Prints information on the statepanel when Polygondetector button is pressed.

    Args:
        button (tkinter button): Buttons.
        statepanel (textfield.class): Shows information.
    """

    button_bool["polygondetector_toggle"] = not button_bool["polygondetector_toggle"]

    button_bool["linedetector_toggle"] = False

    if button_bool["polygondetector_toggle"]:
        button_polygondetector.config(text="Finish")
        button_linedetector.config(text="Line")
        statepanel.update_statepanel(
            "left click to create new polygoncorner\nright button to delete previous"
            + " corner\nwheelclick to close polygon\nenter to finish creation process"
        )
    else:
        button_polygondetector.config(text="Polygon")


def button_display_tracks_switch(button_display_tracks):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): Button.
    """
    button_bool["display_all_tracks_toggle"] = not button_bool[
        "display_all_tracks_toggle"
    ]

    if button_bool["display_all_tracks_toggle"]:
        button_display_tracks.config(text="hide tracks")
    else:
        button_display_tracks.config(text="show tracks")


def button_display_bb_switch(button_display_bb):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): Button.
    """
    button_bool["display_bb"] = not button_bool["display_bb"]

    if button_bool["display_bb"]:
        button_display_bb.config(text="hide bb")
    else:
        button_display_bb.config(text="show bb")


def button_display_live_track_switch(button_display_tracks):
    """Toggles the live-display of trajectories while playing video.

    Args:
        button (tkinter button): Buttons.
    """

    button_bool["display_live_track"] = not button_bool["display_live_track"]

    if button_bool["display_live_track"]:
        button_display_tracks.config(text="Stop Livetrack")
    else:
        button_display_tracks.config(text="Livetrack")
