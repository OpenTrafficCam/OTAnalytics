import tkinter as tk
from tkinter import filedialog
import cv2
import PIL.Image, PIL.ImageTk
import time


class Controlpanel:
    def __init__(self, padx, side, anchor):
        self.button1 = tk.Button(text="play")
        self.button2 = tk.Button(text="stop")

        self.button1.pack(padx=padx, side=side, anchor=anchor)
        self.button2.pack(padx=padx, side=side, anchor=anchor)


class Sidepanel:
    def __init__(self, padx, side, anchor):
        self.button1 = tk.Button(text="load", command=App.load_video)
        self.button2 = tk.Button(text="save")

        self.button1.pack(padx=padx, side=side, anchor=anchor)
        self.button2.pack(padx=padx, side=side, anchor=anchor)


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.window.geometry("1000x950")

        self.sidepanel = Sidepanel(5, "right", "n")
        self.controlpanel = Controlpanel(5, "left", "n")

        self.general = init_general_dict()

        # open video source (by default this will try to open the computer webcam)
        self.vid = Video(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def load_video():
        video_source = filedialog.askopenfile(filetypes=("all video format", ".mp4"))


# class for videos, including the file itself
class Video:
    def __init__(self, filepath, startdatetime, id_):
        # Open the video source
        self.video_file = cv2.VideoCapture(filepath)
        # not None for no errors during multiprocessing, where the video_file gets
        # set to "multiprocessing" to not copy the video for each process
        #  (if video file is None, isOpened function cant be called)
        if self.video_file != "multiprocessing" and not self.video_file.isOpened():
            raise ValueError("Unable to open video source", filepath)

        # Get video source width and height
        self.width = self.video_file.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.video_file.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.video_file.get(cv2.CAP_PROP_FPS)
        self.frames = self.video_file.get(cv2.CAP_PROP_FRAME_COUNT)
        self.startdatetime = startdatetime
        # self.current_frame = 0
        self.corner_angles_list = None  # later and only for radial
        self.id_ = id_
        self.path = filepath
        # get duration (ms) of the video
        # self.video_file.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        self.duration = self.frames / self.fps * 1000
        # set back to start
        # self.video_file.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
        self.last_showen_frame = None
        self.current_CAP_PROP_POS_MSEC = -10000

        print(
            "id: "
            + str(self.id_)
            + ", filpath: "
            + str(self.path)
            + ", width: "
            + str(self.width)
            + ", height:"
            + str(self.height)
            + ", duration: "
            + str(self.duration)
            + " ms"
            + ", fps: "
            + str(self.fps)
            + ", frames: "
            + str(self.frames)
        )

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.video_file != "multiprocessing" and self.video_file.isOpened():
            self.video_file.release()
            # self.window.mainloop()

    # get frame from the file
    def get_frame(self, app):
        if self.video_file.isOpened():
            if app.general["active_modul"] == "mtc":
                # if it is just a small step in the same video --> change by grab()
                # because grab is way faster than always set the wanted time
                if 1100 > app.mtc["video_state"]["current_timeskip"] > 0:
                    frames_to_skip = round(
                        app.mtc["video_state"]["current_timeskip"] / (1000 / self.fps)
                    )
                    if frames_to_skip > 1:
                        for i in range(frames_to_skip - 1):
                            self.video_file.grab()
                # get the frame
                i = 2
                while True:
                    ret, frame = self.video_file.read()
                    # take the frame only if the current time
                    # position changed or it is on the beginning of
                    # the video (no changes expected)
                    # break the loop than
                    if (
                        self.video_file.get(cv2.CAP_PROP_POS_MSEC)
                        != self.current_CAP_PROP_POS_MSEC
                        or self.video_file.get(cv2.CAP_PROP_POS_MSEC) <= 150
                    ):
                        break
                    # if it should go backward but didnt change the position
                    # (sometimes the case for some reason, results in no time pos change),
                    # the timeskip size have to be changed by set
                    # if it shoulw go forward, read() is enough to change the
                    # position in the next duration (but read only can go forward)
                    if app.mtc["video_state"]["current_timeskip"] < 0:
                        self.video_file.set(
                            cv2.CAP_PROP_POS_MSEC,
                            self.current_CAP_PROP_POS_MSEC - 100 * i,
                        )
                    # increase i to increase the backward timeskip with every duration
                    i += 1
                app.mtc["video_state"]["current_timeskip"] = 0
            # ot (just get the start frame, nothing else to do)
            else:
                ret, frame = self.video_file.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)


def init_general_dict():
    return {
        "video": None,  # current video
        "junction": None,
        "active_modul": "mtc",
        # "previous_modul":None,???
        "count_name": None,
        "click_counter": None,
        # names --> later a boolean if the boxes for the counting have names beside increasing numbers
        "names_boolean": None,
        "gate_assignment_finished": False,
        # modes: radial, two_clicks, any_number_clicks
        "mode": None,
        "load_filepath": None,
    }


# Create a window and pass it to the Application object
App(tk.Tk(), "tk and OpenCV")
