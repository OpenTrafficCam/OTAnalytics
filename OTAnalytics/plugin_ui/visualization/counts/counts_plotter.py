import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from os.path import join
from typing import Callable

# from adapter_visualization.color_provider import ColorPaletteProvider
from application.analysis.traffic_counting import (
    Count,
    SimpleTaggerFactory,
    TrafficCounting,
)
from application.analysis.traffic_counting_specification import CountingSpecificationDto
from application.export_formats.export_mode import OVERWRITE
from application.state import TracksMetadata
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import Divider, Size
from PIL import Image as ImageModule
from PIL.Image import Image

DPI = 100


@dataclass(frozen=True)
class CountsImage:
    """
    Represents an image with a counts plot.
    """

    image: Image
    width: int
    height: int
    name: str
    timestamp: datetime

    def save(self, path: str) -> None:
        time = self.timestamp.strftime("%d_%m_%Y__%H_%M_%S")
        self.save(join(path, f"counts_plot_{self.name}_{time}.png"))


class CountsPlotter(ABC):
    "Abstract counts plotter"

    def __init__(self, traffic_counting: TrafficCounting) -> None:
        self._traffic_counting = traffic_counting

    def plot(self, width: int, height: int) -> list[CountsImage]:
        specification = self.get_counting_specification()
        count = self._traffic_counting.count(specification)
        return self.plot_counts(count, width, height)

    @abstractmethod
    def get_counting_specification(self) -> CountingSpecificationDto:
        pass

    @abstractmethod
    def plot_counts(
        self,
        count: Count,
        width: int,
        height: int,
    ) -> list[CountsImage]:
        pass


AXES_CONSUMER = Callable[[Axes], None]


class MultipleCountsPlotters(CountsPlotter):

    def __init__(
        self, traffic_counting: TrafficCounting, plotters: list[CountsPlotter]
    ):
        super().__init__(traffic_counting)
        self._plotters = plotters

    def plot_counts(self, count: Count, width: int, height: int) -> list[CountsImage]:
        raise NotImplementedError(
            "plot_counts should not be called on MultipleCountsPlotters, "
            + "they should be defined per contained plotter!"
        )

    def plot(self, width: int, height: int) -> list[CountsImage]:
        result = []
        for plotter in self._plotters:
            result += plotter.plot(width, height)
        return result


class MatplotlibCountsPlotter(CountsPlotter):

    def __init__(self, traffic_counting: TrafficCounting):
        super().__init__(traffic_counting)
        self._styler = MatplotlibPlotStyler()

    def plot_counts(self, count: Count, width: int, height: int) -> list[CountsImage]:
        result = []
        timestamp = datetime.now()

        for name, plotter in self.create_axes_plotters(count):
            pil = self._styler.apply_plotter(width, height, plotter)
            image = CountsImage(pil, width, height, name, timestamp)
            result.append(image)

        return result

    @abstractmethod
    def create_axes_plotters(self, count: Count) -> list[tuple[str, AXES_CONSUMER]]:
        pass


class MatplotlibPlotStyler:
    """
    A utility class for creating and styling matplotlib Figures/Axes.
    """

    def apply_plotter(
        self,
        width: int,
        height: int,
        plotter: AXES_CONSUMER,
    ) -> Image:
        image_width = width / DPI
        image_height = height / DPI
        figure = self._create_figure(width=image_width, height=image_height)
        axes = self._create_axes(image_width, image_height, figure)
        plotter(axes)
        self._style_axes(width, height, axes)
        return self.convert_to_image(figure)

    def _create_axes(self, width: float, height: float, figure: Figure) -> Axes:
        """
        Create axes to plot on.

        Args:
            width (int): width of the axes
            height (int): height of the axes
            figure (Figure): figure object to add the axis to

        Returns:
            Axes: axes object with the given width and height
        """
        # The first items are for padding and the second items are for the axes.
        # sizes are in inch.
        horizontal = [Size.Fixed(0.0), Size.Fixed(width)]
        vertical = [Size.Fixed(0.0), Size.Fixed(height)]

        divider = Divider(
            fig=figure,
            pos=(0, 0, 1, 1),
            horizontal=horizontal,
            vertical=vertical,
            aspect=False,
        )
        # The width and height of the rectangle are ignored.
        return figure.add_axes(
            divider.get_position(), axes_locator=divider.new_locator(nx=1, ny=1)
        )

    def _style_axes(self, width: int, height: int, axes: Axes) -> None:
        """
        Style axes object to show the image and tracks correctly.

        Args:
            width (int): width of the axes
            height (int): height of the axes
            axes (Axes): axes object to be styled
        """
        axes.set(
            xlabel="",
            ylabel="",
            xticklabels=[],
            yticklabels=[],
        )
        axes.set_ylim(0, height)
        axes.set_xlim(0, width)
        axes.patch.set_alpha(0.0)
        axes.invert_yaxis()

    def _create_figure(self, width: float, height: float) -> Figure:
        """
        Create figure to be plotted on.

        Returns:
            Figure: figure to be plotted on
        """
        figure = Figure(figsize=(width, height), dpi=DPI)
        figure.patch.set_alpha(0.0)
        return figure

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
        image = ImageModule.open(buf).convert("RGBA")

        buf.close()
        return image


class FlowByModeCountPlotter(MatplotlibCountsPlotter):

    def __init__(
        self,
        traffic_counting: TrafficCounting,  # TODO: color_provider: ColorPaletteProvider
        tracks_metadata: TracksMetadata,
    ) -> None:
        super().__init__(traffic_counting.with_tagger_factory(SimpleTaggerFactory()))
        self._metadata = tracks_metadata

    def get_name(self) -> str:
        return f"counts plotter for modes {self._metadata.detection_classifications}"

    def create_axes_plotters(self, count: Count) -> list[tuple[str, AXES_CONSUMER]]:
        print("count values", count.to_dict())
        return []

    def get_counting_specification(self) -> CountingSpecificationDto:
        return CountingSpecificationDto(
            start=datetime.min,
            end=datetime.max,
            count_all_events=True,
            interval_in_minutes=15,
            modes=self._metadata.detection_classifications,  # todo how to get modes
            output_file="none",
            output_format="png",
            export_mode=OVERWRITE,
        )
