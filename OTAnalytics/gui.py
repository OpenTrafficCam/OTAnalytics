import tkinter as tk
from tkinter.constants import ANCHOR
import cv2
from PIL import Image, ImageTk
from tkinter import Button, Toplevel, filedialog


class MainWindow(tk.Frame):
    def __init__(self, master):
        self.videos = {}
        self.detectors = {}
        self.videoobject = None

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")
        #self.master.geometry("1000x600")
        self.new_detector_creation_buttonClicked = False
 
        self.Listbox1 = tk.Listbox(self.frame)
        self.Listbox1.grid(row=0, column=0, columnspan=6, sticky="ew")
        self.Listbox1.bind('<<ListboxSelect>>',self.CurSelet)

        self.Button1 = tk.Button(self.frame,text="Add", command= lambda: MainWindow.load_video_and_frame(self))
        self.Button1.grid(row=1, column=0, sticky="w")

        self.Button2 = tk.Button(self.frame,text="Remove")
        self.Button2.grid(row=1, column=1 ,columnspan=2, sticky="w")

        self.Button3 = tk.Button(self.frame,text="Clear")
        self.Button3.grid(row=1, column=2, sticky="w")

        self.Listbox2 = tk.Listbox(self.frame)
        self.Listbox2.grid(row=2, column=0, columnspan=6, sticky="ew")

        self.Button4 = tk.Button(self.frame, text="New", command= lambda: MainWindow.new_detector_button(self))
        self.Button4.grid(row=3, column=0, sticky="w")

        self.Button5 = tk.Button(self.frame,text="Rename")
        self.Button5.grid(row=3, column=1, sticky="w")

        self.Button6 = tk.Button(self.frame,text="Remove", command= lambda: MainWindow.delete_detector(self))
        self.Button6.grid(row=3, column=2, sticky="w")

        self.Button7 = tk.Button(self.frame,text="Clear")
        self.Button7.grid(row=3, column=3, sticky="w")

        self.Button8 = tk.Button(self.frame,text="Save")
        self.Button8.grid(row=3, column=4, sticky="w")

        self.Button9 = tk.Button(self.frame,text="Load")
        self.Button9.grid(row=3, column=5, sticky="w")

        self.Button9 = tk.Button(self.frame,text="Add to movement")
        self.Button9.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.Listbox3 = tk.Listbox(self.frame, width=25)
        self.Listbox3.grid(row=5, column=0, columnspan=3, sticky="ew")

        self.Listbox4 = tk.Listbox(self.frame, width=25)
        self.Listbox4.grid(row=5, column=3, columnspan=3, sticky="ew")

        self.Button10 = tk.Button(self.frame,text="New")
        self.Button10.grid(row=6, column=0, sticky="w")

        self.Button11 = tk.Button(self.frame,text="Rename")
        self.Button11.grid(row=6, column=1, sticky="w")

        self.Button12 = tk.Button(self.frame,text="Remove")
        self.Button12.grid(row=6, column=2, sticky="w")

        self.Button13 = tk.Button(self.frame,text="Clear")
        self.Button13.grid(row=6, column=3, sticky="w")

        self.Button14 = tk.Button(self.frame,text="Save")
        self.Button14.grid(row=6, column=4, sticky="w")

        self.Button15 = tk.Button(self.frame,text="Load")
        self.Button15.grid(row=6, column=5, sticky="w")


    def load_video_and_frame(self):
        # opens dialog to load video file
        video_source = filedialog.askopenfile(filetypes=[("Videofiles", '*.mkv')])       
        video_source = video_source.name
        video_name = video_source.split('/')[-1]


        # creates Videoobject
        # key is the name of the object
        self.videos[video_name] = Video(video_source)
        self.videoobject = self.videos[video_name]

    

        # creates image from video
        self.image = cv2.cvtColor(self.videoobject.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        self.image = Image.fromarray(self.image) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format

        # puts image on canvas
        self.canvas = tk.Canvas(self.frame, width=self.videoobject.width, height=self.videoobject.height, bg="white")
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.grid(row= 0,rowspan=6,column=7, sticky="n")

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        # fills listbox with added video
        self.recieve_videoname(self.Listbox1, self.videoobject.filename)

        print(self.videoobject)

    def CurSelet(self, event):
        # return selected videoname, puts frame of selected image on canvas
        self.widget = event.widget
        self.selection=self.widget.curselection()

        video_name = self.widget.get(self.selection[0])

        #print(video_name)
        self.videoobject = self.videos[video_name]

        # creates image from video
        self.image = cv2.cvtColor(self.videoobject.cap.read()[-1], cv2.COLOR_BGR2RGB) # to RGB
        self.image = Image.fromarray(self.image) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def new_detector_button(self):

        self.new_detector_creation_buttonClicked = not self.new_detector_creation_buttonClicked
        
        if self.new_detector_creation_buttonClicked == True:
            self.Button4.config(text="Finish")
        else: self.Button4.config(text="New")

        print(self.new_detector_creation_buttonClicked)


    def on_button_press(self, event):
        # save mouse drag start position

        if self.new_detector_creation_buttonClicked == True:

            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)

            self.x = self.y = 0

            self.lineid = self.canvas.create_line(self.x, self.y, 1, 1)

    def on_move_press(self, event):

        if self.new_detector_creation_buttonClicked == True:

            self.end_x = self.canvas.canvasx(event.x)
            self.end_y = self.canvas.canvasy(event.y)

            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if event.x > 0.9*w:
                self.canvas.xview_scroll(1, 'units') 
            elif event.x < 0.1*w:
                self.canvas.xview_scroll(-1, 'units')
            if event.y > 0.9*h:
                self.canvas.yview_scroll(1, 'units') 
            elif event.y < 0.1*h:
                self.canvas.yview_scroll(-1, 'units')

            # expand rectangle as you drag the mouse
            self.canvas.coords(self.lineid, self.start_x, self.start_y, self.end_x, self.end_y)    

    def on_button_release(self, event):

        if self.new_detector_creation_buttonClicked == True:

            self.new_detector_creation = Toplevel()
            #self.new_detector_creation.geometry("200x200")
            self.new_detector_creation.title("Create new section")
            self.detector_name_entry = tk.Entry(self.new_detector_creation, textvariable="Sectionname")
            self.detector_name_entry.grid(row=1, column=0, sticky="w",pady=10, padx=10)
            self.add_section = tk.Button(self.new_detector_creation,text="Add section", command= self.recieve_detectorname)
            self.add_section.grid( row=1, column=1, sticky="w", pady=10, padx=10)

    def recieve_videoname(self,Listbox, filename):
      
        Listbox.insert(0, filename)

    def recieve_detectorname(self):

        self.detector_name = self.detector_name_entry.get()
        self.detectors[self.detector_name]= {'id': self.lineid, 'start_x': self.start_x, 'start_y': self.start_y, 'end_x': self.end_x, 'end_y': self.end_y}
        self.Listbox2.insert(0,self.detector_name)


        print(self.detectors[self.detector_name])

    def delete_detector(self):
        # deletes selected detectors from dic; listbox2; canvas

        self.detector_name=self.Listbox2.get(self.Listbox2.curselection())
        self.Listbox2.delete(self.Listbox2.curselection())
        self.canvas.delete(self.detectors[self.detector_name]["id"])

        del self.detectors[self.detector_name]

 


class Video:
    # objekt which contains relevant information of the video
    def __init__(self, filepath) -> None:

        #self.id = id
        self.filepath = filepath
        self.filename = filepath.split('/')[-1]

        #opens video source
        self.cap = cv2.VideoCapture(self.filepath)

        # retrieve dimensions of video
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)




def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()