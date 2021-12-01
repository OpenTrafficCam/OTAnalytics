button_bool = {
    "linedetector_toggle": True,
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


def button_play_video_toggle(button_play, button_rewind):
    """Toggle video play function.

    Args:
        button (tkinter button): ...
    """
    button_bool["play_video"] = not button_bool["play_video"]

    if button_bool["play_video"]:
        button_play.config(text="Stop")
        button_rewind.config(text="Rewind")
    else:
        button_play.config(text="Play")

    print("test")


def button_rewind_video_toggle(button_rewind, button_play):
    """Summary.

    Args:
        button (tkinter button): ...
    """
    button_bool["rewind_video"] = not button_bool["rewind_video"]

    if button_bool["rewind_video"]:
        button_rewind.config(text="Stop")
        button_play.config(text="Play")
    else:
        button_rewind.config(text="Rewind")
