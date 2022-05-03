from tkinter import messagebox
import helpers.file_helper as file_helper
import view.config

# TODO Create statepanelclass

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

    button_bool["rewind_video"] = False

    if not view.config.videoobject:
        info_message("Warning", "Please import video first!")

        return

    if button_bool["play_video"]:
        button_play.configure(text="Stop")
        button_rewind.configure(text="Rewind")
    else:
        button_play.configure(text="Play")


def button_rewind_switch(button_rewind, button_play):
    """Toggle video rewind function.

    Args:
        button (tkinter button): play and rewind button.
    """
    if not view.config.videoobject:
        info_message("Warning", "Please import video first!")

        return

    button_bool["rewind_video"] = not button_bool["rewind_video"]

    button_bool["play_video"] = False

    if button_bool["rewind_video"]:
        button_rewind.configure(text="Stop")
        button_play.configure(text="Play")
    else:
        button_rewind.configure(text="Rewind")


def button_line_switch(button_linedetector, button_polygondetector):
    """Prints information on the statepanel when linedetector button is pressed.

    Args:
        button (tkinter button): Buttons.
        statepanel (textfield.class): Shows information.
    """
    button_bool["linedetector_toggle"] = not button_bool["linedetector_toggle"]

    button_bool["polygondetector_toggle"] = False

    if button_bool["linedetector_toggle"]:
        button_linedetector.configure(text="Finish")
        button_polygondetector.configure(text="Add Polygon")
        # statepanel.update_statepanel(statepanel_txt["Linedetector_information"])
    else:
        button_linedetector.configure(text="Add Line")
        # statepanel.update_statepanel("")


def button_polygon_switch(button_polygondetector, button_linedetector):
    """Prints information on the statepanel when Polygondetector button is pressed.

    Args:
        button (tkinter button): Buttons.
        statepanel (textfield.class): Shows information.
    """

    button_bool["polygondetector_toggle"] = not button_bool["polygondetector_toggle"]

    button_bool["linedetector_toggle"] = False

    if button_bool["polygondetector_toggle"]:
        button_polygondetector.configure(text="Finish")
        button_linedetector.configure(text="Add Line")
        # statepanel.update_statepanel(
        #     "left click to create new polygoncorner\nmousewheelbutton to undo"
        #     + " corner\nrightclock to close polygon\nenter to finish creation process"
        # )
    else:
        button_polygondetector.configure(text="Add Polygon")


def button_display_tracks_switch(button_display_tracks):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): Button.
    """

    if not file_helper.tracks:

        info_message("Warning", "No tracks imported")

        return

    button_bool["display_all_tracks_toggle"] = not button_bool[
        "display_all_tracks_toggle"
    ]

    if button_bool["display_all_tracks_toggle"]:
        button_display_tracks.configure(text="Hide all Tracks")
    else:
        button_display_tracks.configure(text="Show all Tracks")


def button_display_bb_switch(button_display_bb):
    """Toggles the display of trajectories.

    Args:
        button (tkinter button): Button.
    """
    if not file_helper.tracks:

        info_message("Warning", "No tracks imported")

        return

    button_bool["display_bb"] = not button_bool["display_bb"]

    if button_bool["display_bb"]:
        button_display_bb.configure(text="Hide Bboxes")
    else:
        button_display_bb.configure(text="Show Bboxes")


def button_display_live_track_switch(button_display_tracks):
    """Toggles the live-display of trajectories while playing video.

    Args:
        button (tkinter button): Buttons.
    """

    if not file_helper.tracks:

        info_message("Warning", "No tracks imported!")

        return

    button_bool["display_live_track"] = not button_bool["display_live_track"]

    if button_bool["display_live_track"]:
        button_display_tracks.configure(text="Hide Tracks")
    else:
        button_display_tracks.configure(text="Show Tracks")


def info_message(title, text):

    messagebox.showinfo(title=title, message=text)
