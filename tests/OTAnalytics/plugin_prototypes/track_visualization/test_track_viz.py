from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain.filter import FilterBuilder
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.track import (
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
    FilterById,
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
        track_view_state.show_tracks.set(True)
        track_plotter = Mock(sepc=TrackPlotter)
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

        provider = PandasTrackProvider(datastore, track_view_state, filter_builder)
        result = provider.get_data()

        datastore.get_all_tracks.assert_called_once()
        assert result.empty


class TestCachedPandasTrackProvider:
    def create_tracks(self) -> None:
        """Create two dummy tracks with ids 1 and 2, each 5 detections."""
        self.track_1 = self.set_up_track(1)
        self.track_2 = self.set_up_track(2)

    def set_up_track(self, id: int) -> Track:
        t_id = TrackId(id)
        detections = [
            Detection("car", 0.99, 0, 1, 2, 7, 1, datetime.min, Path(""), False, t_id),
            Detection("car", 0.99, 0, 2, 2, 7, 2, datetime.min, Path(""), False, t_id),
            Detection("car", 0.99, 0, 3, 2, 7, 3, datetime.min, Path(""), False, t_id),
            Detection("car", 0.99, 0, 4, 2, 7, 4, datetime.min, Path(""), False, t_id),
            Detection("car", 0.99, 0, 5, 2, 7, 5, datetime.min, Path(""), False, t_id),
        ]
        return Track(t_id, "car", detections)

    def set_up_provider(
        self, init_tracks: list[Track], query_tracks: list[Track]
    ) -> CachedPandasTrackProvider:
        """Create cached track provider with moc´ked datastore.
        Mocked datastore uses given query_tracks for track repository id queries.
        Initializes provider cache with given init_tracks.
        """
        datastore = Mock(spec=Datastore)
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.side_effect = query_tracks

        datastore._track_repository = track_repository

        track_view_state = Mock(spec=TrackViewState).return_value
        track_view_state.track_offset.get.return_value = RelativeOffsetCoordinate(0, 0)
        filter_builder = Mock(FilterBuilder)
        provider = CachedPandasTrackProvider(
            datastore, track_view_state, filter_builder
        )

        assert provider._cache_df.empty
        result = provider._convert_tracks(init_tracks)
        assert result is not None
        assert result is provider._cache_df

        return provider

    def test_notify_tracks_clear_cache(self) -> None:
        """Test clearing cache."""
        self.create_tracks()
        provider = self.set_up_provider([self.track_1], [])

        provider.notify_tracks([])
        assert provider._cache_df.empty


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
        axes = Mock()

        data_provider.get_data.return_value = data_frame

        plotter = TrackGeometryPlotter(data_provider, enable_legend=False)

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
        axes = Mock()

        data_provider.get_data.return_value = data_frame

        plotter = TrackStartEndPointPlotter(data_provider, enable_legend=False)

        plotter.plot(axes)
        assert mock_plot_dataframe.call_count == call_count


class TestFilterById:
    @pytest.fixture
    def data(self) -> DataFrame:
        d = {TRACK_ID: [1, 2]}
        return DataFrame(data=d)

    def test_get_data(self, data: DataFrame) -> None:
        data_provider = Mock(PandasDataFrameProvider)
        data_provider.get_data.return_value = data
        id_filter = Mock(spec=TrackIdProvider)
        track_id = Mock(spec=TrackId)
        track_id.id = 1

        id_filter.get_ids.return_value = [track_id]

        filter_by_id = FilterById(data_provider, id_filter)
        result = filter_by_id.get_data()

        assert result.equals(DataFrame(data={TRACK_ID: [1]}))
        data_provider.get_data.assert_called_once()
        id_filter.get_ids.assert_called_once()
