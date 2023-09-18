from pathlib import Path

from pandas import DataFrame

from OTAnalytics.adapter_ui.default_values import TRACK_LENGTH_LIMIT
from OTAnalytics.application.datastore import Datastore, TrackToVideoRepository
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.progress import NoProgressbarBuilder
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
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PandasTrackProvider,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
    PullingProgressbarBuilder,
    PullingProgressbarPopupBuilder,
)
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader

paths = {
    "small": (
        r"D:\ptm\OTAnalytics\tests\data\Testvideo_"
        + "Cars-Truck_FR20_2020-01-01_00-00-00.ottrk",
        r"D:\ptm\data\flows_small.otflow",
    ),
    "medium": (
        r"D:\ptm\data\Standard_SCUEHQ_FR30_2022-09-15_07-00-00.ottrk",
        r"D:\ptm\data\flows.otflow",
    ),
}


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


def load_data(skip_tracks: bool, size: str = "small") -> Datastore:
    track_path, flow_path = paths.get(size, paths["small"])

    print("loading data")
    datastore = create_data_store()
    if not skip_tracks:
        datastore.load_track_file(Path(track_path))
    print(f"Loaded {len(datastore.get_all_tracks())} tracks.")

    datastore.load_otflow(Path(flow_path))
    print(f"Loaded {len(datastore.get_all_sections())} sections.")

    return datastore


def tracks_as_dataframe(datastore: Datastore) -> DataFrame:
    track_provider = PandasTrackProvider(datastore, NoProgressbarBuilder())
    return track_provider.get_data()
