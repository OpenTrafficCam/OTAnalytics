import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import close, subplots
from pandas import DataFrame, MultiIndex, to_datetime
from PIL import Image as ImageModule
from PIL.Image import Image

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
from OTAnalytics.plugin_parser.export import count_dict_to_dataframe

DPI = 100


class CountPlotter(ABC):
    """
    Abstract base class for plotting count data.

    This class defines the interface for all count plotters in the system.
    It provides the basic structure for retrieving counting specifications,
    performing counts, and plotting the results.

    Attributes:
        _traffic_counting: The traffic counting service.
    """

    def __init__(self, traffic_counting: TrafficCounting) -> None:
        self._traffic_counting = traffic_counting

    def plot(self, width: int, height: int) -> list[CountImage]:
        specification = self.get_counting_specification()
        count = self._traffic_counting.count(specification)
        plots = self.plot_count(count, width, height)

        return plots

    @abstractmethod
    def get_counting_specification(self) -> CountingSpecificationDto:
        """
        Get the specification for counting traffic.

        This method should be implemented by subclasses to define the parameters
        for traffic counting.

        Returns:
            CountingSpecificationDto: the counting parameters.
        """
        pass

    @abstractmethod
    def plot_count(
        self,
        count: Count,
        width: int,
        height: int,
    ) -> list[CountImage]:
        """
        Plot the count data into visual representations.

        This method should be implemented by subclasses to transform count data
        into visual plots according to the specific visualization strategy.

        Args:
            count (Count): The count data to be plotted.
            width (int): The width of the resulting image in pixels.
            height (int): The height of the resulting image in pixels.

        Returns:
            list[CountImage]: A list of count images generated from the count data.
        """
        pass


class MultipleCountPlotters(CountPlotter):
    """
    A composite plotter that contains and manages multiple CountPlotter instances.

    This class implements the Composite pattern, allowing multiple plotters to be
    treated as a single plotter. It delegates plotting operations to its contained
    plotters and aggregates their results.

    Attributes:
        _traffic_counting: The traffic counting service.
        _plotters: A list of CountPlotter instances that this composite manages.
    """

    def __init__(self, traffic_counting: TrafficCounting, plotters: list[CountPlotter]):
        super().__init__(traffic_counting)
        self._plotters = plotters

    def plot_count(self, count: Count, width: int, height: int) -> list[CountImage]:
        raise NotImplementedError(
            "plot_count should not be called on MultipleCountPlotters, "
            + "they should be defined per contained plotter!"
        )

    def get_counting_specification(self) -> CountingSpecificationDto:
        raise NotImplementedError(
            "get_counting_specification should not be called on "
            + "MultipleCountPlotters, they should be defined "
            + "per contained plotter!"
        )

    def plot(self, width: int, height: int) -> list[CountImage]:
        result = []
        for plotter in self._plotters:
            result += plotter.plot(width, height)
        return result


FIGURE_CONSUMER = Callable[[Any, Figure, Axes], None]


@dataclass(frozen=True)
class FigurePlotter:
    """
    A dataclass that encapsulates the details needed to plot a figure.

    It holds the key, name, and plotter function needed to create
    a specific figure.

    Attributes:
        key: An identifier for the figure, e.g., a flow or classification string.
        name: The display name for the figure, used as the plot title.
        plotter: A callable that takes a key, figure, and axes and plots data.
    """

    key: Any
    name: str
    plotter: FIGURE_CONSUMER

    def __call__(self, figure: Figure, axes: Axes) -> None:
        self.plotter(self.key, figure, axes)


class MatplotlibCountPlotStyler:
    """
    A utility class for creating and styling matplotlib Figures/Axes.
    """

    def apply_plotter(self, plotter: FigurePlotter, width: int, height: int) -> Image:
        fig, ax = self.setup_fig_ax(width, height)
        plotter(fig, ax)
        self.style_count_plot_axes(plotter.name, fig, ax)
        return self.convert_to_image(fig)

    def setup_fig_ax(self, width: int, height: int) -> tuple[Figure, Axes]:
        image_width = width / DPI
        image_height = height / DPI

        return subplots(figsize=(image_width, image_height), dpi=DPI)

    def style_count_plot_axes(self, title: str, figure: Figure, axes: Axes) -> None:
        axes.set_title(title)
        axes.set_xlabel("Time")
        axes.set_ylabel("Count")
        axes.legend()
        axes.grid(True)
        figure.autofmt_xdate()  # Rotate x-axis labels if needed

    def convert_to_image(self, figure: Figure) -> Image:
        """
        Convert the figure into an image.

        Args:
            figure (Figure): figure containing the plotted axes object

        Returns:
            Image: image containing the content of the axes object
        """
        # Convert to PIL Image
        buf = io.BytesIO()
        buf.seek(0)
        figure.savefig(buf, format="png", dpi=DPI)
        image = ImageModule.open(buf).convert("RGBA")

        buf.close()
        close(figure)
        return image


