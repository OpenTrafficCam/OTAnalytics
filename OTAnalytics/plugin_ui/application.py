import tkinter
from abc import abstractmethod

import customtkinter
from application.datastore import Datastore
from customtkinter import CTk, CTkButton
from plugin_parser.otvision_parser import OttrkParser


class OTAnalyticsApplication:
    def __init__(self) -> None:
        self.datastore: Datastore

    def add_tracks_of_file(self) -> None:
        track_file = ""  # TODO read from file chooser
        self.datastore.load_track_file(file=track_file)

    def start(self) -> None:
        self.setup_application()
        self.start_internal()

    @abstractmethod
    def start_internal(self) -> None:
        pass

    def setup_application(self) -> None:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser()
        self.datastore = Datastore(track_parser)


class OTAnalyticsCli(OTAnalyticsApplication):
    def __init__(self) -> None:
        pass

    def start_internal(self) -> None:
        pass


class OTAnalyticsGui(OTAnalyticsApplication):
    def __init__(self) -> None:
        self.app: CTk

    def add_tracks_of_file(self) -> None:
        track_file = ""  # TODO read from file chooser
        self.datastore.load_track_file(file=track_file)

    def start(self) -> None:
        self.setup_application()
        self.show_gui()

    def show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.app = CTk()
        self.app.geometry("800x600")

        self.add_track_loader()

        self.app.mainloop()

    def add_track_loader(self) -> None:
        button = CTkButton(
            master=self.app,
            text="Read tracks",
            command=self.add_tracks_of_file,
        )
        button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
