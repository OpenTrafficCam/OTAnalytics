import tkinter as tk
from tkinter.constants import ANCHOR, END
import cv2
import PIL
from PIL import Image, ImageTk
from tkinter import Button, Toplevel, filedialog
import json
import ast
import numpy as np
from gui_dict import *
from sections import get_coordinates_opencv
from movement import new_movement, add_to_movement, curselected_movement
from sections import save_file, draw_line, load_file
from tracks import load_tracks
import time

class MainWindow(tk.Frame):
    def __init__(self, master):
        # dictionary of videoobjects
        self.videos = {}
        # dictionary of linedetectors, include id, start point, end point
        self.linepoints = [(0,0),(0,0)]
        # dictionary of linedetectors, include id, start point, end point
        self.polygondetectors = {}

        self.flow_dict = {}
        self.flow_dict["Detectors"] = {}
        self.flow_dict["Movements"] = {}
        self.object_dict = {}
        self.videoobject = None

        self.interval = 20

        self.tracks = {}

        # auxilery list for polygondetector creation/ gets deleted after polygon creation
        self.polypoints = []

        #imagelist with original and altered images, zeros are placeholder
        self.imagelist = [0,0]

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        self.Listboxvideo = tk.Listbox(self.frame)
        self.Listboxvideo.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.Listboxvideo.bind('<<ListboxSelect>>',self.curselected_video)

        self.Buttonaddvideo = tk.Button(self.frame,text="Add", command= lambda: MainWindow.load_video_and_frame(self))
        self.Buttonaddvideo.grid(row=1, column=0, sticky="ew")

        self.ButtonPlayVideo = tk.Button(self.frame,text="Play", command= lambda: [MainWindow.update_image(self), button_play_video_toggle(self.ButtonPlayVideo)])
        self.ButtonPlayVideo.grid(row=1, column=1 ,columnspan=1, sticky="ew")

        self.Button3 = tk.Button(self.frame,text="Clear")
        self.Button3.grid(row=1, column=2, sticky="ew")

        self.ListboxDetector = tk.Listbox(self.frame)
        self.ListboxDetector.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.ListboxDetector.bind('<<ListboxSelect>>', self.curselected_detetector)  

        self.ListboxTracks = tk.Listbox(self.frame, selectmode='multiple', exportselection=False)
        self.ListboxTracks.grid(row=2, column=3, columnspan=4, sticky="ew")
        self.ListboxTracks.bind('<<ListboxSelect>>', self.curselected_track) 

        self.ButtonLine = tk.Button(self.frame, text="Line", command= lambda: button_information_line(self.ButtonLine, self.statepanel))
        self.ButtonLine.grid(row=3, column=0, sticky="ew")

        self.ButtonPoly = tk.Button(self.frame, text="Polygon", command= lambda: button_information_polygon(self.ButtonPoly, self.statepanel))
        self.ButtonPoly.grid(row=3, column=1, sticky="ew")

        self.Button5 = tk.Button(self.frame,text="Rename")
        self.Button5.grid(row=3, column=2, sticky="ew")

        self.ButtonDeleteDetector = tk.Button(self.frame,text="Remove", command= lambda: MainWindow.delete_selected_detector(self))
        self.ButtonDeleteDetector.grid(row=3, column=3, sticky="ew")

        self.ButtonDisplayTracks = tk.Button(self.frame,width= 10, text="show tracks", command= lambda: [button_display_tracks_toggle(self.ButtonDisplayTracks), self.draw_from_dict()])
        self.ButtonDisplayTracks.grid(row=3, column=4, sticky="ew")

        self.Button9 = tk.Button(self.frame,text="Add to movement", command=lambda: add_to_movement(self.ListboxDetector,self.ListboxMovement, self.flow_dict["Detectors"],self.polygondetectors, self.flow_dict["Movements"], self.ListBoxMovement) )
        self.Button9.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.ButtonLoadTracks = tk.Button(self.frame,text="Load tracks", command = lambda: [load_tracks(self.object_dict, self.ListboxTracks), self.draw_from_dict()])
        self.ButtonLoadTracks.grid(row=4, column=3, columnspan=4, sticky="ew")

        self.ListBoxMovement = tk.Listbox(self.frame, width=25)
        self.ListBoxMovement.grid(row=5, column=3, columnspan=4, sticky="ew")

        self.ButtonNewMovement = tk.Button(self.frame,text="New",command = lambda: new_movement(self.ListboxMovement, self.flow_dict["Movements"]))
        self.ButtonNewMovement.grid(row=6, column=0, sticky="ew")

        self.Button11 = tk.Button(self.frame,text="Rename")
        self.Button11.grid(row=6, column=1, sticky="ew")

        self.Button12 = tk.Button(self.frame,text="Remove")
        self.Button12.grid(row=6, column=2, sticky="ew")

        self.Button13 = tk.Button(self.frame,text="Clear")
        self.Button13.grid(row=6, column=3, sticky="ew")

        self.ButtonSaveFlow = tk.Button(self.frame,text="Save", command= lambda: save_file(self.flow_dict, self.flow_dict["Detectors"], self.flow_dict["Movements"]))
        self.ButtonSaveFlow.grid(row=6, column=4, sticky="ew")

        self.ButtonLoadFlow = tk.Button(self.frame,text="Load", command= lambda: [load_file(self.flow_dict["Detectors"],self.flow_dict["Movements"], self.ListboxDetector, self.ListboxMovement), self.draw_from_dict()])
        self.ButtonLoadFlow.grid(row=6, column=5, sticky="ew")

        self.ListboxMovement = tk.Listbox(self.frame, width=25, exportselection=False)
        self.ListboxMovement.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.ListboxMovement.bind('<<ListboxSelect>>', lambda event: curselected_movement(event, self.ListBoxMovement,self.ListboxMovement, self.flow_dict["Movements"], self.statepanel))

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
        self.image_original = cv2.cvtColor(self.videoobject.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        # copy is important or else original image will be changed
        self.image = Image.fromarray(self.image_original.copy()) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format

        self.imagelist[0] = self.image_original

        # puts image on canvas
        self.canvas = tk.Canvas(self.frame, width=self.videoobject.width, height=self.videoobject.height, bg="white")
        #prevents canvas from scrolling
        self.canvas.configure(scrollregion=(0,0,self.videoobject.width,self.videoobject.height))
        self.canvas.bind("<ButtonPress-1>", lambda event: get_coordinates_opencv(event,self.linepoints, self.canvas))
        self.canvas.bind("<B1-Motion>",self.draw_line_with_mousedrag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<ButtonPress-3>")
        self.canvas.bind("<ButtonPress-2>")

        self.canvas.grid(row= 0,rowspan=7,column=7, sticky="n")

        # puts the image from the videosourse on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        # fills listbox with added video
        filename = self.videoobject.filename

        self.Listboxvideo.insert(0, filename)

    def update_image(self):
        # Get the latest frame and convert image format

            self.image_original = cv2.cvtColor(self.videoobject.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB

            self.imagelist[0] = self.image_original

            self.draw_from_dict()

            self.frame.after(self.interval, self.update_image)
    
    def draw_tracks_from_dict(self):

        # if detectors exist in dictionary and "display tracks-button" is pressed then use the altered picture

        if gui_dict["display_tracks_toggle"]== True:

            if self.flow_dict["Detectors"]:
                print(bool(self.flow_dict["Detectors"]))

                self.image_cache= self.imagelist[1].copy()

            else: 
                self.image_cache = self.imagelist[0].copy()
                print("this pic is used 0")

            for track in self.object_dict:

                trackcolor = (0,0,255)       

                if self.object_dict[track]["Class"] == "car":
                    trackcolor = (255,0,0)
                if self.object_dict[track]["Class"] == "person":
                    trackcolor = (0,255,0)
                if self.object_dict[track]["Class"] == "motorcycle":
                    trackcolor = (240,248,255)

                pts = np.array(self.object_dict[track]["Coord"], np.int32)

                pts = pts.reshape((-1, 1, 2))

                self.image = cv2.polylines(self.image_cache, [pts], False,color= trackcolor, thickness=2 )

                self.imagelist[1] = self.image_cache
            
                self.image = Image.fromarray(self.image_cache) # to PIL format
                self.image = ImageTk.PhotoImage(self.image) # to ImageTk format 

                self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)

    def curselected_track(self, event):
        """draws on or more selected tracks on canvas

        Args:
            event Listboxmultiselection: all highlighted object_ids will be displayed on canvas as colored tracks
            corresponding to vehicle class
        """

        self.draw_from_dict()
        

        self.widget = event.widget
        multiselection=self.widget.curselection()

        selectionlist = []

        for selection in multiselection:
            entry = self.widget.get(selection)
            selectionlist.append(entry)

        #TODO ZUSAMMENFASSEN!!     

        for object_id in selectionlist:

            trackcolor = (0,0,255)       

            if self.object_dict[object_id]["Class"] == "car":
                trackcolor = (255,0,0)
            if self.object_dict[object_id]["Class"] == "person":
                trackcolor = (0,255,0)
            if self.object_dict[object_id]["Class"] == "motorcycle":
                trackcolor = (240,248,255)


            pts = np.array(self.object_dict[object_id]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            self.image = cv2.polylines(self.image_cache, [pts], False,color= trackcolor, thickness=2 )

            self.imagelist[1] = self.image_cache
        
            self.image = Image.fromarray(self.image_cache) # to PIL format
            self.image = ImageTk.PhotoImage(self.image) # to ImageTk format 

            self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)


    def draw_line_with_mousedrag(self, event):

        if gui_dict["linedetector_toggle"] == True:

            self.end_x = int(self.canvas.canvasx(event.x))
            self.end_y = int(self.canvas.canvasy(event.y))

            self.linepoints[1] = (self.end_x, self.end_y)


            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if event.x > 0.9*w:
                self.canvas.xview_scroll(1, 'units') 
            elif event.x < 0.1*w:
                self.canvas.xview_scroll(-1, 'units')
            if event.y > 0.9*h:
                self.canvas.yview_scroll(1, 'units') 
            elif event.y < 0.1*h:
                self.canvas.yview_scroll(-1, 'units')

            self.image = draw_line(self.flow_dict["Detectors"], self.imagelist, self.linepoints)

            self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)

    def on_button_release(self, event):
        if gui_dict["linedetector_toggle"] == True and len(self.linepoints)==2:

        # creates window to insert name of detector
        #if self.new_linedetector_creation_buttonClicked == True:

            self.new_detector_creation = Toplevel()
            self.new_detector_creation.title("Create new section")
            self.detector_name_entry = tk.Entry(self.new_detector_creation, textvariable="Sectionname")
            self.detector_name_entry.grid(row=1, column=0, sticky="w",pady=10, padx=10)
            self.detector_name_entry.delete(0, END)
            self.add_section = tk.Button(self.new_detector_creation,text="Add section", command= self.recieve_detectorname)
            self.add_section.grid( row=1, column=1, sticky="w", pady=10, padx=10)
        
            self.new_detector_creation.protocol("WM_DELETE_WINDOW",  self.on_close)
            #makes the background window unavailable
            self.new_detector_creation.grab_set()

    def curselected_detetector(self, event):
        """Re draws detectors, where the selected detectors has different color

        Args:
            event (Listboxselection): single listboxselection
        """

        self.widget = event.widget
        self.selection=self.widget.curselection()

        detector_name = self.widget.get(self.selection[0])    

        for dict_key in self.flow_dict["Detectors"].keys():

            if detector_name == dict_key:

                self.flow_dict["Detectors"][detector_name]["color"] = (0,0,255)

            else:
                self.flow_dict["Detectors"][dict_key]["color"] = (255,0,0)


        self.draw_from_dict()

    def on_close(self):
        """deletes polygon or line on canvas if no name is entered and toplevelwindow is closed
        """

        #if self.new_linedetector_creation_buttonClicked == True:
        if self.detector_name_entry.get() == "":

            self.draw_from_dict()

        if self.new_polygondetector_creation_buttonClicked == True:
            if self.detector_name_entry.get() == "":
                self.canvas.delete(self.polygonid)

                self.polylineid_list = []
                self.polypoints = []
        
        self.new_detector_creation.destroy()


    def recieve_detectorname(self):
        #TODO outsource this function
        # takes the new created section and adds it to the listbox

        detector_name = self.detector_name_entry.get()

        if gui_dict["linedetector_toggle"] == True:
            
            self.flow_dict["Detectors"][detector_name]= {'type': 'line', 'start_x': self.linepoints[0][0], 'start_y': self.linepoints[0][1], 'end_x': self.linepoints[1][0], 'end_y': self.linepoints[1][1], 'color': (255,0,0)}

        self.draw_from_dict()

        self.ListboxDetector.insert(0,detector_name)

        self.new_detector_creation.destroy()

    def delete_selected_detector(self):
        #gets selection from listbox
        # delete from dict and re draw detectors on canvas
        detector_name=self.ListboxDetector.get(self.ListboxDetector.curselection())

       
        if gui_dict["linedetector_toggle"] == True: #WRONG      

            self.ListboxDetector.delete(self.ListboxDetector.curselection())    

            del self.flow_dict["Detectors"][detector_name]

            #check if detetector is in movement and delete as well
       
            for movement in self.flow_dict["Movements"]: 
                if detector_name in self.flow_dict["Movements"][movement]:
                    self.flow_dict["Movements"][movement].remove(detector_name)

                    # BUG
                    if self.ListboxMovement.get(self.ListboxMovement.curselection()) == movement:

                        self.ListBoxMovement.delete(0,'end')

                        for detector_name in self.flow_dict["Movements"][movement]:
                            self.ListBoxMovement.insert(0, detector_name)

        
        if not self.flow_dict["Detectors"]:
        # deletes polygon
                self.image = Image.fromarray(self.imagelist[0].copy()) # to PIL format
                self.image = ImageTk.PhotoImage(self.image) # to ImageTk format 

                self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)

        self.draw_from_dict()
        

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
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
    
    def draw_from_dict(self):

        #takes original picture
        self.image_cache= self.imagelist[0].copy()

        if self.flow_dict["Detectors"]:

            for linedetectors in self.flow_dict["Detectors"]:


                    start_x = self.flow_dict["Detectors"][linedetectors]["start_x"]
                    start_y = self.flow_dict["Detectors"][linedetectors]["start_y"]
                    end_x = self.flow_dict["Detectors"][linedetectors]["end_x"]
                    end_y = self.flow_dict["Detectors"][linedetectors]["end_y"]
                    color = self.flow_dict["Detectors"][linedetectors]["color"]

                    self.image_cache = cv2.line(self.image_cache,(start_x,start_y),(end_x,end_y),color,5)
                    self.imagelist[1] = self.image_cache
                
                    self.image = Image.fromarray(self.image_cache) # to PIL format
                    self.image = ImageTk.PhotoImage(self.image) # to ImageTk format 

                    self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)

        else:
            self.image = Image.fromarray(self.image_cache) # to PIL format
            self.image = ImageTk.PhotoImage(self.image) # to ImageTk format 
            self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)

            print("dic is empty")

        self.draw_tracks_from_dict()

 
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

