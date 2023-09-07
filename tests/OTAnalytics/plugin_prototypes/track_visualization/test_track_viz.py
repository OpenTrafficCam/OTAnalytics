from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import ObservableProperty, TrackViewState
from OTAnalytics.domain.filter import Filter, FilterBuilder, FilterElement
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.track import (
    CLASSIFICATION,
    OCCURRENCE,
    TRACK_ID,
    Detection,
    Track,
    TrackId,
    TrackIdProvider,
    TrackImage,
    TrackRepository,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    ColorPaletteProvider,
    FilterByClassification,
    FilterById,
    FilterByOccurrence,
    MatplotlibPlotterImplementation,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTrackProvider,
    PlotterPrototype,
    TrackBackgroundPlotter,
    TrackGeometryPlotter,
    TrackPlotter,
    TrackStartEndPointPlotter,
)


class TestPlotterPrototype:
    def test_plot(self) -> None:
        track_id = TrackId(1)
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
        datastore = Mock(spec=Datastore)
        datastore.get_all_tracks.return_value = []
        track_view_state = Mock(spec=TrackViewState).return_value
        track_view_state.track_offset.get.return_value = RelativeOffsetCoordinate(0, 0)
        filter_builder = Mock(FilterBuilder)

        provider = PandasTrackProvider(
            datastore, track_view_state, filter_builder, NoProgressbarBuilder()
        )
        result = provider.get_data()

        datastore.get_all_tracks.assert_called_once()
        assert result.empty


