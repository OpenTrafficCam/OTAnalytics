import datetime
from pathlib import Path

from OTAnalytics.application.datastore import Datastore, TrackToVideoRepository
from OTAnalytics.application.plotting import LayeredPlotter
from OTAnalytics.application.state import Plotter, TrackViewState
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_parser.otvision_parser import (
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    MatplotlibTrackPlotter,
    PandasTrackProvider,
    PlotterPrototype,
    SectionGeometryPlotter,
    TrackBackgroundPlotter,
    TrackGeometryPlotter,
    TrackStartEndPointPlotter,
)
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader
from tests.profiling import profile

CLASS_CAR = "car"
CLASS_MOTORCYCLE = "motorcycle"
CLASS_PERSON = "person"
CLASS_TRUCK = "truck"
CLASS_BICYCLE = "bicycle"
CLASS_TRAIN = "train"

FILTER_CLASSES: list[str] = [
    CLASS_CAR,
    CLASS_MOTORCYCLE,
    CLASS_PERSON,
    CLASS_TRUCK,
    CLASS_BICYCLE,
    CLASS_TRAIN,
]


class TestPlotterProfiling:
    def test_plotter_real_data(self) -> None:
        datastore = self.load_data()
        state = self.create_state()
        cache_data_provider = self.create_track_provider(datastore, state, cached=True)
        base_data_provider = self.create_track_provider(datastore, state, cached=False)

        cache_plotter_track = self.create_track_plotter(state, cache_data_provider)
        self.run_track_plotter_cache(cache_plotter_track)

        base_plotter_track = self.create_track_plotter(state, base_data_provider)
        self.run_track_plotter_base(base_plotter_track)

        cache_plotter_point = self.create_point_plotter(state, cache_data_provider)
        self.run_point_plotter_cache(cache_plotter_point)

        base_plotter_point = self.create_point_plotter(state, base_data_provider)
        self.run_point_plotter_base(base_plotter_point)

    @profile(repeat=100)
    def create_layer_plotter(self, layers: list[Plotter]) -> Plotter:
        return LayeredPlotter(layers)

    @profile(repeat=10)
    def run_layer_plotter(self, plotter_layer: Plotter) -> None:
        print("run layer plotter")
        self.run_plotter(plotter_layer)

    @profile(repeat=100)
    def create_section_plotter(
        self, state: TrackViewState, datastore: Datastore
    ) -> Plotter:
        section_plotter = MatplotlibTrackPlotter(SectionGeometryPlotter(datastore))
        return PlotterPrototype(state, section_plotter)

    @profile(repeat=10)
    def run_section_plotter(self, plotter_section: Plotter) -> None:
        print("run section plotter")
        self.run_plotter(plotter_section)

    @profile(repeat=100)
    def create_point_plotter(
        self, state: TrackViewState, data_provider: PandasTrackProvider
    ) -> Plotter:
        point_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(data_provider),
        )
        return PlotterPrototype(state, point_plotter)

    @profile(repeat=10)
    def run_point_plotter_cache(self, plotter_point: Plotter) -> None:
        print("run point plotter cache")
        self.run_plotter(plotter_point)

    @profile(repeat=10)
    def run_point_plotter_base(self, plotter_point: Plotter) -> None:
        print("run point plotter base")
        self.run_plotter(plotter_point)

    @profile(repeat=100)
    def create_track_plotter(
        self, state: TrackViewState, data_provider: PandasTrackProvider
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackGeometryPlotter(data_provider),
        )
        return PlotterPrototype(state, track_plotter)

    @profile(repeat=10)
    def run_track_plotter_cache(self, plotter_track: Plotter) -> None:
        print("run track plotter cache")
        self.run_plotter(plotter_track)

    @profile(repeat=10)
    def run_track_plotter_base(self, plotter_track: Plotter) -> None:
        print("run track plotter base")
        self.run_plotter(plotter_track)

    @profile(repeat=100)
    def create_bg_plotter(self, datastore: Datastore) -> Plotter:
        print("create bg plotter")
        return TrackBackgroundPlotter(datastore)

    @profile(repeat=10)
    def run_bg_plotter(self, plotter_bg: Plotter) -> None:
        print("run bg plotter")
        self.run_plotter(plotter_bg)

    def run_plotter(self, plotter: Plotter) -> None:
        plt = plotter.plot()

        if plt:
            now = datetime.datetime.now()
            p = Path(
                "profiles/plots/"
                + f"{plotter.__class__.__name__}"
                + f"_plot_{now.hour}-{now.minute}-{now.second}.png"
            )
            p.parent.mkdir(exist_ok=True)
            plt.as_image().save(p)

    def create_state(self) -> TrackViewState:
        from_date = datetime.datetime(year=2022, month=9, day=15, hour=7, minute=30)
        to_date = datetime.datetime(year=2022, month=9, day=15, hour=7, minute=59)

        state = TrackViewState()
        state.show_tracks.set(True)
        state.filter_element.set(
            FilterElement(DateRange(from_date, to_date), FILTER_CLASSES)
        )

        return state

    def create_track_provider(
        self, datastore: Datastore, state: TrackViewState, cached: bool = False
    ) -> PandasTrackProvider:
        if cached:
            return CachedPandasTrackProvider(datastore, state, DataFrameFilterBuilder())
        else:
            return PandasTrackProvider(datastore, state, DataFrameFilterBuilder())

    @profile(repeat=1)
    def load_data(self) -> Datastore:
        datastore = self.create_data_store()

        print("loading data")
        datastore.load_track_file(
            Path(r"D:\ptm\data\Standard_SCUEHQ_FR30_2022-09-15_07-00-00.ottrk")
        )
        print("finished loading tracks")

        datastore.load_flow_file(Path(r"D:\ptm\data\sections.otflow"))
        print("finished loading sections/flows")

        return datastore

    def create_data_store(self) -> Datastore:
        track_repo = TrackRepository()
        track_parser = OttrkParser(
            CalculateTrackClassificationByMaxConfidence(), track_repo
        )
        section_repo = SectionRepository()
        flow_repo = FlowRepository()
        flow_parser = OtFlowParser()
        event_repo = EventRepository()
        events_parser = OtEventListParser()
        video_parser = SimpleVideoParser(MoviepyVideoReader())
        video_repo = VideoRepository()
        track_to_video_repo = TrackToVideoRepository()
        track_video_parser = OttrkVideoParser(video_parser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
        )
        datastore = Datastore(
            track_repo,
            track_parser,
            section_repo,
            flow_parser,
            flow_repo,
            event_repo,
            events_parser,
            track_to_video_repo,
            video_repo,
            video_parser,
            track_video_parser,
            config_parser,
        )

        return datastore


if __name__ == "__main__":
    TestPlotterProfiling().test_plotter_real_data()
