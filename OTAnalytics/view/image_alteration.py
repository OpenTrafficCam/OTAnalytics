import tkinter

import cv2
import numpy as np
from gui_helper import button_bool, color_dict
from PIL import Image, ImageTk
import config
import file_helper


def manipulate_image(
    np_image=None,
    flowdictionary=None,
    selectionlist=None,
    tracks=None,
    tracks_live=None,
    raw_detections=None,
):
    """Function to draw sections, tracks and bounding boxes on a given numpy image.
    Image is converted to photo image and plotted on tkinter canvas object.

    Args:
        np_image (numpy_array): Numpy image from videoobject or opencv function.
        video (object): Videoobject with important attributes for image manipulation.
        canvas (tkinter.canvas): Canvas to draw photo on.
        flowdictionary (dictionary): Dictionary with sections and movements.
        selectionlist (list): List created from selection of tracks in listboxwidget.
        tracks (dictionary): Dictionary with track coords and frames.
        tracks_live (dictionary): Dictionary with track coords from
        current and last twenty frames.
        raw_detections (dictionary): Dictionary with raw detections from OpenVision.
    """
    if np_image is None:
        np_image = config.videoobject.np_image.copy()

    # TODO: #59 Draw detectors on top of all elements
    np_image = draw_detectors_from_dict(np_image, flowdictionary=file_helper.flow_dict)

    if button_bool["tracks_imported"]:
        np_image = draw_tracks(np_image, selectionlist, tracks)

        np_image = draw_bounding_box(
            np_image, raw_detections, str(config.videoobject.current_frame)
        )

        np_image = draw_tracks_live(
            np_image,
            tracks,
            raw_detections,
            tracks_live,
            config.videoobject.current_frame,
        )

    # copy is important or else original image will be changed
    image = Image.fromarray(np_image)  # to PIL format

    # The variable photo is a local variable which gets garbage collected after the
    # class is instantiated. Save a reference to the photo
    # photo is attribute of video
    config.videoobject.ph_image = ImageTk.PhotoImage(image)

    print(type(config.videoobject.ph_image))

    config.maincanvas.create_image(
        0, 0, anchor=tkinter.NW, image=config.videoobject.ph_image
    )

    config.maincanvas.update()


def draw_detectors_from_dict(np_image, flowdictionary):
    """Draws detectors on every frame.

    Args:
        np_image (numpy_array): image as numpy array

    Returns:
        np_image (numpy_array): returns manipulated image"""

    if flowdictionary["Detectors"]:

        Line = "line"

        for detector in flowdictionary["Detectors"]:
            if flowdictionary["Detectors"][detector]["type"] == Line:
                start_x = flowdictionary["Detectors"][detector]["start_x"]
                start_y = flowdictionary["Detectors"][detector]["start_y"]
                end_x = flowdictionary["Detectors"][detector]["end_x"]
                end_y = flowdictionary["Detectors"][detector]["end_y"]
                color = flowdictionary["Detectors"][detector]["color"]

                np_image = cv2.line(
                    np_image, (start_x, start_y), (end_x, end_y), color, 3
                )

            else:

                # don't know why
                image = np_image
                overlay = image.copy()

                polypoints = flowdictionary["Detectors"][detector]["points"]
                color = flowdictionary["Detectors"][detector]["color"]

                list_of_tuples = [list(elem) for elem in polypoints]
                pts = np.array(list_of_tuples, np.int32)
                pts = pts.reshape((-1, 1, 2))

                np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))

                opacity = 0.4
                np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0)
                np_image = cv2.polylines(np_image, [pts], True, color, 2)

    return np_image


