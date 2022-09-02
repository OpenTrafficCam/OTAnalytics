import tkinter

import cv2
import numpy as np
from view.helpers.gui_helper import (
    button_bool,
    color_dict,
)
from PIL import Image, ImageTk
import view.objectstorage
import helpers.file_helper as file_helper
from view.sections import draw_line, draw_polygon
from helpers.config import bbox_factor_reference
import time


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
    if not view.objectstorage.videoobject:
        return

    if np_image is None:
        np_image = view.objectstorage.videoobject.np_image.copy()
        
    if button_bool["tracks_imported"]:

        np_image = draw_tracks(
            np_image,
            selectionlist=file_helper.selectionlist_objects,
            tracks_df=file_helper.tracks_df,
        )

        # np_image = draw_bounding_box(
        #     np_image,
        #     str(view.objectstorage.videoobject.current_frame),
        #     raw_detections=file_helper.raw_detections,
        # )
        np_image = draw_bounding_box_with_df(view.objectstorage.videoobject.current_frame,np_image )

        np_image = draw_tracks_live_with_df(view.objectstorage.videoobject.current_frame,np_image)

        # np_image = draw_tracks_live(
        #     np_image,
        #     view.objectstorage.videoobject.current_frame,
        #     tracks=file_helper.tracks_dic,
        #     raw_detections=file_helper.raw_detections,
        #     track_live=file_helper.tracks_live,
        # )

    if button_bool["display_all_tracks_toggle"] and button_bool["tracks_imported"]:

        if view.objectstorage.videoobject.transparent_image is None:

            # creates transparent_image and draws all tracks on it
            # so all tracks dont have to be drawn everytime
            view.objectstorage.videoobject.transparent_image = draw_all_tracks()

        np_image = cv2.addWeighted(
            view.objectstorage.videoobject.transparent_image, 0.5, np_image, 1, 0
        )

    # copy is important or else original image will be changed

    # The variable photo is a local variable which gets garbage collected after the
    # class is instantiated. Save a reference to the photo
    # photo is attribute of video

    

    if button_bool["linedetector_toggle"]:

        np_image = draw_line(np_image)

    if button_bool["polygondetector_toggle"]:

        np_image = draw_polygon(np_image, closing)

    np_image = draw_detectors_from_dict(np_image)

    image = Image.fromarray(np_image)  # to PIL format

    view.objectstorage.videoobject.ph_image = ImageTk.PhotoImage(image)

    view.objectstorage.maincanvas.create_image(
        0, 0, anchor=tkinter.NW, image=view.objectstorage.videoobject.ph_image
    )

    view.objectstorage.maincanvas.update()


def draw_all_tracks():

    np_image = np.zeros(
        [
            view.objectstorage.videoobject.height,
            view.objectstorage.videoobject.width,
            4,
        ],
        dtype=np.uint8,
    )

    for index, track in file_helper.tracks_df.iterrows():
        try:
            trackcolor = color_dict[track["Class"]] + (200,)
        except:
            print("Class not found")
            trackcolor = (
                0,
                0,
                255)+(150,)

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


def draw_tracks(np_image, selectionlist, tracks_df):
    """Draw selected tracks.

    Args:
        np_image (numpy_array): Numpy image from videoobject or opencv function.
        selectionlist (list): List created from selection of tracks in listboxwidget.
        tracks (dictionary): Dictionary with track coords and frames.

    Returns:
        np_image (numpy_array): manipulated array
    """

    if selectionlist:
        tracks_df = tracks_df.loc[selectionlist]

        for index, row in tracks_df.iterrows():

            try:
                trackcolor = color_dict[row["Class"]] + (200,)
            except:

                trackcolor = (0, 0, 255, 150)

            pts = np.array(row["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    return np_image

def draw_bounding_box_with_df(frame, np_image):

    if not button_bool["display_bb"]:
        return np_image
    #start_time = time.time()

    df = file_helper.tracks_df.loc[(file_helper.tracks_df['first_appearance_frame'] <= frame) & (file_helper.tracks_df['last_appearance_frame'] >= frame)]

    #print(df)

    for index, row in df.iterrows():
        try:
            index_of_frame = row["Frame"].index(frame)
            coordinates = row["Coord"][index_of_frame]
            width = row["Width"][index_of_frame]
            height = row["Height"][index_of_frame]
            vehicle_class = row["Class"]
            confidence = row["Confidence"][index_of_frame]
            np_image = draw_bb_from_coordinates(coordinates[0], coordinates[1], width, height, np_image, vehicle_class, confidence)

        except:
            continue


    #print("--- %s seconds ---" % (time.time() - start_time))

    return np_image

    

def draw_bb_from_coordinates(x,y,w,h, np_image, vehicle_class, confidence):

    x_start = int(x - w / 2)

    y_start = int(y- h /2)

    x_end = int(x + w /2)

    y_end = int(y + h /2)

    vehicle_class = vehicle_class

    bbcolor = color_dict[vehicle_class] + (255,)

    cv2.rectangle(
        np_image,
        (
            int(
                x_start * view.objectstorage.videoobject.x_resize_factor
            ),
            int(
                y_start * view.objectstorage.videoobject.y_resize_factor
            ),
        ),
        (
            int(x_end * view.objectstorage.videoobject.x_resize_factor),
            int(y_end * view.objectstorage.videoobject.y_resize_factor),
        ),
        bbcolor,
        2,
    )

    if w < 0.3 * 100:
        fontscale = 0.3
    elif w > 0.5 * 100:
        fontscale = 0.5
    else:
        fontscale = w / 100

    class_txt = vehicle_class
    confidence_txt = "{:.2f}".format((confidence))
    anno_txt = f"{class_txt} {confidence_txt}"

    text_size, _ = cv2.getTextSize(anno_txt, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)

    text_w, text_h = text_size
    cv2.rectangle(
                        np_image,
                        (
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            )
                            - 1,
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            )
                            - 1,
                        ),
                        (
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            )
                            + text_w
                            + 2,
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            )
                            - text_h
                            - 2,
                        ),
                        bbcolor,
                        -1,
                    )
    cv2.putText(np_image,
                        anno_txt,
                        (
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            ),
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            )
                            - 2,
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontscale,
                        (255, 255, 255),
                        1,
                    )
    draw_reference_cross(np_image,x, y, w, h, vehicle_class)

    return np_image



