from application.datastore import Datastore
from domain.track import CalculateTrackClassificationByMaxConfidence
from plugin_parser.otvision_parser import (
    OtEventListParser,
    OtsectionParser,
    OttrkParser,
    OttrkVideoParser,
)
from plugin_ui.application import OTAnalyticsCli, OTAnalyticsGui
from plugin_ui.dummy_viewmodel import DummyViewModel


class ApplicationStarter:
    def start_gui(self) -> None:
        datastore = self.create_datastore()
        dummy_viewmodel = DummyViewModel(datastore=datastore)
        OTAnalyticsGui(datastore, dummy_viewmodel).start()

    def start_cli(self) -> None:
        datastore = self.create_datastore()
        OTAnalyticsCli(datastore).start()

    def create_datastore(self) -> Datastore:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser(CalculateTrackClassificationByMaxConfidence())
        section_parser = OtsectionParser()
        event_list_parser = OtEventListParser()
        video_parser = OttrkVideoParser()
        return Datastore(track_parser, section_parser, event_list_parser, video_parser)
