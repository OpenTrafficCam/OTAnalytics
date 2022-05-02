import tkinter

import cv2
import numpy as np
from view.helpers.gui_helper import (
    button_bool,
    color_dict,
)
from PIL import Image, ImageTk
import view.config
import helpers.file_helper as file_helper
from view.sections import draw_line, draw_polygon


def manipulate_image(np_image=None, closing=False):
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
        np_image = view.config.videoobject.np_image.copy()

    if button_bool["tracks_imported"]:

        np_image = draw_tracks(
            np_image,
            selectionlist=file_helper.selectionlist_objects,
            tracks=file_helper.tracks_df,
        )

        np_image = draw_bounding_box(
            np_image,
            str(view.config.videoobject.current_frame),
            raw_detections=file_helper.raw_detections,
        )

        np_image = draw_tracks_live(
            np_image,
            view.config.videoobject.current_frame,
            tracks=file_helper.tracks,
            raw_detections=file_helper.raw_detections,
            track_live=file_helper.tracks_live,
        )

    if button_bool["display_all_tracks_toggle"] and button_bool["tracks_imported"]:

        if view.config.videoobject.transparent_image is None:

            view.config.videoobject.transparent_image = draw_all_tracks()

        np_image = cv2.addWeighted(
            view.config.videoobject.transparent_image, 0.5, np_image, 1, 0
        )

    # TODO: #59 Draw detectors on top of all elements
    np_image = draw_detectors_from_dict(np_image)

    # copy is important or else original image will be changed

    # The variable photo is a local variable which gets garbage collected after the
    # class is instantiated. Save a reference to the photo
    # photo is attribute of video

    if button_bool["linedetector_toggle"]:

        np_image = draw_line(np_image)

    if button_bool["polygondetector_toggle"]:

        np_image = draw_polygon(np_image, closing)

    image = Image.fromarray(np_image)  # to PIL format

    view.config.videoobject.ph_image = ImageTk.PhotoImage(image)

    view.config.maincanvas.create_image(
        0, 0, anchor=tkinter.NW, image=view.config.videoobject.ph_image
    )

    view.config.maincanvas.update()


def draw_all_tracks():

    np_image = np.zeros(
        [view.config.videoobject.height, view.config.videoobject.width, 4],
        dtype=np.uint8,
    )

    for index, track in file_helper.tracks_df.iterrows():

        try:
            trackcolor = color_dict[track["Class"]] + (200,)
        except NameError:
            trackcolor = (
                0,
                0,
                255,
            ) + (150,)

        pts = np.array(track["Coord"], np.int32)

        pts = pts.reshape((-1, 1, 2))

        np_image = cv2.polylines(np_image, [pts], False, color=trackcolor, thickness=2)
    return np_image


def draw_detectors_from_dict(np_image):
    """Draws detectors on every frame.

    Args:
        np_image (numpy_array): image as numpy array

    Returns:
        np_image (numpy_array): returns manipulated image"""

    if file_helper.flow_dict["Detectors"]:

        Line = "line"

        for detector in file_helper.flow_dict["Detectors"]:
            if file_helper.flow_dict["Detectors"][detector]["type"] == Line:
                start_x = file_helper.flow_dict["Detectors"][detector]["start_x"]
                start_y = file_helper.flow_dict["Detectors"][detector]["start_y"]
                end_x = file_helper.flow_dict["Detectors"][detector]["end_x"]
                end_y = file_helper.flow_dict["Detectors"][detector]["end_y"]
                color = file_helper.flow_dict["Detectors"][detector]["color"]

                np_image = cv2.line(
                    np_image, (start_x, start_y), (end_x, end_y), color, 3
                )

            else:

                # don't know why
                image = np_image
                overlay = image.copy()

                polypoints = file_helper.flow_dict["Detectors"][detector]["points"]
                color = file_helper.flow_dict["Detectors"][detector]["color"]

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

    if selectionlist:
        df = tracks.loc[selectionlist]

        for index, row in df.iterrows():

            try:
                trackcolor = color_dict[row["Class"]] + (200,)
            except NameError:

                trackcolor = (0, 0, 255, 150)

            pts = np.array(row["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    return np_image


def draw_bounding_box(np_image, frame, raw_detections):
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

                    anno_txt = f"{class_txt} {confidence_txt}"
                    # anno_txt = f"{class_txt} {detection} {confidence_txt}"

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
                        bbcolor = color_dict[
                            raw_detections[frame][detection]["class"]
                        ] + (255,)

                    except ValueError:
                        bbcolor = (0, 0, 255, 255)

                    cv2.rectangle(
                        image_cache,
                        (
                            int(x_start * view.config.videoobject.x_resize_factor),
                            int(y_start * view.config.videoobject.y_resize_factor),
                        ),
                        (
                            int(x_end * view.config.videoobject.x_resize_factor),
                            int(y_end * view.config.videoobject.y_resize_factor),
                        ),
                        bbcolor,
                        2,
                    )

                    text_size, _ = cv2.getTextSize(
                        anno_txt, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1
                    )

                    text_w, text_h = text_size

                    cv2.rectangle(
                        image_cache,
                        (
                            int(x_start * view.config.videoobject.x_resize_factor) - 1,
                            int(y_start * view.config.videoobject.y_resize_factor) - 1,
                        ),
                        (
                            int(x_start * view.config.videoobject.x_resize_factor)
                            + text_w
                            + 2,
                            int(y_start * view.config.videoobject.y_resize_factor)
                            - text_h
                            - 2,
                        ),
                        bbcolor,
                        -1,
                    )

                    image = cv2.putText(
                        image_cache,
                        anno_txt,
                        (
                            int(x_start * view.config.videoobject.x_resize_factor),
                            int(y_start * view.config.videoobject.y_resize_factor) - 2,
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontscale,
                        (255, 255, 255),
                        1,
                    )

        return image

    except ImportError:
        return image


def draw_tracks_live(np_image, frame, tracks, raw_detections, track_live):
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

                    trackcolor = color_dict[tracks[object]["Class"]] + (255,)

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


def create_intersection_list(current_line_shape):

    if button_bool["tracks_imported"] and button_bool["display_all_tracks_toggle"]:

        intersect_series = file_helper.tracks_geoseries.intersects(current_line_shape)

        file_helper.selectionlist_objects = [
            i for i in intersect_series.index if intersect_series[i]
        ]
