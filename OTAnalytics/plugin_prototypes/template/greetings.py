from typing import Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.plugin_ui.main_application import ApplicationStarter

otanalytics = ApplicationStarter().build_application()


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
