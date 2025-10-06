from pathlib import Path

from OTAnalytics.application.analysis.traffic_counting import CountImage
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.plugin_ui.visualization.counts.counts_plotter import CountPlotter


class CountPlotsUpdater:

    def __init__(self, state: TrackViewState, plotter: CountPlotter) -> None:
        self._state = state
        self._plotter = plotter

    def __call__(self) -> None:
        self.update()

    def update(self) -> None:
        width = self._state.view_width.get()
        height = self._state.view_height.get()
        plots = self._plotter.plot(width, height)

        self._state.count_plots.set(plots)


class CountPlotSaver:

    def __init__(self, path: Path):
        self._path = path

    def __call__(self, plots: list[CountImage]) -> None:
        self.save(plots)

    def save(self, plots: list[CountImage]) -> None:
        for plot in plots:
            plot.save(self._path)
