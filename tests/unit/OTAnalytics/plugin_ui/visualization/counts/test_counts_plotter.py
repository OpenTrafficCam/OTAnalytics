from datetime import datetime, timedelta
from typing import Any, Iterator
from unittest.mock import Mock, patch

import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import DataFrame, concat

from OTAnalytics.adapter_visualization.color_provider import ColorPaletteProvider
from OTAnalytics.application.analysis.traffic_counting import (
    LEVEL_CLASSIFICATION,
    LEVEL_FLOW,
    LEVEL_START_TIME,
    Count,
    CountImage,
    TrafficCounting,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.state import TracksMetadata
from OTAnalytics.plugin_ui.visualization.counts.counts_plotter import (
    DPI,
    ClassByFlowCountPlotter,
    CountPlotter,
    FigureData,
    FigureTrace,
    FlowAndClassOverTimeCountPlotter,
    FlowByClassCountPlotter,
    MatplotlibCountBarPlotStyler,
    MatplotlibCountLinePlotStyler,
    MatplotlibCountPlotStyler,
    MatplotlibCountPlotter,
    MultipleCountPlotters,
)

IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600


@pytest.fixture
def traffic_counting() -> Mock:
    """Create a mock TrafficCounting instance."""
    return Mock(spec=TrafficCounting)


@pytest.fixture
def count() -> Mock:
    """Create a mock Count instance."""
    count_mock = Mock(spec=Count)
    count_dict = {
        "flow1": {
            "2023-01-01 12:00:00": {"car": 5, "bicycle": 3},
            "2023-01-01 12:05:00": {
                "car": 7,
            },
        },
        "flow2": {
            "2023-01-01 12:00:00": {"bicycle": 1},
            "2023-01-01 12:05:00": {"car": 3, "bicycle": 4},
        },
    }
    count_mock.to_dict.return_value = count_dict
    return count_mock


@pytest.fixture
def sample_dataframe() -> DataFrame:
    """Create a sample DataFrame for testing."""
    data = {
        LEVEL_FLOW: ["flow1", "flow1", "flow1", "flow2", "flow2", "flow2"],
        LEVEL_START_TIME: [
            datetime(2023, 1, 1, 12, 0, 0),
            datetime(2023, 1, 1, 12, 0, 0),
            datetime(2023, 1, 1, 12, 5, 0),
            datetime(2023, 1, 1, 12, 0, 0),
            datetime(2023, 1, 1, 12, 5, 0),
            datetime(2023, 1, 1, 12, 5, 0),
        ],
        LEVEL_CLASSIFICATION: ["car", "bicycle", "car", "bicycle", "car", "bicycle"],
        "count": [5, 3, 7, 1, 3, 4],
    }
    return DataFrame(data)


@pytest.fixture
def color_provider() -> Mock:
    """Create a mock ColorPaletteProvider."""
    provider = Mock(spec=ColorPaletteProvider)
    provider.get.return_value = {
        "car": "red",
        "bicycle": "blue",
        "flow1": "green",
        "flow2": "purple",
    }
    return provider


@pytest.fixture
def tracks_metadata() -> Mock:
    """Create a mock TracksMetadata."""
    metadata = Mock(spec=TracksMetadata)
    metadata.detection_classifications = ["car", "bicycle"]
    return metadata


@pytest.fixture
def figure_mock() -> Mock:
    """Create a mock Figure."""
    figure = Mock(spec=Figure)
    figure.savefig = Mock()
    return figure


@pytest.fixture
def axes_mock() -> Mock:
    """Create a mock Axes."""
    axes = Mock(spec=Axes)
    axes.plot = Mock()
    axes.bar = Mock()
    axes.set_title = Mock()
    axes.set_xlabel = Mock()
    axes.set_ylabel = Mock()
    axes.legend = Mock()
    axes.grid = Mock()
    return axes


@pytest.fixture
def counting_specs() -> CountingSpecificationDto:
    return CountingSpecificationDto(
        start=datetime.min,
        end=datetime.max,
        count_all_events=True,
        interval_in_minutes=5,
        modes=["car", "bicycle"],
        output_file="none",
        output_format="png",
        export_mode=OVERWRITE,
    )


INTERVAL_MIN = 5
DELTA = timedelta(minutes=INTERVAL_MIN)
START_DATE = datetime(2023, 1, 1, 12, 0, 0)


def new_trace(x: list[int], y: list[int], name: str, color: str) -> FigureTrace:
    x_dates = [START_DATE + i * DELTA for i in x]
    return FigureTrace(
        data=DataFrame({"x": x_dates, "y": y}),
        label=name,
        color=color,
    )


class TestCountPlotter:
    """Tests for the CountPlotter base class."""

    def test_plot_delegate_calls(
        self,
        traffic_counting: Mock,
        count: Mock,
        counting_specs: CountingSpecificationDto,
    ) -> None:
        """Test that plot calls get_counting_specification."""
        traffic_counting.count.return_value = count

        plotter = Mock(spec=CountPlotter)
        plotter._traffic_counting = traffic_counting
        plotter.plot = lambda w, h: CountPlotter.plot(plotter, w, h)
        plotter.get_counting_specification.return_value = counting_specs
        plotter.plot_count.return_value = []

        plotter.plot(800, 600)

        plotter.get_counting_specification.assert_called_once()
        traffic_counting.count.assert_called_once_with(counting_specs)
        plotter.plot_count.assert_called_once_with(count, 800, 600)


class TestMultipleCountPlotters:
    """Tests for the MultipleCountPlotters class."""

    def test_plot_calls_plot_on_each_plotter(self, traffic_counting: Mock) -> None:
        """Test that plot calls plot on each contained plotter."""
        img1 = Mock(spec=CountImage)
        img2 = Mock(spec=CountImage)
        img3 = Mock(spec=CountImage)

        plotter1 = Mock(spec=CountPlotter)
        plotter1.plot.return_value = [img1]

        plotter2 = Mock(spec=CountPlotter)
        plotter2.plot.return_value = [img2, img3]

        multiple_plotters = MultipleCountPlotters(
            traffic_counting, [plotter1, plotter2]
        )

        result = multiple_plotters.plot(800, 600)

        plotter1.plot.assert_called_once_with(800, 600)
        plotter2.plot.assert_called_once_with(800, 600)
        assert result == [img1, img2, img3]

    @pytest.mark.parametrize(
        "method_name", ["plot_count", "get_counting_specification"]
    )
    def test_unsupported_methods_raise_not_implemented(
        self, traffic_counting: Mock, count: Mock, method_name: str
    ) -> None:
        """Test that unsupported methods raise NotImplementedError."""
        plotter1 = Mock(spec=CountPlotter)
        plotter2 = Mock(spec=CountPlotter)
        multiple_plotters = MultipleCountPlotters(
            traffic_counting, [plotter1, plotter2]
        )

        with pytest.raises(NotImplementedError):
            if method_name == "plot_count":
                multiple_plotters.plot_count(count, 800, 600)
            else:
                multiple_plotters.get_counting_specification()


class TestMatplotlibCountPlotStyler:
    """Tests for the MatplotlibCountPlotStyler class."""

    class DummyStyler(MatplotlibCountPlotStyler):
        def _plot(self, data: FigureData, figure: Figure, axes: Axes) -> None:
            pass

    @patch("OTAnalytics.plugin_ui.visualization.counts.counts_plotter.subplots")
    def test_apply_plotter_calls_setup_and_plot(
        self, mock_subplots: Mock, figure_mock: Mock, axes_mock: Mock
    ) -> None:
        """Test that apply_plotter calls _setup_fig_ax and _plot."""
        figure_name = "Test Plot"
        # Setup
        mock_subplots.return_value = (figure_mock, axes_mock)
        styler = self.DummyStyler("_test")
        data = FigureData(name=figure_name, traces=[], x="x", y="y")

        # Execute
        with patch.object(styler, "_plot") as mock_plot:
            with patch.object(styler, "_convert_to_image") as mock_convert:
                mock_convert.return_value = Mock(spec=CountImage)
                styler.apply_plotter(data, IMAGE_WIDTH, IMAGE_HEIGHT)

        # Verify
        mock_subplots.assert_called_once_with(
            figsize=(IMAGE_WIDTH / DPI, IMAGE_HEIGHT / DPI), dpi=DPI
        )
        mock_plot.assert_called_once_with(data, figure_mock, axes_mock)
        mock_convert.assert_called_once_with(
            figure_mock, IMAGE_WIDTH, IMAGE_HEIGHT, figure_name
        )


class TestMatplotlibCountLinePlotStyler:
    """Tests for the MatplotlibCountLinePlotStyler class."""

    def assert_plot_called_with_trace_args(
        self, args: Any, kwargs: Any, trace: FigureTrace
    ) -> None:
        assert list(args[0]) == list(trace.data.x)
        assert list(args[1]) == list(trace.data.y)
        assert kwargs["label"] == trace.label
        assert kwargs["color"] == trace.color
        assert kwargs["marker"] == "x"

    def test_plot_calls_axes_plot_for_each_trace(
        self, figure_mock: Mock, axes_mock: Mock
    ) -> None:
        """Test that _plot calls axes.plot for each trace."""

        trace1 = new_trace([1, 2, 3], [4, 5, 6], "Trace 1", "red")
        trace2 = new_trace([1, 2, 3], [7, 8, 9], "Trace 2", "blue")
        data = FigureData(name="Test Plot", traces=[trace1, trace2], x="x", y="y")

        styler = MatplotlibCountLinePlotStyler(legend=True)
        styler._plot(data, figure_mock, axes_mock)

        assert axes_mock.plot.call_count == 2
        call_args_list = axes_mock.plot.call_args_list
        assert len(call_args_list) == 2

        args1, kwargs1 = call_args_list[0]
        self.assert_plot_called_with_trace_args(args1, kwargs1, trace1)

        args2, kwargs2 = call_args_list[1]
        self.assert_plot_called_with_trace_args(args2, kwargs2, trace2)


class TestMatplotlibCountBarPlotStyler:
    """Tests for the MatplotlibCountBarPlotStyler class."""

    def assert_bar_call_args(
        self, args: Any, kwargs: Any, trace: FigureTrace, bottom: list[int]
    ) -> None:
        assert list(kwargs["x"]) == list(trace.data.x)
        assert list(kwargs["height"]) == list(trace.data.y)
        assert kwargs["width"] == timedelta(minutes=3)
        assert kwargs["bottom"] == bottom
        assert kwargs["label"] == trace.label
        assert kwargs["color"] == trace.color

    @pytest.mark.parametrize("ascending", [True, False])
    def test_plot_calls_axes_bar_for_each_trace(
        self, figure_mock: Mock, axes_mock: Mock, ascending: bool
    ) -> None:
        """Test that _plot calls axes.bar for each trace."""

        trace1 = new_trace([0, 1], [7, 8], "Trace 1", "red")
        trace2 = new_trace([0, 1], [3, 4], "Trace 2", "blue")
        trace3 = new_trace([0, 1], [5, 6], "Trace 3", "green")
        data = FigureData(
            name="Test Plot", traces=[trace1, trace2, trace3], x="x", y="y"
        )

        styler = MatplotlibCountBarPlotStyler(
            time_interval_min=INTERVAL_MIN, legend=True, ascending_trace_sum=ascending
        )
        styler._plot(data, figure_mock, axes_mock)

        # Verify
        assert axes_mock.bar.call_count == 3
        call_args_list = axes_mock.bar.call_args_list
        assert len(call_args_list) == 3

        args1, kwargs1 = call_args_list[0]
        expected_trace_1 = trace2 if ascending else trace1
        expected_bottom_1 = [0, 0]
        self.assert_bar_call_args(args1, kwargs1, expected_trace_1, expected_bottom_1)

        args2, kwargs2 = call_args_list[1]
        expected_bottom_2 = [3, 4] if ascending else [7, 8]
        self.assert_bar_call_args(args2, kwargs2, trace3, expected_bottom_2)

        args3, kwargs3 = call_args_list[2]
        expected_trace_3 = trace1 if ascending else trace2
        expected_bottom_3 = [8, 10] if ascending else [12, 14]
        self.assert_bar_call_args(args3, kwargs3, expected_trace_3, expected_bottom_3)


class TestMatplotlibCountPlotter:
    """Tests for the MatplotlibCountPlotter class."""

    class DummyMatplotlibCountPlotter(MatplotlibCountPlotter):
        def __init__(
            self,
            traffic_counting: TrafficCounting,
            styler: MatplotlibCountBarPlotStyler,
            data: list[FigureData],
            specs: CountingSpecificationDto,
        ) -> None:
            super().__init__(traffic_counting, styler)
            self._data = data
            self._specs = specs

        def _prepare_dataframe(self, count: Count) -> DataFrame:
            if len(self._data) == 0:
                return DataFrame()
            else:  # non-empty data frame
                return DataFrame({"x": [-1]})

        def _create_figure_data(self, dataframe: DataFrame) -> Iterator[FigureData]:
            return iter(self._data)

        def get_counting_specification(self) -> CountingSpecificationDto:
            return self._specs

    def test_plot_count_returns_empty_list_for_empty_dataframe(
        self,
        traffic_counting: Mock,
        count: Mock,
        counting_specs: CountingSpecificationDto,
    ) -> None:
        """Test that plot_count returns an empty list when the dataframe is empty."""
        styler = Mock()
        plotter = self.DummyMatplotlibCountPlotter(
            traffic_counting, styler, [], counting_specs
        )
        result = plotter.plot_count(count, IMAGE_WIDTH, IMAGE_HEIGHT)
        assert result == []
        assert styler.call_count == 0

    def test_plot_count_calls_styler_for_each_figure_data(
        self,
        traffic_counting: Mock,
        count: Mock,
        counting_specs: CountingSpecificationDto,
    ) -> None:
        """Test that plot_count calls the styler for each figure data."""
        trace1 = new_trace([1, 2, 3], [4, 5, 6], "Trace 1", "red")
        trace2 = new_trace([1, 2, 3], [7, 8, 9], "Trace 2", "blue")
        trace3 = new_trace([1, 2, 3], [10, 11, 12], "Trace 3", "green")
        data1 = FigureData(name="Test Plot", traces=[trace1, trace2], x="x", y="y")
        data2 = FigureData(name="Test Plot", traces=[trace3, trace1], x="x", y="y")

        styler = Mock()
        styler.apply_plotter.return_value = Mock(spec=CountImage)
        plotter = self.DummyMatplotlibCountPlotter(
            traffic_counting, styler, [data1, data2], counting_specs
        )

        # Execute
        result = plotter.plot_count(count, IMAGE_WIDTH, IMAGE_HEIGHT)

        # Verify
        assert styler.apply_plotter.call_count == 2
        assert len(result) == 2
        call_args_list = styler.apply_plotter.call_args_list
        assert len(call_args_list) == 2

        args1, kwargs1 = call_args_list[0]
        assert args1[0] == data1
        assert args1[1] == IMAGE_WIDTH
        assert args1[2] == IMAGE_HEIGHT

        args2, kwargs2 = call_args_list[1]
        assert args2[0] == data2
        assert args2[1] == IMAGE_WIDTH
        assert args2[2] == IMAGE_HEIGHT


class TestFlowAndClassOverTimeCountPlotter:
    """Tests for the FlowAndClassOverTimeCountPlotter class."""

    class DummyFlowAndClassOverTimeCountPlotter(FlowAndClassOverTimeCountPlotter):
        def _create_figure_data(self, dataframe: DataFrame) -> Iterator[FigureData]:
            return iter([])

    def test_get_counting_specification(
        self, traffic_counting: Mock, color_provider: Mock, tracks_metadata: Mock
    ) -> None:
        """Test that get_counting_specification returns the correct specification."""
        given_interval_in_minutes = 10

        plotter = self.DummyFlowAndClassOverTimeCountPlotter(
            traffic_counting,
            color_provider,
            tracks_metadata,
            interval_in_minutes=given_interval_in_minutes,
        )

        spec = plotter.get_counting_specification()

        assert spec.interval_in_minutes == 10
        assert spec.start == datetime.min
        assert spec.end == datetime.max
        assert spec.count_all_events is True
        assert spec.interval_in_minutes == given_interval_in_minutes
        assert spec.modes == list(tracks_metadata.detection_classifications)
        assert spec.output_file == "none"
        assert spec.export_mode == OVERWRITE

    @patch(
        "OTAnalytics.plugin_ui.visualization.counts.counts_plotter"
        + ".count_dict_to_dataframe"
    )
    def test_prepare_dataframe_handles_empty_dataframe(
        self,
        mock_count_dict_to_dataframe: Mock,
        traffic_counting: Mock,
        color_provider: Mock,
        tracks_metadata: Mock,
        count: Mock,
    ) -> None:
        """Test that _prepare_dataframe handles an empty dataframe correctly."""

        plotter = self.DummyFlowAndClassOverTimeCountPlotter(
            traffic_counting, color_provider, tracks_metadata
        )
        mock_count_dict_to_dataframe.return_value = DataFrame()

        result = plotter._prepare_dataframe(count)

        assert result.empty is True
        mock_count_dict_to_dataframe.assert_called_once_with(count.to_dict())

    @patch(
        "OTAnalytics.plugin_ui.visualization.counts.counts_plotter"
        + ".count_dict_to_dataframe"
    )
    def test_prepare_dataframe_creates_full_index(
        self,
        mock_count_dict_to_dataframe: Mock,
        traffic_counting: Mock,
        color_provider: Mock,
        tracks_metadata: Mock,
        count: Mock,
        sample_dataframe: DataFrame,
    ) -> None:
        """Test that _prepare_dataframe creates a full index with all combinations."""

        plotter = self.DummyFlowAndClassOverTimeCountPlotter(
            traffic_counting, color_provider, tracks_metadata
        )
        mock_count_dict_to_dataframe.return_value = sample_dataframe

        result = plotter._prepare_dataframe(count)

        assert result.empty is not True
        assert len(result) == 8
        assert list(result["count"]) == [5, 3, 7, 0, 0, 1, 3, 4]


class TestFlowByClassCountPlotter:
    """Tests for the FlowByClassCountPlotter class."""

    def test_create_figure_data_yields_one_figure_per_flow(
        self,
        traffic_counting: Mock,
        color_provider: Mock,
        tracks_metadata: Mock,
        sample_dataframe: DataFrame,
    ) -> None:
        """Test that _create_figure_data yields one figure per flow."""
        plotter = FlowByClassCountPlotter(
            traffic_counting, color_provider, tracks_metadata
        )

        # Execute
        result = list(plotter._create_figure_data(sample_dataframe))

        # Verify
        color_provider.get.assert_called_once()

        assert len(result) == 2  # One for each flow
        assert "flow1" in result[0].name
        assert "flow2" in result[1].name

        for figure_data in result:
            assert isinstance(figure_data, FigureData)
            assert len(figure_data.traces) == 2
            actual_labels = {trace.label for trace in figure_data.traces}
            expected_labels = {"car", "bicycle"}
            assert actual_labels == expected_labels

            # Verify the dataframe content in each trace
            flow = "flow1" if "flow1" in figure_data.name else "flow2"
            for trace in figure_data.traces:
                expected_df = sample_dataframe[
                    (sample_dataframe[LEVEL_FLOW] == flow)
                    & (sample_dataframe[LEVEL_CLASSIFICATION] == trace.label)
                ]
                expected_df = expected_df.sort_values(LEVEL_START_TIME)

                assert list(trace.data["count"]) == list(expected_df["count"])
                assert trace.data.equals(expected_df)


class TestClassByFlowCountPlotter:
    """Tests for the ClassByFlowCountPlotter class."""

    def test_create_figure_data_yields_one_figure_per_classification(
        self,
        traffic_counting: Mock,
        color_provider: Mock,
        tracks_metadata: Mock,
        sample_dataframe: DataFrame,
    ) -> None:
        """Test that _create_figure_data yields one figure per classification."""

        plotter = ClassByFlowCountPlotter(
            traffic_counting, color_provider, tracks_metadata
        )

        # Execute
        result = list(plotter._create_figure_data(sample_dataframe))

        # Verify
        color_provider.get.assert_called_once()
        color_provider.update.assert_called_once_with(frozenset([]))
        assert len(result) == 2  # One for each classification
        assert "car" in result[0].name
        assert "bicycle" in result[1].name

        for figure_data in result:
            assert isinstance(figure_data, FigureData)
            assert len(figure_data.traces) == 2
            actual_labels = {trace.label for trace in figure_data.traces}
            expected_labels = {"flow1", "flow2"}
            assert actual_labels == expected_labels

            # Verify the dataframe content in each trace
            classification = "car" if "car" in figure_data.name else "bicycle"
            for trace in figure_data.traces:
                expected_df = sample_dataframe[
                    (sample_dataframe[LEVEL_CLASSIFICATION] == classification)
                    & (sample_dataframe[LEVEL_FLOW] == trace.label)
                ]
                expected_df = expected_df.sort_values(LEVEL_START_TIME)

                assert trace.data.equals(expected_df)

    def test_create_figure_data_updates_color_palette_for_new_flows(
        self,
        traffic_counting: Mock,
        color_provider: Mock,
        tracks_metadata: Mock,
        sample_dataframe: DataFrame,
    ) -> None:
        """Test that _create_figure_data updates the color palette for new flows."""
        unknown_flow = "flow3"

        plotter = ClassByFlowCountPlotter(
            traffic_counting, color_provider, tracks_metadata
        )

        # Add a new flow to the dataframe
        new_flow_data = sample_dataframe.copy()
        new_flow_data[LEVEL_FLOW] = unknown_flow
        combined_df = concat([sample_dataframe, new_flow_data])

        list(plotter._create_figure_data(combined_df))

        color_provider.get.assert_called_once()
        color_provider.update.assert_called_once()
        color_provider.update.assert_called_once_with(frozenset([unknown_flow]))
