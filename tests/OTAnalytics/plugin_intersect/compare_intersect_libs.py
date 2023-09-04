from pathlib import Path

from OTAnalytics.adapter_ui.default_values import TRACK_LENGTH_LIMIT
from OTAnalytics.application.datastore import Datastore, TrackToVideoRepository
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_parser.otvision_parser import (
    CachedVideoParser,
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
    PullingProgressbarBuilder,
    PullingProgressbarPopupBuilder,
)
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader


def create_data_store() -> Datastore:
    track_repository = TrackRepository()
    section_repository = SectionRepository()
    flow_repository = FlowRepository()
    event_repository = EventRepository()
    track_to_video_repository = TrackToVideoRepository()
    video_repository = VideoRepository()

    flow_parser = OtFlowParser()
    event_list_parser = OtEventListParser()
    video_parser = CachedVideoParser(SimpleVideoParser(MoviepyVideoReader()))
    track_video_parser = OttrkVideoParser(video_parser)
    track_parser = OttrkParser(
        CalculateTrackClassificationByMaxConfidence(),
        track_repository,
        track_length_limit=TRACK_LENGTH_LIMIT,
    )
    config_parser = OtConfigParser(video_parser, flow_parser)

    progressbar = PullingProgressbarBuilder(PullingProgressbarPopupBuilder())

    return Datastore(
        track_repository,
        track_parser,
        section_repository,
        flow_parser,
        flow_repository,
        event_repository,
        event_list_parser,
        track_to_video_repository,
        video_repository,
        video_parser,
        track_video_parser,
        progressbar,
        config_parser,
    )


def load_data() -> Datastore:
    print("loading data")
    datastore = create_data_store()
    datastore.load_track_file(
        Path(r"D:\ptm\data\Standard_SCUEHQ_FR30_2022-09-15_07-00-00.ottrk")
    )
    print("finished loading tracks")

    datastore.load_otflow(Path(r"D:\ptm\data\flows.otflow"))
    print("finished loading sections/flows")

    return datastore


if __name__ == "__main__":
    data = load_data()
    print("tracks:", len(data.get_all_tracks()))
    print("sections:", len(data.get_all_sections()))
    print("flows:", len(data.get_all_flows()))
