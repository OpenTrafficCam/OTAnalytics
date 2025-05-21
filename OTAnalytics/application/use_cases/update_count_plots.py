from OTAnalytics.application.analysis.traffic_counting import CountsImage
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.plugin_ui.visualization.counts.counts_plotter import CountsPlotter


class CountPlotsUpdater:

    def __init__(self, state: TrackViewState, plotter: CountsPlotter) -> None:
        self._state = state
        self._plotter = plotter

    def __call__(self) -> None:
        self.update()

    def update(self) -> None:
        width = self._state.view_width.get()
        height = self._state.view_width.get()
        plots = self._plotter.plot(width, height)

        self._state.count_plots.set(plots)


class CountPlotSaver:

    def __init__(self, path: str):
        self._path = path

    def __call__(self, plots: list[CountsImage]) -> None:
        self.save(plots)

    def save(self, plots: list[CountsImage]) -> None:
        for plot in plots:
            plot.save(self._path)
