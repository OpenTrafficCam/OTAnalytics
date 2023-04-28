from unittest.mock import Mock

from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain.track import Track, TrackId, TrackImage
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    MatplotlibTrackPlotter,
    PlotterImplementation,
    PlotterPrototype,
    TrackPlotter,
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
        plotter_implementation = Mock(spec=PlotterImplementation)
        plotter = MatplotlibTrackPlotter(plotter_implementation)

        image = plotter.plot(width=width, height=height)

        assert image is not None
        plotter_implementation.plot.assert_called_once()