def draw_tracks(np_image, selectionlist, tracks):
    """Draw selected tracks.

    Args:
        np_image (numpy_array): Numpy image from videoobject or opencv function.
        selectionlist (list): List created from selection of tracks in listboxwidget.
        tracks (dictionary): Dictionary with track coords and frames.

    Returns:
        np_image (numpy_array): manipulated array
    """
    if button_bool["display_all_tracks_toggle"] is True:

        for track in tracks:

            try:
                trackcolor = color_dict[tracks[track]["Class"]]
            except NameError:
                trackcolor = (0, 0, 255)

            pts = np.array(tracks[track]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    elif selectionlist:

        for object_id in selectionlist:

            try:
                trackcolor = color_dict[tracks[object_id]["Class"]]
            except NameError:

                trackcolor = (0, 0, 255)

            pts = np.array(tracks[object_id]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    return np_image


def draw_bounding_box(np_image, raw_detections, frame):
    """Draws bounding boxes in every frame.

    Args:
        raw_detections (dictionary): Inputfile with detections from OTVision.
        frame (int): Current frame as index.
        np_image (numpy_image): Arraylike image to draw on.

    Returns:
       np_image: Returns manipulated image.
    """
    if not button_bool["display_bb"]:
        return np_image
    try:
        if raw_detections:

            image_cache = np_image

            for detection in raw_detections[frame]:
                if raw_detections[frame][detection]["class"] in color_dict.keys():

                    class_txt = raw_detections[frame][detection]["class"]

                    confidence_txt = "{:.2f}".format(
                        (raw_detections[frame][detection]["conf"])
                    )

                    anno_txt = class_txt + " " + str(confidence_txt)

                    if raw_detections[frame][detection]["w"] < 0.3 * 100:
                        fontscale = 0.3
                    elif raw_detections[frame][detection]["w"] > 0.5 * 100:
                        fontscale = 0.5
                    else:
                        fontscale = raw_detections[frame][detection]["w"] / 100

                    x_start = int(
                        raw_detections[frame][detection]["x"]
                        - raw_detections[frame][detection]["w"] / 2
                    )

                    y_start = int(
                        raw_detections[frame][detection]["y"]
                        - raw_detections[frame][detection]["h"] / 2
                    )

                    x_end = int(
                        raw_detections[frame][detection]["x"]
                        + raw_detections[frame][detection]["w"] / 2
                    )

                    y_end = int(
                        raw_detections[frame][detection]["y"]
                        + raw_detections[frame][detection]["h"] / 2
                    )

                    try:
                        bbcolor = color_dict[raw_detections[frame][detection]["class"]]

                    except ValueError:
                        bbcolor = (0, 0, 255)

                    cv2.rectangle(
                        image_cache, (x_start, y_start), (x_end, y_end), bbcolor, 2
                    )

                    text_size, _ = cv2.getTextSize(
                        anno_txt, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1
                    )

                    text_w, text_h = text_size

                    cv2.rectangle(
                        image_cache,
                        (x_start - 1, y_start - 1),
                        (x_start + text_w + 2, y_start - text_h - 2),
                        bbcolor,
                        -1,
                    )

                    image = cv2.putText(
                        image_cache,
                        anno_txt,
                        (x_start, y_start - 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontscale,
                        (255, 255, 255),
                        1,
                    )

        return image

    except ImportError:
        return image


def draw_tracks_live(np_image, tracks, raw_detections, track_live, frame):
    """Draw tracks while playing video

    Args:
        object_dict (dictionary): resampled raw detections
        object_live_track (dictionary): dictionary with framewiselive coordinates
        frame (int): current video frame
        raw_detections (dictionary): input file with all detections
        np_image (numpy_array) : arraylike image object

    Returns:
        np_image: returns manipulated image
    """

    if (
        raw_detections
        and button_bool["play_video"]
        and button_bool["display_live_track"]
    ):

        for object in tracks.keys():

            if frame in tracks[object]["Frame"]:

                if not track_live[object]:
                    track_live[object] = [
                        tracks[object]["Coord"][tracks[object]["Frame"].index(frame)]
                    ]

                elif frame < tracks[object]["Frame"][-1]:

                    nextframeindex = tracks[object]["Frame"].index(frame)
                    track_live[object].append(tracks[object]["Coord"][nextframeindex])

                    if len(track_live[object]) >= 20:
                        track_live[object].pop(0)

                    trackcolor = color_dict[tracks[object]["Class"]]

                    pts = np.array(track_live[object], np.int32)

                    pts = pts.reshape((-1, 1, 2))

                    np_image = cv2.polylines(
                        np_image, [pts], False, color=trackcolor, thickness=2
                    )
                # else:
                # not necessary
                #     #if track is drawn completely => erase from canvas
                #     object_live_track[object] = []

    return np_image
