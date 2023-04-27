from unittest.mock import Mock

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.plotting import (
    LayeredPlotter,
    PlotterPrototype,
    TrackPlotter,
)
from OTAnalytics.application.state import Plotter, TrackViewState
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track, TrackId, TrackImage


class TestPlotterPrototype:
    def test_plot(self) -> None:
        background_image = Mock(spec=TrackImage)
        track_id = TrackId(1)
        track = Mock(spec=Track)
        all_tracks = [track]
        all_sections = [Mock(spec=Section)]
        plotted_tracks = Mock(spec=TrackImage)
        combined_image = Mock(spec=TrackImage)
        datastore = Mock(spec=Datastore)
        track_view_state = TrackViewState()
        track_view_state.show_tracks.set(True)
        track_plotter = Mock(sepc=TrackPlotter)
        track.id = track_id
        datastore.get_all_tracks.return_value = all_tracks
        datastore.get_all_sections.return_value = all_sections
        background_image.width.return_value = 100
        background_image.height.return_value = 100
        background_image.add.return_value = combined_image
        datastore.get_image_of_track.return_value = background_image
        track_plotter.plot.return_value = plotted_tracks
        plotter = PlotterPrototype(datastore, track_view_state, track_plotter)

        image = plotter.plot()

        assert image == combined_image


class TestLayeredPlotter:
    def test_plot_all_layers_and_combine_images(self) -> None:
        layer_1_image = Mock(spec=TrackImage)
        layer_2_image = Mock(spec=TrackImage)
        layer_3_image = Mock(spec=TrackImage)
        layer_1_and_2 = Mock(spec=TrackImage)
        combined_image = Mock(spec=TrackImage)
        layer_1 = Mock(spec=Plotter)
        layer_2 = Mock(spec=Plotter)
        layer_3 = Mock(spec=Plotter)
        layer_1.plot.return_value = layer_1_image
        layer_2.plot.return_value = layer_2_image
        layer_3.plot.return_value = layer_3_image
        layer_1_image.add.return_value = layer_1_and_2
        layer_1_and_2.add.return_value = combined_image

        plotter = LayeredPlotter(layers=[layer_1, layer_2, layer_3])

        image = plotter.plot()

        assert image == combined_image
        layer_1_image.add.assert_called_with(layer_2_image)
        layer_1_and_2.add.assert_called_with(layer_3_image)