class TestCachedPandasTrackProvider:
    @pytest.fixture
    def track_1(self) -> Track:
        """Create dummy track with id 1 and 5 detections."""
        return self.set_up_track(1)

    @pytest.fixture
    def track_2(self) -> Track:
        """Create dummy track with id 2 and 5 detections."""
        return self.set_up_track(2)

    def set_up_track(self, id: int) -> Track:
        """Create a dummy track with the given id and 5 car detections."""
        t_id = TrackId(id)
        detections = [
            Detection(
                "car",
                0.99,
                0,
                1,
                2,
                7,
                1,
                datetime.min,
                False,
                t_id,
                "video_name",
            ),
            Detection(
                "car",
                0.99,
                0,
                2,
                2,
                7,
                2,
                datetime.min,
                False,
                t_id,
                "video_name",
            ),
            Detection(
                "car",
                0.99,
                0,
                3,
                2,
                7,
                3,
                datetime.min,
                False,
                t_id,
                "video_name",
            ),
            Detection(
                "car",
                0.99,
                0,
                4,
                2,
                7,
                4,
                datetime.min,
                False,
                t_id,
                "video_name",
            ),
            Detection(
                "car",
                0.99,
                0,
                5,
                2,
                7,
                5,
                datetime.min,
                False,
                t_id,
                "video_name",
            ),
        ]
        return Track(t_id, "car", detections)

    def set_up_provider(
        self, init_tracks: list[Track], query_tracks: list[Track]
    ) -> CachedPandasTrackProvider:
        """Create cached track provider with mocked datastore.

        Mocked datastore uses given query_tracks for track repository id queries.
        Initializes provider cache with given init_tracks.
        """
        datastore = Mock(spec=Datastore)
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.side_effect = query_tracks

        datastore._track_repository = track_repository

        track_view_state = Mock(spec=TrackViewState).return_value
        track_view_state.track_offset.get.return_value = RelativeOffsetCoordinate(0, 0)
        filter_builder = Mock(spec=FilterBuilder)
        provider = CachedPandasTrackProvider(
            datastore, track_view_state, filter_builder, NoProgressbarBuilder()
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
            cached_ids = provider._cache_df[TRACK_ID].unique()

            expected_detections = sum(len(t.detections) for t in expected_tracks)
            assert expected_detections == len(provider._cache_df)
            assert len(expected_tracks) == len(cached_ids)

            for track in expected_tracks:
                assert track.id.id in cached_ids

    def test_notify_tracks_clear_cache(self, track_1: Track) -> None:
        """Test clearing cache."""
        provider = self.set_up_provider([track_1], [])

        provider.notify_tracks([])
        self.check_expected_ids(provider, [])

    def test_notify_update_add(self, track_1: Track, track_2: Track) -> None:
        """Test adding track to non empty cache."""
        provider = self.set_up_provider([track_1], [track_2])

        provider.notify_tracks([track_2.id])
        self.check_expected_ids(provider, [track_1, track_2])

    def test_notify_update_add_first(self, track_2: Track) -> None:
        """Test adding first track to cache."""
        provider = self.set_up_provider([], [track_2])

        provider.notify_tracks([track_2.id])
        self.check_expected_ids(provider, [track_2])

    def test_notify_update_add_multiple_first(
        self, track_2: Track, track_1: Track
    ) -> None:
        """Test adding first tracks to cache."""
        provider = self.set_up_provider([], [track_2, track_1])

        provider.notify_tracks([track_2.id, track_1.id])
        self.check_expected_ids(provider, [track_2, track_1])

    def test_notify_update_existing(self, track_1: Track, track_2: Track) -> None:
        provider = self.set_up_provider([track_1, track_2], [track_1])

        provider.notify_tracks([track_1.id])
        self.check_expected_ids(provider, [track_1, track_2])

    def test_notify_update_mixed(self, track_1: Track, track_2: Track) -> None:
        provider = self.set_up_provider([track_2], [track_1, track_2])

        provider.notify_tracks([track_1.id, track_2.id])
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
        new_classifications: set[str],
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


class TestBackgroundPlotter:
    def test_plot(self) -> None:
        track = Mock(spec=Track).return_value
        track.id = TrackId(5)

        tracks = [track]
        expected_image = Mock()
        datastore = Mock(spec=Datastore)
        datastore.get_all_tracks.return_value = tracks
        datastore.get_image_of_track.return_value = expected_image

        background_plotter = TrackBackgroundPlotter(datastore)
        result = background_plotter.plot()

        datastore.get_all_tracks.assert_called_once()
        datastore.get_image_of_track.assert_called_once_with(track.id)
        assert result is not None
        assert result == expected_image

    def test_plot_empty_track_repository_returns_none(self) -> None:
        mock_datastore = Mock(spec=Datastore)
        mock_datastore.get_all_tracks.return_value = []
        background_plotter = TrackBackgroundPlotter(mock_datastore)
        result = background_plotter.plot()

        mock_datastore.get_all_tracks.assert_called_once()
        assert result is None


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
        d = {TRACK_ID: [1, 2]}
        return DataFrame(data=d)

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
        observable_property = Mock(spec=ObservableProperty)
        observable_property.get.return_value = filter_element
        return observable_property

    @pytest.fixture
    def track_view_state(self, observable_filter_element: Mock) -> Mock:
        track_view_state = Mock(spec=TrackViewState)
        track_view_state.filter_element = observable_filter_element
        return track_view_state

    def test_filter_by_id(self, data_provider: Mock) -> None:
        id_filter = Mock(spec=TrackIdProvider)
        track_id = Mock(spec=TrackId)
        track_id.id = 1

        id_filter.get_ids.return_value = [track_id]

        filter_by_id = FilterById(data_provider, id_filter)
        result = filter_by_id.get_data()

        assert result.equals(DataFrame(data={TRACK_ID: [1]}))
        data_provider.get_data.assert_called_once()
        id_filter.get_ids.assert_called_once()

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
        result == filter_result

        filter_builder.set_classification_column.assert_called_once_with(CLASSIFICATION)
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
        result == filter_result

        filter_builder.set_occurrence_column.assert_called_once_with(OCCURRENCE)
        observable_filter_element.get.assert_called_once()
        filter_element.build_filter.assert_called_once_with(filter_builder)
        filter_imp.apply.assert_called_once_with([filter_input])
