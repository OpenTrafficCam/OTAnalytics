import tkinter
from abc import abstractmethod
from pathlib import Path

import customtkinter
from customtkinter import CTk, CTkButton

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.section import Coordinate, LineSection, Section
from OTAnalytics.plugin_parser.otvision_parser import (
    OtEventListParser,
    OtsectionParser,
    OttrkParser,
    OttrkVideoParser,
)


class OTAnalyticsApplication:
    def __init__(self, datastore: Datastore) -> None:
        self._datastore: Datastore = datastore

    def add_tracks_of_file(self, track_file: Path) -> None:
        self._datastore.load_track_file(file=track_file)

    def add_sections_of_file(self, sections_file: Path) -> None:
        self._datastore.load_section_file(file=sections_file)

    def start(self) -> None:
        self.start_internal()

    @abstractmethod
    def start_internal(self) -> None:
        pass


class OTAnalyticsCli(OTAnalyticsApplication):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def start_internal(self) -> None:
        # TODO parse config and add track and section files
        pass


class OTAnalyticsGui(OTAnalyticsApplication):
    def __init__(self, datastore: Datastore, app: CTk = CTk()) -> None:
        super().__init__(datastore)
        self._app: CTk = app

    def _load_tracks_in_file(self) -> None:
        track_file = Path("")  # TODO read from file chooser
        self._datastore.load_track_file(file=track_file)

    def _load_sections_in_file(self) -> None:
        section_file = Path("")  # TODO read from file chooser
        self._datastore.load_section_file(file=section_file)

    def _save_sections_to_file(self) -> None:
        section_file = Path("")  # TODO read from file choser
        self._datastore.save_section_file(file=section_file)

    def start_internal(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self._app.geometry("800x600")

        self._add_track_loader()
        self._add_section_loader()

        self._app.mainloop()

    def _add_track_loader(self) -> None:
        button = CTkButton(
            master=self._app,
            text="Read tracks",
            command=self._load_tracks_in_file,
        )
        button.place(relx=0.25, rely=0.5, anchor=tkinter.CENTER)

    def _add_section_loader(self) -> None:
        button = CTkButton(
            master=self._app,
            text="Read sections",
            command=self._load_sections_in_file,
        )
        button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    def _add_section_button(self) -> None:
        button = CTkButton(
            master=self._app,
            text="Add sections",
            command=self._add_section,
        )
        button.place(relx=0.75, rely=0.5, anchor=tkinter.CENTER)

    def _add_section(self) -> None:
        section: Section = LineSection(
            id="north",
            start=Coordinate(0, 1),
            end=Coordinate(2, 3),
        )
        self._datastore.add_section(section)


class ApplicationStarter:
    def start_gui(self) -> None:
        datastore = self.create_datastore()
        OTAnalyticsGui(datastore).start()

    def start_cli(self) -> None:
        datastore = self.create_datastore()
        OTAnalyticsCli(datastore).start()

    def create_datastore(self) -> Datastore:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser()
        section_parser = OtsectionParser()
        event_list_parser = OtEventListParser()
        video_parser = OttrkVideoParser()
        return Datastore(track_parser, section_parser, event_list_parser, video_parser)