def draw_bounding_box(np_image, frame, raw_detections):
    # sourcery skip: low-code-quality
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
                    
                    x = raw_detections[frame][detection]["x"]
                    y = raw_detections[frame][detection]["y"]
                    w = raw_detections[frame][detection]["w"]
                    h = raw_detections[frame][detection]["h"]
                    vehicle_class = raw_detections[frame][detection]["class"]

                    x_start = int(
                        x
                        - w / 2
                    )

                    y_start = int(
                        y
                        - h / 2
                    )

                    x_end = int(
                        x
                        + w / 2
                    )

                    y_end = int(
                        y
                        + h / 2
                    )

                    try:
                        bbcolor = color_dict[
                            vehicle_class
                        ] + (255,)

                    except ValueError:
                        bbcolor = (0, 0, 255, 255)

                    cv2.rectangle(
                        image_cache,
                        (
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            ),
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            ),
                        ),
                        (
                            int(x_end * view.objectstorage.videoobject.x_resize_factor),
                            int(y_end * view.objectstorage.videoobject.y_resize_factor),
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
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            )
                            - 1,
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            )
                            - 1,
                        ),
                        (
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            )
                            + text_w
                            + 2,
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            )
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
                            int(
                                x_start * view.objectstorage.videoobject.x_resize_factor
                            ),
                            int(
                                y_start * view.objectstorage.videoobject.y_resize_factor
                            )
                            - 2,
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontscale,
                        (255, 255, 255),
                        1,
                    )
                    draw_reference_cross(image,x, y, w, h, vehicle_class)


        return image

    except ImportError:
        return image


def draw_reference_cross(image, x, y, w, h, vehicle_class):

    x_reference_point = int(x - 0.5 * w + w * bbox_factor_reference[vehicle_class][0])
    y_reference_point = int(y - 0.5 * h + h * bbox_factor_reference[vehicle_class][1])

    x_reference_point = int(x_reference_point*view.objectstorage.videoobject.x_resize_factor)
    y_reference_point = int(y_reference_point*view.objectstorage.videoobject.y_resize_factor)

    cv2.line(image, (x_reference_point-5, y_reference_point+5), (x_reference_point+5, y_reference_point-5), (255, 0, 0, 255), 2)
    cv2.line(image, (x_reference_point-5, y_reference_point-5), (x_reference_point+5, y_reference_point+5), (255, 0, 0, 255), 2)


def draw_tracks_live_with_df(frame, np_image):
    #subset dataframe
    if button_bool["tracks_imported"] and button_bool["play_video"] and button_bool["display_live_track"]:
        df = file_helper.tracks_df.loc[(file_helper.tracks_df['first_appearance_frame'] <= frame) & (file_helper.tracks_df['last_appearance_frame'] >= frame)]

        for index, row in df.iterrows():
            try:
                index_of_frame = row["Frame"].index(frame)
                vehicle_class = row["Class"]
                trackcolor = color_dict[vehicle_class] + (255,)

                list_of_points = row["Coord"][(index_of_frame-5):index_of_frame]

                pts = np.array(list_of_points, np.int32)

                pts = pts.reshape((-1, 1, 2))

                np_image = cv2.polylines(
                    np_image, [pts], False, color=trackcolor, thickness=2
                )
            except:
                continue

    return np_image

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
    """creates list with crossed tracks while drawing polygon or linedetectors.

    Args:
        current_line_shape (_type_): polygon or line
    """

    if button_bool["tracks_imported"] and button_bool["display_all_tracks_toggle"]:

        intersect_series = file_helper.tracks_geoseries.intersects(current_line_shape)

        file_helper.selectionlist_objects = [
            i for i in intersect_series.index if intersect_series[i]
        ]
