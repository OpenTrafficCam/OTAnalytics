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
