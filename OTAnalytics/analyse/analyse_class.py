from view.video import Video
import helpers.file_helper as file_helper
import re



class Analyse():
    def __init__(self, filepath_vid : str,**kwargs):
        #necessary videodata

        #get name till dot
        self.filepath_vid = filepath_vid
        self.folder_path = file_helper.get_dir(self.filepath_vid)
        self.videoobject = Video(filepath_vid)

        self.analyse_name = self._get_filename()
        #files
        self.track_file = None

        #necessary track data
        self.raw_detections = None
        self.tracks_dic = {}
        self.tracks_df = None
        self.tracks_geoseries = None

        #check for check_fileexistence
        self.flowfile_existence, self.trackfile_existence, self.track_file = self._corresponding_file_existence()
        
        
        #Analysationresults
        self.eventbased_dictionary = None
        self.tracks_df_result = None

        
    def _get_filename(self):

        m = re.search(r'.*(?=\.)', file_helper.get_filename(self.filepath_vid))
        return str(m.group(0))

    def _corresponding_file_existence(self):
        #patterns
        otflow_pattern, ottrk_pattern = file_helper.create_pattern(self.analyse_name)
        return file_helper.check_fileexistence(self.folder_path, otflow_pattern, ottrk_pattern)

