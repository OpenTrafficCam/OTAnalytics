gui_dict = {
    "linedetector_toggle" : False ,
    "polygondetector_toggle": False,
    "tracks_imported" : False, 
    "detections_drawn": False,
    "display_tracks_toggle": False,
    "play_video": False
}

statepanel_txt = {"Linedetector_information": "press and drag mouse to create a line\nButton needs to be toggled to remove sections",
                    "Add_movement_information": "select and add section while movement is highlighted"}


def button_information_line(button, statepanel):
    """if the button for the creation of linedector is clicked the buttontext changes and bool:
    self.new_linedetector_creation_buttonClicked changes status
    """
    gui_dict["linedetector_toggle"] = not gui_dict["linedetector_toggle"]
    
    if gui_dict["linedetector_toggle"] == True and gui_dict["polygondetector_toggle"] == False:
        button.config(text="Finish")
        statepanel.update(statepanel_txt["Linedetector_information"])
    else: 
        button.config(text="Line")
        statepanel.update("")

def button_information_polygon(button, statepanel):
    """if the button for the creation of linedector is clicked the buttontext changes and bool:
    self.new_polygondetector_creation_buttonClicked changes status
    """

    gui_dict["polygondetector_toggle"] = not gui_dict["polygondetector_toggle"]
    
    if gui_dict["polygondetector_toggle"] == True and gui_dict["linedetector_toggle"] == False:
        button.config(text="Finish")
        statepanel.update("left click to create new polyogon corner\nmiddle button to delete previous corner\nright click to close polygon")
    else: button.config(text="Polygon")

def button_display_tracks_toggle(button):
    gui_dict["display_tracks_toggle"] = not gui_dict["display_tracks_toggle"]

    if  gui_dict["display_tracks_toggle"] == True:
            button.config(text="hide tracks")
    else: button.config(text="show tracks")


def button_play_video_toggle(button):
    gui_dict["play_video"] = not gui_dict["play_video"]

    print(gui_dict["play_video"])

    if  gui_dict["play_video"] == True:
            button.config(text="Play")
    else: button.config(text="Stop")