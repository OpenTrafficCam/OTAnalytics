from tkinter import filedialog

import cv2
from PIL import Image, ImageTk

# import the necessary packages
from threading import Thread
import sys
import time

if sys.version_info >= (3, 0):
    from queue import Queue


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
    print("filepath: " + filepath)

    return Video(filepath)


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
        print("Thread_backward started")

        return self

    def start_thread_forward(self):
        # start a thread to read frames from the file video stream
        self.thread_forward.start()
        self.stopped = False
        print("Thread_forward started")

        return self

    def update(self, direction):
        print("update thread")
        # keep looping infinitely
        backward_looper = self.current_frame

        self.stream.set(1, self.current_frame)

        while True:
            # if the thread indicator variable is set,
            # stop the thread

            if self.stopped:
                break

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

        # self.stream.release()
        print("Thread stopped")

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

    def stop_thread_backward(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released
        # (producer thread might be still grabbing frame)
        self.thread_backward.join()
        print("thread_backward killed")


class Video(FileVideoStream):
    """Videoclass that gets created on importing video."""

    # object which contains relevant information of the video
    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)

        self.filename = filepath.split("/")[-1]

        # start a thread to read frames from the file video stream
        self.start_thread_forward()
        time.sleep(1)

        # opens video source
        # self.cap = cv2.VideoCapture(self.filepath)
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)

        # retrieve dimensions of video
        self.width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.totalframecount = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))

        # time between two frames
        self.frame_delay = 1 / self.fps

    def get_frame(self, np_image):

        # when imported set current frame to 0
        # self.cap.set(1, self.current_frame)

        print("Frame: " + str(self.current_frame))

        frame = self.read()

        self.np_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # to RGB

        if np_image:

            return self.np_image

        # copy is important or else original image will be changed
        image = Image.fromarray(self.np_image.copy())  # to PIL format

        # The variable photo is a local variable which gets garbage collected after the
        # class is instantiated. Save a reference to the photo
        self.ph_image = ImageTk.PhotoImage(image)  # to ImageTk format

        print("creating image worked")

        return self.ph_image

    def set_frame(self):

        self.stream.set(1, self.current_frame)

        ret, frame = self.stream.read()

        print("Cap set:" + str(ret))

        self.np_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return self.np_image
