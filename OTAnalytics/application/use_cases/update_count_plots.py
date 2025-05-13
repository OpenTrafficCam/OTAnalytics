from application.state import TrackViewState
from plugin_ui.visualization.counts.counts_plotter import (
    CountsPlotter,
    MultipleCountsPlotters,
)


class CountPlotsUpdater:

    def __init__(self, state: TrackViewState, *plotters: CountsPlotter) -> None:
        self._state = state

        if len(plotters) > 1:
            self._plotter = MultipleCountsPlotters(list(plotters))
        elif len(plotters) == 1:
            self._plotter = plotters[0]
        else:
            raise ValueError("No CountsPlotter given in var arg: plotters")

    def __call__(self) -> None:
        self.update()

    def update(self) -> None:
        width = self._state.view_width.get()
        height = self._state.view_width.get()
        plots = self._plotter.plot(width, height)

        self._state.count_plots.set(plots)
