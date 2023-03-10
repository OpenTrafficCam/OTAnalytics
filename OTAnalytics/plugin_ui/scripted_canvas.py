import customtkinter
from customtkinter import CTk, CTkCanvas
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk

app = CTk()
canvas = CTkCanvas(master=app)

video = VideoFileClip(r"tests/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4")
image = video.get_frame(0)
pillow_image = Image.fromarray(image)
width, height = pillow_image.size
canvas.config(width=width, height=height)
pillow_photo_image = ImageTk.PhotoImage(image=pillow_image)
canvas.create_image(0, 0, image=pillow_photo_image, anchor=customtkinter.NW)

canvas.pack()
app.mainloop()