class MatplotlibCountPlotter(CountPlotter):
    """
    An abstract implementation of CountPlotter that uses matplotlib for plotting.

    This class provides common functionality for matplotlib-based plotters,
    including dataframe preparation and figure creation. Concrete subclasses
    must implement the _prepare_dataframe and create_figure_plotters methods.

    Attributes:
        _traffic_counting: The traffic counting service.
        _styler: A MatplotlibCountPlotStyler instance used to style the plots.
    """

    def __init__(
        self,
        traffic_counting: TrafficCounting,
        styler: MatplotlibCountPlotStyler = MatplotlibCountPlotStyler(),
    ):
        super().__init__(traffic_counting)
        self._styler = styler

    def plot_count(self, count: Count, width: int, height: int) -> list[CountImage]:
        dataframe = self._prepare_dataframe(count)
        if dataframe.empty:
            return []

        result = []
        timestamp = datetime.now()

        for plotter in self.create_figure_plotters(dataframe):
            pil = self._styler.apply_plotter(plotter, width, height)
            image = CountImage(pil, width, height, plotter.name, timestamp)
            result.append(image)

        return result

    @abstractmethod
    def _prepare_dataframe(self, count: Count) -> DataFrame:
        """
        Prepare a DataFrame from the count data for plotting.

        Args:
            count (Count): The raw count data to be transformed.

        Returns:
            DataFrame: A pandas DataFrame structured for plotting.
        """
        pass

    @abstractmethod
    def create_figure_plotters(self, dataframe: DataFrame) -> list[FigurePlotter]:
        """
        Create a list of figure plotters from the prepared DataFrame.
        These are lazy plotting functions that can be executed
        as soon as figure/axes have been created.

        Args:
            dataframe (DataFrame): The prepared DataFrame containing the count data.

        Returns:
            list[FigurePlotter]: A list of plotters to add data to figures.
        """
        pass


class FlowAndClassOverTimeCountPlotter(MatplotlibCountPlotter):
    """
    A plotter for visualizing flow and classification counts over time.

    This class provides the base functionality for plotting count data
    with respect to flows and classifications over time. It prepares the
    dataframe with the necessary structure and handles time-based sorting.

    Attributes:
        _traffic_counting: The traffic counting service.
        _styler: A MatplotlibCountPlotStyler instance used to style the plots.
        _metadata: Metadata about the tracks being analyzed.
        _color_provider: Provider for color palettes used in the plots.
    """

    def __init__(
        self,
        traffic_counting: TrafficCounting,
        color_provider: ColorPaletteProvider,
        tracks_metadata: TracksMetadata,
        interval_in_minutes: int = 5,
        styler: MatplotlibCountPlotStyler = MatplotlibCountPlotStyler(),
    ):
        super().__init__(traffic_counting, styler)
        self._metadata = tracks_metadata
        self._color_provider = color_provider
        self._interval_in_minutes = interval_in_minutes

    def get_counting_specification(self) -> CountingSpecificationDto:
        return CountingSpecificationDto(
            start=datetime.min,
            end=datetime.max,
            count_all_events=True,
            interval_in_minutes=self._interval_in_minutes,
            modes=list(self._metadata.detection_classifications),
            output_file="none",
            output_format="png",
            export_mode=OVERWRITE,
        )

    def _prepare_dataframe(self, count: Count) -> DataFrame:
        count_dict = count.to_dict()
        dataframe = count_dict_to_dataframe(count_dict)

        if dataframe.empty:
            return dataframe

        dataframe[LEVEL_START_TIME] = to_datetime(
            dataframe[LEVEL_START_TIME], format="%Y-%m-%d %H:%M:%S"
        )
        dataframe = dataframe.sort_values(LEVEL_START_TIME)

        # Build full combination index (flow x start time x classification)
        all_flows = dataframe[LEVEL_FLOW].unique()
        all_times = dataframe[LEVEL_START_TIME].unique()
        all_classes = dataframe[LEVEL_CLASSIFICATION].unique()
        multi_index = [LEVEL_FLOW, LEVEL_START_TIME, LEVEL_CLASSIFICATION]
        full_index = MultiIndex.from_product(
            [all_flows, all_times, all_classes],
            names=multi_index,
        )

        # Set index and reindex full DataFrame
        dataframe = dataframe.set_index(multi_index)
        dataframe = dataframe.reindex(full_index, fill_value=0).reset_index()

        return dataframe


