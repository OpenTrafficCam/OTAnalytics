from datetime import datetime, timedelta
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.plotting import (
    GetCurrentFrame,
    GetCurrentVideoPath,
    LayeredPlotter,
    PlottingLayer,
    TrackBackgroundPlotter,
    VideoProvider,
    VisualizationTimeProvider,
)
from OTAnalytics.application.state import Plotter, VideosMetadata
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.video import Video, VideoMetadata


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
        frame_number = 0
        single_video.get_frame_number_for.return_value = frame_number
        single_video.get_frame.return_value = expected_image
        videos: list[Video] = [single_video]
        video_provider = Mock(spec=VideoProvider)
        video_provider.return_value = videos
        some_time = datetime(2023, 1, 1, 0, 0)
        visualization_time_provider = Mock(spec=VisualizationTimeProvider)
        visualization_time_provider.get_time.return_value = some_time

        background_plotter = TrackBackgroundPlotter(
            video_provider=video_provider,
            visualization_time_provider=visualization_time_provider,
        )
        result = background_plotter.plot()

        video_provider.assert_called_once()
        visualization_time_provider.get_time.assert_called_once()
        single_video.get_frame_number_for.assert_called_with(some_time)
        single_video.get_frame.assert_called_once_with(frame_number)
        assert result is not None
        assert result == expected_image

    def test_plot_empty_track_repository_returns_none(self) -> None:
        videos: list[Video] = []
        video_provider = Mock(spec=VideoProvider)
        video_provider.return_value = videos
        visualization_time_provider = Mock(spec=VisualizationTimeProvider)
        background_plotter = TrackBackgroundPlotter(
            video_provider=video_provider,
            visualization_time_provider=visualization_time_provider,
        )
        result = background_plotter.plot()

        video_provider.assert_called_once()
        visualization_time_provider.get_time.assert_not_called()
        assert result is None


class TestGetCurrentVideoPath:
    def test_get_video(self) -> None:
        filter_end_date = datetime(2023, 1, 1, 0, 1)
        time_provider = Mock(spec=VisualizationTimeProvider)
        time_provider.get_time.return_value = filter_end_date

        video_path = "some/path"
        metadata = Mock(spec=VideoMetadata)
        metadata.path = video_path
        videos_metadata = Mock(spec=VideosMetadata)
        videos_metadata.get_metadata_for.return_value = metadata
        use_case = GetCurrentVideoPath(time_provider, videos_metadata)

        actual = use_case.get_video()

        assert actual == video_path
        time_provider.get_time.assert_called_once()


class TestGetCurrentFrame:
    @pytest.mark.parametrize(
        "filter_end_date, expected_frame_number",
        [
            (datetime(2023, 1, 1, 0, 1), 0),
            (datetime(2023, 1, 1, 0, 1, 1), 20),
            (datetime(2023, 1, 1, 0, 1, 3), 60),
            (datetime(2023, 1, 1, 0, 1, 4), 60),
        ],
    )
    def test_get_frame_number(
        self,
        filter_end_date: datetime,
        expected_frame_number: int,
    ) -> None:
        video_start_date = datetime(2023, 1, 1, 0, 1)
        time_provider = Mock(spec=VisualizationTimeProvider)
        time_provider.get_time.return_value = filter_end_date
        metadata = Mock(spec=VideoMetadata)
        metadata.start = video_start_date
        metadata.duration = timedelta(seconds=3)
        metadata.fps = 20
        metadata.number_of_frames = 60
        videos_metadata = Mock(spec=VideosMetadata)
        videos_metadata.get_metadata_for.return_value = metadata
        use_case = GetCurrentFrame(time_provider, videos_metadata)

        frame_number = use_case.get_frame_number()

        assert frame_number == expected_frame_number

        videos_metadata.get_metadata_for.assert_called_with(filter_end_date)
        time_provider.get_time.assert_called_once()
