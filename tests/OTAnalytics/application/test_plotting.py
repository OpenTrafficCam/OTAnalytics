from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.plotting import LayeredPlotter, PlottingLayer
from OTAnalytics.application.state import Plotter
from OTAnalytics.domain.track import TrackImage


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


class TestPlottingLayer:
    @pytest.fixture
    def plotter(self) -> Mock:
        return Mock(spec=Plotter)

    def test_get_name(self, plotter: Mock) -> None:
        name = "My Layer"
        layer = PlottingLayer(name, plotter, enabled=True)
        assert layer.get_name() == name

    def test_set_enabled(self, plotter: Mock) -> None:
        name = "My Layer"
        observer = Mock()
        layer = PlottingLayer(name, plotter, enabled=False)
        layer.register(observer)

        layer.set_enabled(True)
        assert layer.is_enabled() is True
        layer.set_enabled(True)
        assert layer.is_enabled() is True
        layer.set_enabled(False)
        assert layer.is_enabled() is False
        layer.set_enabled(False)
        assert observer.call_args_list == [call(True), call(False)]

    def test_plot(self, plotter: Mock) -> None:
        name = "My Layer"
        layer = PlottingLayer(name, plotter, enabled=False)

        layer.set_enabled(True)
        layer.plot()
        layer.set_enabled(False)
        layer.plot()
        plotter.plot.assert_called_once()
