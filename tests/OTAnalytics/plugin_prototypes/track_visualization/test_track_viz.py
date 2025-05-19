from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame

from OTAnalytics.adapter_visualization.color_provider import ColorPaletteProvider
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain import track
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.filter import Filter, FilterBuilder, FilterElement
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import (
    OCCURRENCE,
    TRACK_CLASSIFICATION,
    Detection,
    Track,
    TrackId,
    TrackIdProvider,
    TrackImage,
)
from OTAnalytics.domain.track_repository import TrackRepository, TrackRepositoryEvent
from OTAnalytics.plugin_datastore.python_track_store import (
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    EventToFlowResolver,
    FilterByClassification,
    FilterById,
    FilterByOccurrence,
    MatplotlibPlotterImplementation,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTrackProvider,
    PlotterPrototype,
    TrackGeometryPlotter,
    TrackPlotter,
    TrackStartEndPointPlotter,
)
from tests.utils.state import observable


class TestEventToFlowResolver:
    def test_resolve(self) -> None:
        flow_repository = Mock(spec=FlowRepository)
        flow_1 = Mock(spec=Flow)
        flow_1.id = FlowId("flow-1")
        flow_1.start = SectionId("section-1")
        event_1 = Mock(spec=Event)
        event_1.section_id = SectionId("section-1")
        events = [event_1]
        event_to_flow = EventToFlowResolver(flow_repository)
        flow_repository.flows_using_section.return_value = [flow_1]

        flows = event_to_flow.resolve(events)

        assert flow_1.id in flows


class TestPlotterPrototype:
    def test_plot(self) -> None:
        track_id = TrackId("1")
        track = Mock(spec=Track)
        plotted_tracks = Mock(spec=TrackImage)
        track_view_state = TrackViewState()
        track_view_state.track_offset.set(RelativeOffsetCoordinate(0.5, 0.7))
        track_plotter = Mock(spec=TrackPlotter)
        track.id = track_id
        track_plotter.plot.return_value = plotted_tracks
        plotter = PlotterPrototype(track_view_state, track_plotter)

        image = plotter.plot()

        assert image == plotted_tracks


class TestPandasDataProvider:
    def test_plot(self) -> None:
        width = 100
        height = 100
        plotter_implementation = Mock(spec=MatplotlibPlotterImplementation)
        plotter = MatplotlibTrackPlotter(plotter_implementation)

        image = plotter.plot(width=width, height=height)

        assert image is not None
        plotter_implementation.plot.assert_called_once()


