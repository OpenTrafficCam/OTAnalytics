import tkinter as tk
from tkinter.constants import ANCHOR, END
import cv2
from PIL import Image, ImageTk
from tkinter import Button, Toplevel, filedialog
import json
import ast
import cv2



class MainWindow(tk.Frame):
    def __init__(self, master):
        # dictionary of videoobjects
        self.videos = {}
        # dictionary of linedetectors, include id, start point, end point
        self.linedetectors = {}
        # dictionary of linedetectors, include id, start point, end point
        self.polygondetectors = {}

        self.movement_dict = {}
        self.videoobject = None
        # auxilery list for polygondetector creation/ gets deleted after polygon creation
        self.polypoints = []
        # auxilery list of polygonline/ gets deleted after polygon creation
        self.polylineid_list = []   

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        

        # boolean to toggle line or poly detector creation
        self.new_linedetector_creation_buttonClicked = False
        self.new_polygondetector_creation_buttonClicked = False
 
        self.Listboxvideo = tk.Listbox(self.frame)
        self.Listboxvideo.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.Listboxvideo.bind('<<ListboxSelect>>',self.curselected_video)

        self.Buttonaddvideo = tk.Button(self.frame,text="Add", command= lambda: MainWindow.load_video_and_frame(self))
        self.Buttonaddvideo.grid(row=1, column=0, sticky="ew")

        self.Button2 = tk.Button(self.frame,text="Remove")
        self.Button2.grid(row=1, column=1 ,columnspan=1, sticky="ew")

        self.Button3 = tk.Button(self.frame,text="Clear")
        self.Button3.grid(row=1, column=2, sticky="ew")

        self.Listbox2 = tk.Listbox(self.frame)
        self.Listbox2.grid(row=2, column=0, columnspan=7, sticky="ew")
        self.Listbox2.bind('<<ListboxSelect>>')
        

        self.Button4 = tk.Button(self.frame, text="Line", command= lambda: MainWindow.draw_line)
        self.Button4.grid(row=3, column=0, sticky="ew")

        self.ButtonPoly = tk.Button(self.frame, text="Polygon")
        self.ButtonPoly.grid(row=3, column=1, sticky="ew")

        self.Button5 = tk.Button(self.frame,text="Rename")
        self.Button5.grid(row=3, column=2, sticky="ew")

        self.Button6 = tk.Button(self.frame,text="Remove")
        self.Button6.grid(row=3, column=3, sticky="ew")

        self.Button7 = tk.Button(self.frame,text="Clear")
        self.Button7.grid(row=3, column=4, sticky="ew")

        self.Button8 = tk.Button(self.frame,text="Save")
        self.Button8.grid(row=3, column=5, sticky="ew")

        self.Button9 = tk.Button(self.frame,text="Load")
        self.Button9.grid(row=3, column=6, sticky="ew")

        self.Button9 = tk.Button(self.frame,text="Add to movement")
        self.Button9.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.Listbox3 = tk.Listbox(self.frame, width=25, exportselection=False)
        self.Listbox3.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.Listbox3.bind('<<ListboxSelect>>')

        self.Listbox4 = tk.Listbox(self.frame, width=25)
        self.Listbox4.grid(row=5, column=3, columnspan=4, sticky="ew")

        self.Button10 = tk.Button(self.frame,text="New")
        self.Button10.grid(row=6, column=0, sticky="ew")

        self.Button11 = tk.Button(self.frame,text="Rename")
        self.Button11.grid(row=6, column=1, sticky="ew")

        self.Button12 = tk.Button(self.frame,text="Remove")
        self.Button12.grid(row=6, column=2, sticky="ew")

        self.Button13 = tk.Button(self.frame,text="Clear")
        self.Button13.grid(row=6, column=3, sticky="ew")

        self.Button14 = tk.Button(self.frame,text="Save")
        self.Button14.grid(row=6, column=4, sticky="ew")

        self.Button15 = tk.Button(self.frame,text="Load")
        self.Button15.grid(row=6, column=5, sticky="ew")

        self.display1 = tk.Label(self.frame)
        self.display1.grid(row=1, column=0, padx=10, pady=2)  #Display 1


    def load_video_and_frame(self):
        """ask for videofile via dialogue
        creates canvas on masterframe with height and width from the videoobject
        first frame is canvas image
        includes mouse motion and button press events
        """
        # opens dialog to load video file
        video_source = filedialog.askopenfile(filetypes=[("Videofiles", '*.mkv'), ("Videofiles", '*.mp4')])       
        video_source = video_source.name
        video_name = video_source.split('/')[-1]

        self.statepanel = StatePanel(self.frame, 7,0,sticky="w", columnspan=8)
        self.statepanel.update("statepanel initialized")


        # creates Videoobject
        # key is the name of the object
        self.videos[video_name] = Video(video_source)
        self.videoobject = self.videos[video_name]
    
        # creates image from video
        self.image = cv2.cvtColor(self.videoobject.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        self.image = Image.fromarray(self.image) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format

        display1.imgtk = imgtk #Shows frame for display 1
        display1.configure(image=imgtk)

        # fills listbox with added video
        self.recieve_videoname(self.Listboxvideo, self.videoobject.filename)

 

    def curselected_video(self, event):
        """Selected video from Listboxvideo-Listbox gets displayed on canvas

        Args:
            event (Listselection): Event is the selection via mousepress
        """
        # return selected videoname, puts frame of selected image on canvas
        self.widget = event.widget
        self.selection=self.widget.curselection()

        video_name = self.widget.get(self.selection[0])

        #print(video_name)
        self.videoobject = self.videos[video_name]

        # creates image from video
        self.image = cv2.cvtColor(self.videoobject.cap.read()[-1], cv2.COLOR_BGR2RGB) # to RGB
        self.image = Image.fromarray(self.image) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format'

    def recieve_videoname(self,Listbox, filename):
      
        Listbox.insert(0, filename)

    def draw_line(self):
        pass

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


class StatePanel:
    # initialize StatePanel
    def __init__(self, window, row, column, sticky, columnspan):
        self.scrollbar = tk.Scrollbar(window)
        self.text = tk.Text(window, height=4, width=150, yscrollcommand=self.scrollbar.set, state="disabled")
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.grid(row=row, column=column, columnspan=2, padx='5', pady='3', sticky='e')
        self.text.grid(row=row, column=column, padx='5', pady='3', sticky=sticky, columnspan=columnspan)
    # new information 
    def update(self, text):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert(tk.END, str(text))
        self.text.see("end")
        self.text.config(state="disabled")
    # change position
    def move(self, row, column, sticky, columnspan=2):
        self.scrollbar.grid(row=row, column=column, padx='5', pady='3', sticky='e')
        self.text.grid(row=row, column=column, padx='5', pady='3', sticky=sticky, columnspan=columnspan)


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()