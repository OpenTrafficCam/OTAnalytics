from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.plotting import (
    FrameProvider,
    LayeredPlotter,
    PlottingLayer,
    TrackBackgroundPlotter,
    VideoProvider,
)
from OTAnalytics.application.state import Plotter
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.video import Video


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


class TestBackgroundPlotter:
    def test_plot(self) -> None:
        expected_image = Mock()
        single_video = Mock(spec=Video)
        single_video.get_frame.return_value = expected_image
        videos: list[Video] = [single_video]
        video_provider = Mock(spec=VideoProvider)
        video_provider.return_value = videos
        frame_provider = Mock(spec=FrameProvider)

        background_plotter = TrackBackgroundPlotter(
            video_provider=video_provider, frame_provider=frame_provider
        )
        result = background_plotter.plot()

        video_provider.assert_called_once()
        frame_provider.assert_called_once()
        single_video.get_frame.assert_called_once()
        assert result is not None
        assert result == expected_image

    def test_plot_empty_track_repository_returns_none(self) -> None:
        videos: list[Video] = []
        video_provider = Mock(spec=VideoProvider)
        video_provider.return_value = videos
        frame_provider = Mock(spec=FrameProvider)
        background_plotter = TrackBackgroundPlotter(
            video_provider=video_provider, frame_provider=frame_provider
        )
        result = background_plotter.plot()

        video_provider.assert_called_once()
        frame_provider.assert_not_called()
        assert result is None
