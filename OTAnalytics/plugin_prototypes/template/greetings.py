from typing import Iterable

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.domain.event import Event
from OTAnalytics.plugin_ui.main_application import ApplicationStarter


class EnglishGreeter:
    def say_hello(self) -> None:
        print("Hello Prototype!")


class GermanGreeter:
    def say_hello(self) -> None:
        print("Hallo Prototyp!")


class EventPrinter:
    def print_all_events(self, events: Iterable[Event]) -> None:
        for event in events:
            print(event)


def build_otanalytics_application() -> OTAnalyticsApplication:
    starter = ApplicationStarter()

    datastore = starter._create_datastore()
    track_state = starter._create_track_state()
    track_view_state = starter._create_track_view_state(datastore)
    section_state = starter._create_section_state()
    intersect = starter._create_intersect()
    scene_event_detection = starter._create_scene_event_detection()
    return OTAnalyticsApplication(
        datastore=datastore,
        track_state=track_state,
        track_view_state=track_view_state,
        section_state=section_state,
        intersect=intersect,
        scene_event_detection=scene_event_detection,
    )


otanalytics = build_otanalytics_application()
