import cv2
from PIL import Image, ImageTk
from tkinter import Toplevel, filedialog


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
    video_source = video_source.name

    return Video(video_source)


class Video:
    """Videoclass that gets created on importing video."""

    # objekt which contains relevant information of the video
    def __init__(self, filepath):

        # self.id = id
        self.filepath = filepath
        self.filename = filepath.split("/")[-1]

        # opens video source
        self.cap = cv2.VideoCapture(self.filepath)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        # retrieve dimensions of video
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.totalframecount = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # time between two frames
        self.frame_delay = 1 / self.fps

        self.current_frame = 0

    def get_frame(self, np_image):

        # when imported set current frame to 0
        self.cap.set(1, self.current_frame)

        self.np_image = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB)  # to RGB

        if np_image:

            return self.np_image

        # copy is important or else original image will be changed
        image = Image.fromarray(self.np_image.copy())  # to PIL format

        # The variable photo is a local variable which gets garbage collected after the
        # class is instantiated. Save a reference to the photo
        self.ph_image = ImageTk.PhotoImage(image)  # to ImageTk format

        print("creating image worked")

        return self.ph_image
