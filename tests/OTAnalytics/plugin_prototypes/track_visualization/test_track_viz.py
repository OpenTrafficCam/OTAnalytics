from typing import Optional
from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain.filter import FilterBuilder
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.track import Track, TrackId, TrackImage
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    MatplotlibPlotterImplementation,
    MatplotlibTrackPlotter,
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
        assert result is None


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
            (None, 0),
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
        data_frame: Optional[DataFrame],
        call_count: int,
    ) -> None:
        data_provider = Mock(spec=PandasTrackProvider)
        axes = Mock()

        data_provider.get_data.return_value = data_frame

        plotter = TrackGeometryPlotter(data_provider)

        plotter.plot(axes)
        assert mock_plot_dataframe.call_count == call_count


class TestStartEndPointPlotter:
    @pytest.mark.parametrize(
        "data_frame,call_count",
        [
            (None, 0),
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
        data_frame: Optional[DataFrame],
        call_count: int,
    ) -> None:
        data_provider = Mock(spec=PandasTrackProvider)
        axes = Mock()

        data_provider.get_data.return_value = data_frame

        plotter = TrackStartEndPointPlotter(data_provider)

        plotter.plot(axes)
        assert mock_plot_dataframe.call_count == call_count
