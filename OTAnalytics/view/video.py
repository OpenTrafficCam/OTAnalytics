import sys
import time
from threading import Thread
from tkinter import filedialog
from tkinter import ttk

import cv2
from PIL import Image, ImageTk
from datetime import datetime
import re

if sys.version_info >= (3, 0):
    from queue import Queue

#can be deleted
def load_video_and_frame():
    """ask for videofile via dialogue
    creates canvas on masterframe with height and width from the videoobject
    first frame is canvas image
    includes mouse motion and button press events
    """
    # opens dialog to load video file
    video_source = filedialog.askopenfile(
        filetypes=[("Videofiles", "*.mkv"), ("Videofiles", "*.mp4")]
    )
    filepath = video_source.name

    checkbox = ttk.Checkbutton

    return Video(filepath), checkbox


class FileVideoStream:
    def __init__(self, path, transform=None):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        self.transform = transform
        self.current_frame = 0

        # initialize the queue used to store frames read from
        # the video file
        self.new_q()
        # initialize thread
        self.new_thread_forward()
        self.new_thread_backward()

    def new_q(self, queue_size=128):
        self.Q = Queue(maxsize=queue_size)

        print("new Queue initiated")

    def new_thread_forward(self):
        self.thread_forward = Thread(target=lambda: self.update(1), args=())
        self.thread_forward.daemon = True

    def new_thread_backward(self):
        self.thread_backward = Thread(target=lambda: self.update(-1), args=())
        self.thread_backward.daemon = True

    def start_thread_backward(self):
        # start a thread to read frames from the file video stream
        self.thread_backward.start()
        self.stopped = False

        return self

    def start_thread_forward(self):
        # start a thread to read frames from the file video stream
        self.thread_forward.start()
        self.stopped = False
        print("forward thread alive")

        return self

    def update(self, direction):
        # keep looping infinitely
        backward_looper = self.current_frame

        self.stream.set(1, self.current_frame)

        while not self.stopped:
            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                if direction == -1 and backward_looper > 0:
                    backward_looper = backward_looper - 1
                    # set cap to read previous frame
                    self.stream.set(1, backward_looper)

                # read the next frame from the file
                (grabbed, frame) = self.stream.read()

                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stopped = True

                # if there are transforms to be done, might as well
                # do them on producer thread before handing back to
                # consumer thread. ie. Usually the producer is so far
                # ahead of consumer that we have time to spare.
                #
                # Python is not parallel but the transform operations
                # are usually OpenCV native so release the GIL.
                #
                # Really just trying to avoid spinning up additional
                # native threads and overheads of additional
                # producer/consumer queues since this one was generally
                # idle grabbing frames.
                if self.transform:
                    frame = self.transform(frame)

                # add the frame to the queue
                self.Q.put(frame)
            else:
                time.sleep(0.1)  # Rest for 10ms, we have a full queue

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of
    # file stream.
    def running(self):
        return self.more() or not self.stopped

    def more(self):
        # return True if there are still frames in the queue.
        # If stream is not stopped try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.1)
            tries += 1

        return self.Q.qsize() > 0

    def stop_thread_forward(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released
        # (producer thread might be still grabbing frame)
        self.thread_forward.join()
        print("thread_forward killed")
        time.sleep(0.1)

    def stop_thread_backward(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released
        # (producer thread might be still grabbing frame)
        self.thread_backward.join()
        print("thread_backward killed")
        time.sleep(0.1)


class Video(FileVideoStream):
    """Videoclass that gets created on importing video."""

    # object which contains relevant information of the video
    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)

        self.filename = filepath.split("/")[-1]


        # start a thread to read frames from the file video stream
        self.start_thread_forward()
        time.sleep(0.1)

        # fps from videofile
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)

        # retrieve dimensions of video
        self.videowidth = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.videoheight = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.video_size_factor = self.videowidth / self.videoheight

        self.width = 800
        self.height = 600

        self.totalframecount = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))

        # time between two frames
        self.frame_delay = 1 / self.fps

        # compute factors for resizing video and files
        if self.videowidth != self.width or self.videoheight != self.height:
            self.need_for_resize = True

            #
            self.y_resize_factor = self.height / self.videoheight
            self.width = int(self.videowidth * self.y_resize_factor)

            self.x_resize_factor = self.width / self.videowidth

        else:
            self.x_resize_factor = 1
            self.y_resize_factor = 1

        self.initialize_empty_image()
        self.datetime_str = self.__get_datetime_from_filename()
        self.__get_datetime_obj()


    def get_frame(self, np_image):
        """Reads frame from videostream.

        Args:
            np_image (bool): bool if return value needs to be photo or array

        Returns:
           array, photoimage: returns pil image or array
        """

        # when imported set current frame to 0
        frame = self.read()

        frame = cv2.resize(frame, (self.width, self.height))

        self.np_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        # Then assign the mask to the last channel of the image
        self.np_image[:, :, 3] = 255

        if np_image:

            return self.np_image

        # copy is important or else original image will be changed
        image = Image.fromarray(self.np_image.copy())  # to PIL format

        # The variable photo is a local variable which gets garbage collected after the
        # class is instantiated. Save a reference to the photo
        self.ph_image = ImageTk.PhotoImage(image)  # to ImageTk format

        return self.ph_image

    def initialize_empty_image(self):
        self.transparent_image = None

    def set_frame(self):
        """Get frame from current video position.

        Returns:
            array: array of current image
        """

        self.stream.set(1, self.current_frame)

        ret, frame = self.stream.read()

        frame = cv2.resize(frame, (self.width, self.height))

        self.np_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        # Then assign the mask to the last channel of the image
        self.np_image[:, :, 3] = 255

        return self.np_image

    def __get_datetime_from_filename(self, epoch_datetime="1970-01-01_00-00-00"):
        """ Get date and time from file name.
        Searches for "_yyyy-mm-dd_hh-mm-ss".
        Returns "yyyy-mm-dd_hh-mm-ss".
        Args:
            filename (str): filename with expression
            epoch_datetime (str): Unix epoch (00:00:00 on 1 January 1970)
        Returns:
            str: datetime
        """
        regex = "_([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_[0-9]{2,2}-[0-9]{2,2}-[0-9]{2,2})"
        match = re.search(regex, self.filename)
        if not match:
            return epoch_datetime

        # Assume that there is only one timestamp in the file name
        self.datetime_str = match.group(1)  # take group withtout underscore

        try:
            datetime.strptime(self.datetime_str, "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            return epoch_datetime

        return self.datetime_str

    def __get_datetime_obj(self):
        self.datetime_obj = datetime.strptime(self.datetime_str, '%Y-%m-%d_%H-%M-%S')