class FlowByClassCountPlotter(FlowAndClassOverTimeCountPlotter):
    """
    A plotter that creates separate plots for each flow, showing different
    classifications of that flow over time. Each classification
    is represented by a different line in the plot.
    The colors of each classification are obtained from the color palette.

    Attributes:
        _traffic_counting: The traffic counting service.
        _styler: A MatplotlibCountPlotStyler instance used to style the plots.
        _metadata: Metadata about the tracks being analyzed.
        _color_provider: Provider for color palettes used in the plots.
    """

    def create_figure_plotters(self, dataframe: DataFrame) -> list[FigurePlotter]:
        flows = list(dataframe[LEVEL_FLOW].unique())

        results = []
        for flow in flows:
            results.append(
                FigurePlotter(
                    key=flow,
                    name=f"counts of flow {flow} by class over time",
                    plotter=lambda f, fig, ax: self.plot_flow_by_mode(
                        dataframe, f, fig, ax
                    ),
                )
            )
        return results

    def plot_flow_by_mode(
        self, dataframe: DataFrame, flow: str, figure: Figure, axes: Axes
    ) -> None:
        flow_df = dataframe[dataframe[LEVEL_FLOW] == flow]
        color_palette = self._color_provider.get()

        for classification in flow_df[LEVEL_CLASSIFICATION].unique():
            class_df = flow_df[flow_df[LEVEL_CLASSIFICATION] == classification]
            class_df = class_df.sort_values(LEVEL_START_TIME)

            axes.plot(
                class_df[LEVEL_START_TIME],
                class_df["count"],
                label=classification,
                color=color_palette.get(classification, "black"),
                marker="x",
            )


class ClassByFlowCountPlotter(FlowAndClassOverTimeCountPlotter):
    """
    A plotter that creates separate plots for each classification, showing different
    flows of that classification over time. Each flow is represented
    by a different line in the plot.

    The colors for each unique flow string are randomly generated upon the first
    encounter and reused afterward.
    This ensures a consistent color scheme for all plots.

    Attributes:
        _traffic_counting: The traffic counting service.
        _styler: A MatplotlibCountPlotStyler instance used to style the plots.
        _metadata: Metadata about the tracks being analyzed.
        _color_provider: Provider for color palettes used in the plots.
    """

    def create_figure_plotters(self, dataframe: DataFrame) -> list[FigurePlotter]:
        classifications = list(dataframe[LEVEL_CLASSIFICATION].unique())
        flows: list[str] = list(dataframe[LEVEL_FLOW].unique())

        color_palette = self._color_provider.get()
        new_flows = frozenset([flow for flow in flows if flow not in color_palette])
        self._color_provider.update(new_flows)

        results = []
        for cls in classifications:
            results.append(
                FigurePlotter(
                    key=cls,
                    name=f"counts of class {cls} by flow over time",
                    plotter=lambda c, fig, ax: self.plot_class_by_flow(
                        dataframe, c, fig, ax
                    ),
                )
            )
        return results

    def plot_class_by_flow(
        self, dataframe: DataFrame, cls: str, figure: Figure, axes: Axes
    ) -> None:
        class_df = dataframe[dataframe[LEVEL_CLASSIFICATION] == cls]
        color_palette = self._color_provider.get()

        for flow in class_df[LEVEL_FLOW].unique():
            flow_df = class_df[class_df[LEVEL_FLOW] == flow]
            flow_df = flow_df.sort_values(LEVEL_START_TIME)

            axes.plot(
                flow_df[LEVEL_START_TIME],
                flow_df["count"],
                label=flow,
                color=color_palette.get(flow, "black"),
                marker="x",
            )