class TestPandasTrackProvider:
    def test_get_data_empty_track_repository(self) -> None:
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_all.return_value = PythonTrackDataset.from_list(
            [],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        filter_builder = Mock(FilterBuilder)

        provider = PandasTrackProvider(
            track_repository, filter_builder, NoProgressbarBuilder()
        )
        result = provider.get_data()

        track_repository.get_all.assert_called_once()
        assert result.empty


class TestCachedPandasTrackProvider:
    @pytest.fixture
    def track_1(self) -> Track:
        """Create dummy track with id 1 and 5 detections."""
        return self.set_up_track("1")

    @pytest.fixture
    def track_2(self) -> Track:
        """Create dummy track with id 2 and 5 detections."""
        return self.set_up_track("2")

    def set_up_track(self, id: str) -> Track:
        """Create a dummy track with the given id and 5 car detections."""
        first_detection_occurrence = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
        second_occurrence = first_detection_occurrence + timedelta(seconds=1)
        third_occurrence = second_occurrence + timedelta(seconds=1)
        fourth_occurrence = third_occurrence + timedelta(seconds=1)
        fives_occurrence = fourth_occurrence + timedelta(seconds=1)
        t_id = TrackId(id)
        detections: list[Detection] = [
            PythonDetection(
                "car",
                0.99,
                0,
                1,
                2,
                7,
                1,
                first_detection_occurrence,
                False,
                t_id,
                "video_name",
                "video_name.ottrk",
            ),
            PythonDetection(
                "car",
                0.99,
                0,
                2,
                2,
                7,
                2,
                second_occurrence,
                False,
                t_id,
                "video_name",
                "video_name.ottrk",
            ),
            PythonDetection(
                "car",
                0.99,
                0,
                3,
                2,
                7,
                3,
                third_occurrence,
                False,
                t_id,
                "video_name",
                "video_name.ottrk",
            ),
            PythonDetection(
                "car",
                0.99,
                0,
                4,
                2,
                7,
                4,
                fourth_occurrence,
                False,
                t_id,
                "video_name",
                "video_name.ottrk",
            ),
            PythonDetection(
                "car",
                0.99,
                0,
                5,
                2,
                7,
                5,
                fives_occurrence,
                False,
                t_id,
                "video_name",
                "video_name.ottrk",
            ),
        ]
        return PythonTrack(t_id, t_id, "car", detections)

    def set_up_provider(
        self, init_tracks: list[Track], query_tracks: list[Track]
    ) -> CachedPandasTrackProvider:
        """Create cached track provider with mocked datastore.

        Mocked datastore uses given query_tracks for track repository id queries.
        Initializes provider cache with given init_tracks.
        """
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.side_effect = query_tracks

        filter_builder = Mock(spec=FilterBuilder)
        provider = CachedPandasTrackProvider(
            track_repository, filter_builder, NoProgressbarBuilder()
        )

        assert provider._cache_df.empty
        result = provider._convert_tracks(init_tracks)
        assert result is provider._cache_df
        self.check_expected_ids(provider, init_tracks)

        return provider

    def check_expected_ids(
        self, provider: CachedPandasTrackProvider, expected_tracks: list[Track]
    ) -> None:
        """Check whether provider cache contains the expected tracks/detections."""
        if not expected_tracks:
            assert provider._cache_df.empty

        else:
            cached_ids = provider._cache_df.index.get_level_values(0).unique()

            expected_detections = sum(len(t.detections) for t in expected_tracks)
            assert expected_detections == len(provider._cache_df)
            assert len(expected_tracks) == len(cached_ids)

            for _track in expected_tracks:
                assert _track.id.id in cached_ids

    def test_notify_tracks_clear_cache(self, track_1: Track) -> None:
        """Test clearing cache."""
        provider = self.set_up_provider([track_1], [])

        provider.notify_tracks(TrackRepositoryEvent.create_removed([track_1.id]))
        self.check_expected_ids(provider, [])

    def test_notify_update_add(self, track_1: Track, track_2: Track) -> None:
        """Test adding track to non-empty cache."""
        provider = self.set_up_provider([track_1], [track_2])

        provider.notify_tracks(TrackRepositoryEvent.create_added([track_2.id]))
        self.check_expected_ids(provider, [track_1, track_2])

    def test_notify_update_add_first(self, track_2: Track) -> None:
        """Test adding first track to cache."""
        provider = self.set_up_provider([], [track_2])

        provider.notify_tracks(TrackRepositoryEvent.create_added([track_2.id]))
        self.check_expected_ids(provider, [track_2])

    def test_notify_update_add_multiple_first(
        self, track_2: Track, track_1: Track
    ) -> None:
        """Test adding first tracks to cache."""
        provider = self.set_up_provider([], [track_2, track_1])

        provider.notify_tracks(
            TrackRepositoryEvent.create_added([track_2.id, track_1.id])
        )
        self.check_expected_ids(provider, [track_2, track_1])

    def test_notify_update_existing(self, track_1: Track, track_2: Track) -> None:
        provider = self.set_up_provider([track_1, track_2], [track_1])

        provider.notify_tracks(TrackRepositoryEvent.create_added([track_1.id]))
        self.check_expected_ids(provider, [track_1, track_2])

    def test_notify_update_mixed(self, track_1: Track, track_2: Track) -> None:
        provider = self.set_up_provider([track_2], [track_1, track_2])

        provider.notify_tracks(
            TrackRepositoryEvent.create_added([track_1.id, track_2.id])
        )
        self.check_expected_ids(provider, [track_1, track_2])


class TestColorPaletteProvider:
    DEFAULT_RANDOM_COLOR = "#000"

    @pytest.mark.parametrize(
        "new_classifications,default_palette,expected",
        [
            (
                {"Class 1", "Class 2", "Class 3"},
                {},
                {
                    "Class 1": DEFAULT_RANDOM_COLOR,
                    "Class 2": DEFAULT_RANDOM_COLOR,
                    "Class 3": DEFAULT_RANDOM_COLOR,
                },
            ),
            (
                {"Class 1", "Class 2", "Class 3"},
                {"Class 1": "red", "Not used class": "blue"},
                {
                    "Class 1": "red",
                    "Class 2": DEFAULT_RANDOM_COLOR,
                    "Class 3": DEFAULT_RANDOM_COLOR,
                },
            ),
            ({}, {"Default 1": "red", "Default 2": "blue"}, {}),
        ],
    )
    def test_update_with_filled_default(
        self,
        new_classifications: frozenset[str],
        default_palette: dict[str, str],
        expected: dict[str, str],
    ) -> None:
        with patch.object(
            ColorPaletteProvider,
            "_generate_random_color",
            return_value=self.DEFAULT_RANDOM_COLOR,
        ):
            assert self._is_hex_color("#000")
            color_palette_provider = ColorPaletteProvider(default_palette)
            color_palette_provider.update(new_classifications)
            actual = color_palette_provider.get()
            assert actual == expected

    def test_generate_random_color(self) -> None:
        random_color = ColorPaletteProvider._generate_random_color()
        assert self._is_hex_color(random_color)

    @staticmethod
    def _is_hex_color(value: str) -> bool:
        import re

        hex_color_pattern = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
        return bool(hex_color_pattern.match(value))


class TestTrackGeometryPlotter:
    @pytest.mark.parametrize(
        "data_frame,call_count",
        [
            (DataFrame(), 0),
            (
                DataFrame.from_dict(
                    {"row_1": [0, 2, 3], "row_2": [4, 5, 6]}, orient="index"
                ),
                1,
            ),
        ],
    )
    @patch(
        (
            "OTAnalytics.plugin_prototypes.track_visualization.track_viz."
            "TrackGeometryPlotter._plot_dataframe"
        )
    )
    def test_plot(
        self,
        mock_plot_dataframe: Mock,
        data_frame: DataFrame,
        call_count: int,
    ) -> None:
        data_provider = Mock(spec=PandasTrackProvider)
        color_palette_provider = Mock(spec=ColorPaletteProvider)
        axes = Mock()

        data_provider.get_data.return_value = data_frame
        color_palette_provider.get.return_value = {"Class 1": "green", "Class 2": "red"}

        plotter = TrackGeometryPlotter(
            data_provider, color_palette_provider, enable_legend=False
        )

        plotter.plot(axes)
        assert mock_plot_dataframe.call_count == call_count


class TestStartEndPointPlotter:
    @pytest.mark.parametrize(
        "data_frame,call_count",
        [
            (DataFrame(), 0),
            (
                DataFrame.from_dict(
                    {"row_1": [0, 2, 3], "row_2": [4, 5, 6]}, orient="index"
                ),
                1,
            ),
        ],
    )
    @patch(
        (
            "OTAnalytics.plugin_prototypes.track_visualization.track_viz."
            "TrackStartEndPointPlotter._plot_dataframe"
        )
    )
    def test_plot(
        self,
        mock_plot_dataframe: Mock,
        data_frame: DataFrame,
        call_count: int,
    ) -> None:
        data_provider = Mock(spec=PandasTrackProvider)
        data_provider.get_data.return_value = data_frame
        axes = Mock()

        color_palette_provider = Mock(spec=ColorPaletteProvider)
        color_palette_provider.get.return_value = {"Class 1": "green", "Class 2": "red"}

        plotter = TrackStartEndPointPlotter(
            data_provider, color_palette_provider, enable_legend=False
        )

        plotter.plot(axes)
        assert mock_plot_dataframe.call_count == call_count


class TestDataFrameProviderFilter:
    @pytest.fixture
    def filter_input(self) -> DataFrame:
        first_occurrence = datetime(2000, 1, 1, 1)
        second_occurrence = datetime(2000, 1, 1, 2)
        d = {
            track.TRACK_ID: ["1", "2"],
            track.OCCURRENCE: [first_occurrence, second_occurrence],
            "data": [Mock(), Mock()],
        }
        df = DataFrame(data=d)
        return df.set_index([track.TRACK_ID, track.OCCURRENCE])

    @pytest.fixture
    def filter_result(self) -> Mock:
        return Mock(spec=DataFrame)

    @pytest.fixture
    def data_provider(self, filter_input: DataFrame) -> Mock:
        provider = Mock(spec=PandasDataFrameProvider)
        provider.get_data.return_value = filter_input
        return provider

    @pytest.fixture
    def filter_imp(self, filter_result: Mock) -> Mock:
        _filter = Mock(spec=Filter)
        _filter.apply.return_value = [filter_result]
        return _filter

    @pytest.fixture
    def filter_element(self, filter_imp: Mock) -> Mock:
        filter_element = Mock(spec=FilterElement)
        filter_element.build_filter.return_value = filter_imp
        return filter_element

    @pytest.fixture
    def observable_filter_element(self, filter_element: Mock) -> Mock:
        return observable(filter_element)

    @pytest.fixture
    def track_view_state(self, observable_filter_element: Mock) -> Mock:
        track_view_state = Mock(spec=TrackViewState)
        track_view_state.filter_element = observable_filter_element
        return track_view_state

    def test_filter_by_id(self, data_provider: Mock, filter_input: DataFrame) -> None:
        id_filter = Mock(spec=TrackIdProvider)
        track_id = Mock(spec=TrackId)
        track_id.id = "1"

        id_filter.get_ids.return_value = [track_id]

        filter_by_id = FilterById(data_provider, id_filter)
        result = filter_by_id.get_data()
        expected = filter_input.drop("2", level=track.TRACK_ID)

        assert result.equals(expected)
        data_provider.get_data.assert_called_once()
        id_filter.get_ids.assert_called_once()

    def test_filter_by_id_with_no_index_set(self, data_provider: Mock) -> None:
        data_provider.get_data.return_value = DataFrame.from_dict(
            {1: {"classification": "car", "track_id": "1"}}, orient="index"
        )
        id_filter = Mock()
        filter_by_id = FilterById(data_provider, id_filter)
        with pytest.raises(ValueError):
            filter_by_id.get_data()

    def test_filter_by_classification(
        self,
        filter_input: DataFrame,
        data_provider: Mock,
        track_view_state: Mock,
        observable_filter_element: Mock,
        filter_element: Mock,
        filter_imp: Mock,
        filter_result: Mock,
    ) -> None:
        filter_builder = Mock(Spec=FilterBuilder)
        df_filter = FilterByClassification(
            data_provider, track_view_state, filter_builder
        )
        result = df_filter.get_data()
        assert result == filter_result

        filter_builder.set_classification_column.assert_called_once_with(
            TRACK_CLASSIFICATION
        )
        observable_filter_element.get.assert_called_once()
        filter_element.build_filter.assert_called_once_with(filter_builder)
        filter_imp.apply.assert_called_once_with([filter_input])

    def test_filter_by_occurrence(
        self,
        filter_input: DataFrame,
        data_provider: Mock,
        track_view_state: Mock,
        observable_filter_element: Mock,
        filter_element: Mock,
        filter_imp: Mock,
        filter_result: Mock,
    ) -> None:
        filter_builder = Mock(Spec=FilterBuilder)
        df_filter = FilterByOccurrence(data_provider, track_view_state, filter_builder)
        result = df_filter.get_data()
        assert result == filter_result

        filter_builder.set_occurrence_column.assert_called_once_with(OCCURRENCE)
        observable_filter_element.get.assert_called_once()
        filter_element.build_filter.assert_called_once_with(filter_builder)
        filter_imp.apply.assert_called_once_with([filter_input])
