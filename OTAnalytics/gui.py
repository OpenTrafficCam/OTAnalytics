import tkinter as tk
from tkinter.constants import ANCHOR, END
import cv2
import PIL
from PIL import Image, ImageTk
from tkinter import Button, Toplevel, filedialog
import json
import ast
import numpy as np


class MainWindow(tk.Frame):
    def __init__(self, master):
        # dictionary of videoobjects
        self.videos = {}
        # dictionary of linedetectors, include id, start point, end point
        self.linedetectors = {}
        self.linepoints = []
        # dictionary of linedetectors, include id, start point, end point
        self.polygondetectors = {}

        self.movement_dict = {}
        self.videoobject = None
        # auxilery list for polygondetector creation/ gets deleted after polygon creation
        self.polypoints = []
        # auxilery list of polygonline/ gets deleted after polygon creation
        #self.polylineid_list = []   

        self.imagelist = []

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        self.drawing=False # true if mouse is pressed
        self.mode=True # if True, draw rectangle. Press 'm' to toggle to curve
        

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
        self.Listbox2.bind('<<ListboxSelect>>', self.curselected_detetector)
        

        self.Button4 = tk.Button(self.frame, text="Line", command= lambda: MainWindow.draw_line_opencv(self))
        self.Button4.grid(row=3, column=0, sticky="ew")

        self.ButtonPoly = tk.Button(self.frame, text="Polygon", command= lambda: MainWindow.new_polygondetector_button(self))
        self.ButtonPoly.grid(row=3, column=1, sticky="ew")

        self.Button5 = tk.Button(self.frame,text="Rename")
        self.Button5.grid(row=3, column=2, sticky="ew")

        self.Button6 = tk.Button(self.frame,text="Remove", command= lambda: MainWindow.delete_detector(self))
        self.Button6.grid(row=3, column=3, sticky="ew")

        self.Button7 = tk.Button(self.frame,text="Clear")
        self.Button7.grid(row=3, column=4, sticky="ew")

        self.Button8 = tk.Button(self.frame,text="Save", command= lambda: MainWindow.save_detectors(self))
        self.Button8.grid(row=3, column=5, sticky="ew")

        self.Button9 = tk.Button(self.frame,text="Load", command= lambda: MainWindow.load_detectors(self))
        self.Button9.grid(row=3, column=6, sticky="ew")

        self.Button9 = tk.Button(self.frame,text="Add to movement", command=lambda: MainWindow.add_to_movement(self) )
        self.Button9.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.Listbox3 = tk.Listbox(self.frame, width=25, exportselection=False)
        self.Listbox3.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.Listbox3.bind('<<ListboxSelect>>', self.curselected_movement)

        self.Listbox4 = tk.Listbox(self.frame, width=25)
        self.Listbox4.grid(row=5, column=3, columnspan=4, sticky="ew")

        self.Button10 = tk.Button(self.frame,text="New",command = lambda: MainWindow.new_movement(self))
        self.Button10.grid(row=6, column=0, sticky="ew")

        self.Button11 = tk.Button(self.frame,text="Rename")
        self.Button11.grid(row=6, column=1, sticky="ew")

        self.Button12 = tk.Button(self.frame,text="Remove")
        self.Button12.grid(row=6, column=2, sticky="ew")

        self.Button13 = tk.Button(self.frame,text="Clear")
        self.Button13.grid(row=6, column=3, sticky="ew")

        self.Button14 = tk.Button(self.frame,text="Save", command= lambda: MainWindow.save_movements(self))
        self.Button14.grid(row=6, column=4, sticky="ew")

        self.Button15 = tk.Button(self.frame,text="Load")
        self.Button15.grid(row=6, column=5, sticky="ew")


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

        self.imagelist.append(self.image_original)

        # puts image on canvas
        self.canvas = tk.Canvas(self.frame, width=self.videoobject.width, height=self.videoobject.height, bg="white")
        self.canvas.bind("<ButtonPress-1>", self.get_coordinates_opencv)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>")
        self.canvas.bind("<ButtonPress-3>", self.on_rightbutton_press)
        self.canvas.bind("<ButtonPress-2>", self.on_middlebutton)

        self.canvas.grid(row= 0,rowspan=7,column=7, sticky="n")

        # puts the image from the videosourse on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        # fills listbox with added video
        self.recieve_videoname(self.Listboxvideo, self.videoobject.filename)

        #self.statepanel = StatePanel(self.master,row=2, column=)

    def get_coordinates_opencv(self,event):

            if len(self.linepoints) == 2:
                self.linepoints = []

            # uses mouseevents to get coordinates (left button)
            self.x = int(self.canvas.canvasx(event.x))
            self.y = int(self.canvas.canvasy(event.y))

            linepoints = (self.x, self.y)

            self.linepoints.append(linepoints)

            self.draw_line_opencv()


    def draw_line_opencv(self):

        if len(self.linepoints) == 2:

            #creates new image from last saved image to the imagelist

            self.new_image = cv2.line(self.imagelist[-1].copy(),self.linepoints[0],self.linepoints[1],(255,0,0),5)

            self.image = Image.fromarray(self.new_image.copy()) # to PIL format
            self.image = ImageTk.PhotoImage(self.image) # to ImageTk format 

            #self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.image))
            self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)

            self.after_drawing_line_opencv()

    def after_drawing_line_opencv(self):
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

    def on_close(self):
        """deletes polygon or line on canvas if no name is entered and toplevelwindow is closed
        """

        #if self.new_linedetector_creation_buttonClicked == True:
        if self.detector_name_entry.get() == "":

            self.image_original = Image.fromarray(self.imagelist[-1]) # to PIL format
            self.image = ImageTk.PhotoImage(self.image_original.copy()) # to ImageTk format 

        #self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.image))
            self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW)


        if self.new_polygondetector_creation_buttonClicked == True:
            if self.detector_name_entry.get() == "":
                self.canvas.delete(self.polygonid)

                self.polylineid_list = []
                self.polypoints = []

        self.new_detector_creation.destroy()

    def recieve_detectorname(self):
        # takes the new created section and adds it to the listbox

        self.detector_name = self.detector_name_entry.get()

        #if self.new_linedetector_creation_buttonClicked == True:
            
        self.linedetectors[self.detector_name]= {'type': 'line', 'start_x': self.linepoints[0][0], 'start_y': self.linepoints[0][1], 'end_x': self.linepoints[1][0], 'end_y': self.linepoints[1][1]}

        # after creation of detector is successfull save new image to imagelist
        self.imagelist.append(self.new_image)


        # if self.new_polygondetector_creation_buttonClicked == True:
            
        #     self.polygondetectors[self.detector_name] ={'type': 'polygon',"id": self.polygonid, "Points": self.polypoints}
            
        #     self.polypoints = []

        self.Listbox2.insert(0,self.detector_name)

        self.new_detector_creation.destroy()

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

    def curselected_detetector(self, event):

        self.widget = event.widget
        self.selection=self.widget.curselection()

        detector_name = self.widget.get(self.selection[0])
        
        self.reset_detector_color()

        if detector_name in self.linedetectors.keys():

            id = self.linedetectors[detector_name]["id"]
            self.canvas.itemconfig(id, fill="blue") # change color


        if detector_name in self.polygondetectors.keys():

            id = self.polygondetectors[detector_name]["id"]
            self.canvas.itemconfig(id, fill="blue") # change color

    def reset_detector_color(self):
        """iterates over line or polygon dictionary,takes id and changes color of line
        or polygon to red
        """

        if self.linedetectors:
            for linedetector, attributes in self.linedetectors.items():
                
                id = attributes["id"]
                self.canvas.itemconfig(id, fill="red")

        if self.polygondetectors:
            for polygondetector, attributes in self.polygondetectors.items():
                id = attributes["id"]
                self.canvas.itemconfig(id,outline="red" ,fill="orange")  


    def new_linedetector_button(self):
        """if the button for the creation of linedector is clicked the buttontext changes and bool:
        self.new_linedetector_creation_buttonClicked changes status
        """

        self.new_linedetector_creation_buttonClicked = not self.new_linedetector_creation_buttonClicked
        
        if self.new_linedetector_creation_buttonClicked == True and self.new_polygondetector_creation_buttonClicked == False:
            self.Button4.config(text="Finish")
            self.statepanel.update("keep left mouse-button pressed to draw line detector on canvas")
        else: 
            self.Button4.config(text="Line")
            self.statepanel.update("")

    def new_polygondetector_button(self):
        """if the button for the creation of linedector is clicked the buttontext changes and bool:
        self.new_polygondetector_creation_buttonClicked changes status
        """

        self.new_polygondetector_creation_buttonClicked = not self.new_polygondetector_creation_buttonClicked
        
        if self.new_polygondetector_creation_buttonClicked == True and self.new_linedetector_creation_buttonClicked == False:
            self.ButtonPoly.config(text="Finish")
            self.statepanel.update("left click to create new polyogon corner\nmiddle button to delete previous corner\nright click to close polygon")
        else: self.ButtonPoly.config(text="Polygon")

    def on_leftbutton_press(self, event):
        """draw a line either for a linesection or polygon section

        Args:
            event (Leftbutton-Press): [recieves the coordinates on the canvas]
        """
        # save mouse drag start position /linedetector
        if self.new_linedetector_creation_buttonClicked == True:

            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)

            self.x = self.y = 0

            self.lineid = self.canvas.create_line(self.x, self.y, 1, 1,fill="red", width=2)

        # save mouse drag start position /polygondetector       
        if self.new_polygondetector_creation_buttonClicked == True:

            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)

            # appends the List of points needed for the creation of the polygon
            self.polypoints.append((self.start_x, self.start_y))

            # creates lines using all the points from pointlist which appends with each mouseclick
            for i in range(len(self.polypoints) - 1):
                #self.polygonid = self.canvas.create_polygon(self.polypoints, outline="red", width=2, fill="red")
                self.polylineid = self.canvas.create_line(self.polypoints[i], self.polypoints[i + 1],fill="red", width=2)
                self.polylineid_list.append(self.polylineid)



    def on_rightbutton_press(self,event):
        """closes the polygon while in polygoncreation mode

        Args:
            event (rightbutton-click): only creates polygon when there are more than 2 point-tuple is the pointlist
            draws a last line from last two first point coordinates in list ==> if successfull
            creates toplevel with entry for the detector name
            when add button is pressed than dictionary entry is created and detector is inserted in detectorlistbox
            deletion process:
                drawn lines to indicate polygon 
                and also the list with the polygonlineids
                listofpoints for the creation of the polygon    
                
        """
        if self.new_polygondetector_creation_buttonClicked == True:

            if len(self.polypoints) >= 3:

                if self.new_polygondetector_creation_buttonClicked == True:
                    self.polylineid = self.canvas.create_line(self.polypoints[-1], self.polypoints[0],fill="red", width=2)
                    self.polylineid_list.append(self.polylineid)

                self.polygonid = self.canvas.create_polygon(self.polypoints, outline="red", width=2, fill="orange", stipple="gray50")


                self.new_detector_creation = Toplevel()
                self.new_detector_creation.title("Create new section")
                self.detector_name_entry = tk.Entry(self.new_detector_creation, textvariable="Sectionname")
                self.detector_name_entry.grid(row=1, column=0, sticky="w",pady=10, padx=10)
                self.detector_name_entry.delete(0, END)
                self.add_section = tk.Button(self.new_detector_creation,text="Add section", command= self.recieve_detectorname)
                self.add_section.grid( row=1, column=1, sticky="w", pady=10, padx=10)
            
                self.new_detector_creation.protocol("WM_DELETE_WINDOW",  self.on_close)

                for i in self.polylineid_list:
                    self.canvas.delete(i)

                self.polylineid_list = []

    def on_move_press(self, event):
        # expands the line in linedetectorcreationmode

        if self.new_linedetector_creation_buttonClicked == True:

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

        


    def on_middlebutton(self, event):
        """delete last line and points on canvas

        Args:
            event (middlebutton): middlebutton because keyboard doesnt work somehow
        """
        if self.polypoints :

            del self.polypoints[-1]

        if self.polylineid_list :

            self.canvas.delete(self.polylineid_list[-1])

            del self.polylineid_list[-1]

        else:
            print("Nothing to delete")

    def recieve_videoname(self,Listbox, filename):
      
        Listbox.insert(0, filename)



    def delete_detector(self):
        """Buttoncommand to delete detectors from list and canvas
        BUG: ONLY WORKS WHEN DETECTIONCREATION BUTTON IS TOGGLED ELSE PROGRAMM COLLAPSE
        """
        # deletes selected linedetectors from dic; listbox2; canvas

        self.detector_name=self.Listbox2.get(self.Listbox2.curselection())
        self.Listbox2.delete(self.Listbox2.curselection())

        if self.new_linedetector_creation_buttonClicked == True: #WRONG
            self.canvas.delete(self.linedetectors[self.detector_name]["id"])

            del self.linedetectors[self.detector_name]

        if self.new_polygondetector_creation_buttonClicked == True: #WRONG

            self.canvas.delete(self.polygondetectors[self.detector_name]["id"])

            del self.polygondetectors[self.detector_name]

    def save_detectors(self):
        files = [('Files', '*.OTSect')]
        file = filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        a_file = open(file.name, "w")


        json.dump([self.linedetectors, self.polygondetectors], a_file)

        a_file.close()


    def load_detectors(self):
        """loads detectors from a .OTSect-File 
        """

        filepath = filedialog.askopenfile(filetypes=[("Detectors", '*.OTSect')])   
        files = open(filepath.name, "r")
        files = files.read()

        loaded_dict = json.loads(files)

        self.linedetectors.update(loaded_dict[0])
        self.polygondetectors.update(loaded_dict[1])

        self.draw_detector_from_dict()

        # resets polypoints list or else creation of new polygon leads to bug
        self.polypoints = []

        print(self.linedetectors)



    def draw_detector_from_dict(self):

        self.Listbox2.delete(0,'end')

        for self.detector_name, values in self.linedetectors.items():

            self.start_x = values["start_x"]
            self.end_x = values["end_x"]
            self.start_y = values["start_y"]
            self.end_y = values["end_y"]

            self.lineid = self.canvas.create_line(self.start_x, self.start_y, self.end_x, self.end_y,fill="red", width=2)

            #overwrites the id with the true canvas id
            values["id"] = self.lineid

            self.Listbox2.insert(0,self.detector_name)

        for self.detector_name, values in self.polygondetectors.items():
            self.polypoints = values["Points"]
            self.polygonid = self.canvas.create_polygon(self.polypoints, outline="red", width=2, fill="orange", stipple="gray50")

            #overwrites the id with the true canvas id
            values["id"] = self.polygonid

            self.Listbox2.insert(0,self.detector_name)

    def new_movement(self):
        """creates new movement and adds it to the movement listbox
        """
        self.new_movement_creation = Toplevel()

        self.new_movement_creation.title("Create new movement")
        self.movement_name_entry = tk.Entry(self.new_movement_creation, textvariable="Movement")
        self.movement_name_entry.grid(row=1, column=0, sticky="w",pady=10, padx=10)
        self.movement_name_entry.delete(0, END)
        self.add_movement = tk.Button(self.new_movement_creation,text="Add movement", command= self.recieve_movement_name)
        self.add_movement.grid( row=1, column=1, sticky="w", pady=10, padx=10)   
        self.new_movement_creation.protocol("WM_DELETE_WINDOW")


    def recieve_movement_name(self):
        self.movement_name = self.movement_name_entry.get()
        self.Listbox3.insert(0,self.movement_name)
        self.movement_dict[self.movement_name] = {}

        self.new_movement_creation.destroy()

    def add_to_movement(self):
        """when movement is highlighted in the listbox, it is possible
         to add detectors and sections to the selected movement
        """

        detector_selection = self.Listbox2.curselection()
        detector_name = self.Listbox2.get(detector_selection[0])

        movement_selection = self.Listbox3.curselection()
        self.movement_name = self.Listbox3.get(movement_selection[0])

        if detector_name in self.linedetectors:

            self.movement_dict[self.movement_name].update({detector_name : self.linedetectors[detector_name]})

        else:
            self.movement_dict[self.movement_name].update({detector_name : self.polygondetectors[detector_name]})

        #self.movement_dict[self.movement_name].append(detector_name)

        self.Listbox4.insert(0, detector_name)

        print(self.movement_dict)


    def curselected_movement(self, event):
        #shows detectors and sections belonging to selected movement         

        self.Listbox4.delete(0,'end')

        movement_selection = self.Listbox3.curselection()
        self.movement_name = self.Listbox3.get(movement_selection[0])

        for detector_name in self.movement_dict[self.movement_name]:
            self.Listbox4.insert(0, detector_name)

    def save_movements(self):
        files = [('Files', '*.OTMov')]
        file = filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        a_file = open(file.name, "w")


        json.dump(self.movement_dict, a_file)

        a_file.close()

    def load_movements(self):
        # insert in list 2,3
        # draw on canvas
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